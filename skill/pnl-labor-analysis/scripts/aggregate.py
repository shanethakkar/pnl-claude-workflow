"""Aggregation in DuckDB (SPEC.md section 6.3, ADR-0002).

Collapses the accepted tidy rows into the compact analytics table the model reads: one row
per property per period, with labor percentage, period-over-period delta, an OLS slope of
labor percentage over time per property, and a within-period cross-property z-score.

All of this is computed deterministically in SQL with window functions, so the heavy math
is auditable and never guessed by the model (ADR-0001). `aggregate_rows` is a pure
function: tidy rows in, analytics rows out, with no side effects. CSV writing lives in
pipeline.py.

The scale guardrail (ADR-0002) is honored: tidy rows are inserted into DuckDB and all
aggregation happens in the engine. We never build a portfolio-wide pandas DataFrame.
"""

from __future__ import annotations

import duckdb

from schema import TIDY_COLUMNS

ANALYTICS_COLUMNS: list[str] = [
    "property_id",
    "period",
    "total_revenue",
    "total_labor",
    "labor_pct",
    "labor_pct_delta",
    "labor_pct_slope",
    "labor_pct_z_within_period",
]

# The SQL is one pass of CTEs:
#   base -> per property/period section sums and a numeric period ordinal
#   pct  -> labor_pct
#   final -> window functions for delta, slope, and within-period z-score
#
# period_ord is year*12 + month so consecutive months are exactly one apart and a missing
# period leaves a real gap in the slope's x axis. stddev_pop is used for the z-score
# because each period's properties are the full population for that period, not a sample.
_AGGREGATE_SQL = """
WITH base AS (
    SELECT
        property_id,
        period,
        CAST(SUBSTR(period, 1, 4) AS INTEGER) * 12
            + CAST(SUBSTR(period, 6, 2) AS INTEGER) AS period_ord,
        SUM(CASE WHEN section = 'REVENUE' THEN amount ELSE 0 END) AS total_revenue,
        SUM(CASE WHEN section = 'LABOR' THEN amount ELSE 0 END) AS total_labor
    FROM tidy
    GROUP BY property_id, period
),
pct AS (
    SELECT
        *,
        total_labor / NULLIF(total_revenue, 0) AS labor_pct
    FROM base
)
SELECT
    property_id,
    period,
    total_revenue,
    total_labor,
    labor_pct,
    labor_pct - LAG(labor_pct) OVER (
        PARTITION BY property_id ORDER BY period_ord
    ) AS labor_pct_delta,
    regr_slope(labor_pct, period_ord) OVER (
        PARTITION BY property_id
    ) AS labor_pct_slope,
    (labor_pct - AVG(labor_pct) OVER (PARTITION BY period))
        / NULLIF(stddev_pop(labor_pct) OVER (PARTITION BY period), 0)
        AS labor_pct_z_within_period
FROM pct
ORDER BY property_id, period
"""


def aggregate_rows(tidy_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate tidy rows into the compact analytics table.

    Pure function: returns a list of analytics row dicts keyed by ANALYTICS_COLUMNS.
    Null-valued cells (for example labor_pct_delta at a property's first period) come back
    as None.
    """
    con = duckdb.connect()
    try:
        con.execute(
            "CREATE TABLE tidy ("
            "property_id VARCHAR, period VARCHAR, section VARCHAR, "
            "line_code VARCHAR, line_label VARCHAR, amount DOUBLE)"
        )
        if tidy_rows:
            con.executemany(
                "INSERT INTO tidy VALUES (?, ?, ?, ?, ?, ?)",
                [tuple(row[col] for col in TIDY_COLUMNS) for row in tidy_rows],
            )
        cursor = con.execute(_AGGREGATE_SQL)
        columns = [desc[0] for desc in cursor.description]
        records = cursor.fetchall()
    finally:
        con.close()

    return [dict(zip(columns, record)) for record in records]
