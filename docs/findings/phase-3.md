# Phase 3 findings: Aggregation

Date: 2026-06-10

## What was built

- `skill/pnl-labor-analysis/scripts/aggregate.py`. `aggregate_rows` is a pure function:
  accepted tidy rows in, the compact analytics table out (SPEC.md section 6.3). It inserts
  the tidy rows into an in-memory DuckDB table and computes every derived column in one SQL
  pass with window functions. CSV writing is left to the pipeline.

## How each column is computed (all deterministic SQL)

- `total_revenue`, `total_labor`: section sums per property and period.
- `labor_pct`: `total_labor / total_revenue`.
- `labor_pct_delta`: `labor_pct - LAG(labor_pct)` over the property ordered by a numeric
  period ordinal. Null at a property's first period.
- `labor_pct_slope`: `regr_slope(labor_pct, period_ord)` as a window over each property,
  repeated on every row for that property. `period_ord` is `year*12 + month`, so
  consecutive months are one apart and a missing period leaves a real gap in the slope's x
  axis.
- `labor_pct_z_within_period`: `(labor_pct - AVG) / stddev_pop` windowed over each period.
  Population stddev is used because each period's properties are the full population for
  that period, not a sample.

## Scale guardrail

Tidy rows are inserted into DuckDB and all aggregation happens in the engine. No
portfolio-wide pandas DataFrame is ever built (ADR-0002).

## What was verified (hand-checked fixture)

Two properties over three periods with labor_pct chosen for exact arithmetic:
- P001 labor_pct 0.20, 0.30, 0.40; P002 constant 0.50.
- delta: P001 None, 0.10, 0.10; P002 None, 0.00, 0.00.
- slope: P001 0.10 per period, P002 0.00.
- z within period: -1.0 for P001 and +1.0 for P002 in all three periods.

`uv run pytest tests/test_aggregate.py`: 5 passed. All four derived columns match manual
arithmetic.

## Gate result

PASS. test_aggregate.py passes on the hand-checked fixture with labor_pct, labor_pct_delta,
labor_pct_slope, and labor_pct_z_within_period all verified against manual arithmetic.
Proceeding to Phase 4.
