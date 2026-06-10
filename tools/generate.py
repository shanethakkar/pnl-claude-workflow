"""Synthetic P&L generator (dev-time only, not part of the Skill).

Creates one CSV per property per period following the data contract in SPEC.md
section 6.1, and writes an answer key recording the anomalies it seeds by explicit
construction (SPEC.md sections 6.4 and 7).

The generator is the only component that knows where the anomalies are. The detection
pipeline never reads the answer key; it recovers the anomalies with generic statistical
rules. See ADR-0005.

Anomalies seeded at the default settings (100 properties, 12 periods, seed 42):
- Spike:         P017 in 2025-07 has labor_pct forced to about 0.47 vs a ~0.30 baseline.
- Drift cluster: P040 to P044 have labor_pct rising about 1.5 points per period.
- Malformed:     P088 in 2025-09 is written without its LABOR rows, so validation
                 must quarantine it.

Usage:
    uv run python tools/generate.py --out data/synthetic \\
      --answer-key data/answer_key.json --properties 100 --periods 12 \\
      --start 2025-01 --seed 42
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

import click

# Canonical line dictionary. Must match references/extraction-schema.md and schema.py.
LINE_DICT: dict[str, list[tuple[str, str]]] = {
    "REVENUE": [
        ("REV_ROOMS", "Rooms Revenue"),
        ("REV_FNB", "Food and Beverage Revenue"),
        ("REV_OTHER", "Other Revenue"),
    ],
    "LABOR": [
        ("LAB_ROOMS", "Rooms Labor"),
        ("LAB_FNB", "Food and Beverage Labor"),
        ("LAB_ADMIN", "Administrative Labor"),
    ],
    "OTHER_EXPENSE": [
        ("EXP_UTILITIES", "Utilities"),
        ("EXP_MAINT", "Maintenance"),
        ("EXP_OTHER", "Other Expense"),
    ],
}

# Seeded-anomaly constants. The answer key records conservative minimums derived from
# these, so the test thresholds sit safely below the actual constructed values.
SPIKE_PROPERTY = 17
SPIKE_PERIOD = "2025-07"
SPIKE_LABOR_PCT = 0.47
SPIKE_LABOR_PCT_MIN = 0.45  # recorded in the answer key as the test floor

DRIFT_PROPERTIES = [40, 41, 42, 43, 44]
DRIFT_START_PCT = 0.26
DRIFT_SLOPE = 0.015  # labor_pct rise per period
DRIFT_SLOPE_MIN = 0.012  # recorded in the answer key as the test floor

MALFORMED_PROPERTY = 88
MALFORMED_PERIOD = "2025-09"
MALFORMED_DEFECT = "missing LABOR subtotal row"

BASELINE_LABOR_PCT = 0.30
LABOR_SPLIT = {"LAB_ROOMS": 0.45, "LAB_FNB": 0.35, "LAB_ADMIN": 0.20}
EXPENSE_SPLIT = {"EXP_UTILITIES": 0.40, "EXP_MAINT": 0.30, "EXP_OTHER": 0.30}


def property_id(index: int) -> str:
    """One-based property index to canonical id, for example 17 to P017."""
    return f"P{index:03d}"


def month_range(start: str, n: int) -> list[str]:
    """Return n consecutive ISO months starting at start, for example 2025-01."""
    year, month = (int(part) for part in start.split("-"))
    months: list[str] = []
    for _ in range(n):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def labor_pct_target(index: int, period_idx: int, rng: random.Random) -> float:
    """Construct the target labor percentage for one property and period.

    Normal properties sit near the baseline with small per-property and per-period
    variation. The drift cluster rises linearly. The spike is forced at one period.
    """
    if index == SPIKE_PROPERTY:
        # Normal baseline on every period. The spike at SPIKE_PERIOD is forced by the
        # caller, not here.
        return BASELINE_LABOR_PCT + rng.gauss(0, 0.015)
    if index in DRIFT_PROPERTIES:
        return DRIFT_START_PCT + period_idx * DRIFT_SLOPE + rng.gauss(0, 0.004)
    # Normal property: stable around baseline with mild noise.
    return BASELINE_LABOR_PCT + rng.gauss(0, 0.02) + rng.gauss(0, 0.004)


def build_rows(
    index: int,
    period: str,
    period_idx: int,
    rng: random.Random,
    base_revenue: float,
    phase: float,
) -> list[dict[str, object]]:
    """Build the nine tidy line rows for one property and period."""
    # Mild seasonal swing plus small noise on revenue.
    seasonal = 1.0 + 0.15 * math.sin(2 * math.pi * period_idx / 12 + phase)
    revenue_total = base_revenue * seasonal * rng.gauss(1.0, 0.03)
    revenue_total = max(revenue_total, 50_000.0)

    rev_split = {"REV_ROOMS": 0.60, "REV_FNB": 0.28, "REV_OTHER": 0.12}
    revenue_amounts = {
        code: revenue_total * frac * rng.gauss(1.0, 0.02)
        for code, frac in rev_split.items()
    }
    revenue_sum = sum(revenue_amounts.values())

    # Labor as a fraction of actual revenue, split into the three labor lines so the
    # realized labor_pct matches the constructed target up to cent rounding.
    if index == SPIKE_PROPERTY and period == SPIKE_PERIOD:
        target = SPIKE_LABOR_PCT
    else:
        target = labor_pct_target(index, period_idx, rng)
    target = min(max(target, 0.05), 0.95)
    labor_total = revenue_sum * target
    labor_amounts = {code: labor_total * frac for code, frac in LABOR_SPLIT.items()}

    # Other expense as a separate realistic fraction of revenue.
    expense_total = revenue_sum * min(max(rng.gauss(0.35, 0.03), 0.15), 0.55)
    expense_amounts = {
        code: expense_total * frac for code, frac in EXPENSE_SPLIT.items()
    }

    amounts = {**revenue_amounts, **labor_amounts, **expense_amounts}

    rows: list[dict[str, object]] = []
    for section, lines in LINE_DICT.items():
        for code, label in lines:
            rows.append(
                {
                    "section": section,
                    "line_code": code,
                    "line_label": label,
                    "amount": round(amounts[code], 2),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["section", "line_code", "line_label", "amount"]
        )
        writer.writeheader()
        writer.writerows(rows)


@click.command()
@click.option("--out", required=True, type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--answer-key", required=True, type=click.Path(dir_okay=False, path_type=Path)
)
@click.option("--properties", default=100, show_default=True, type=int)
@click.option("--periods", default=12, show_default=True, type=int)
@click.option("--start", default="2025-01", show_default=True)
@click.option("--seed", default=42, show_default=True, type=int)
def main(
    out: Path,
    answer_key: Path,
    properties: int,
    periods: int,
    start: str,
    seed: int,
) -> None:
    """Generate the synthetic portfolio and the answer key."""
    rng = random.Random(seed)
    out.mkdir(parents=True, exist_ok=True)
    months = month_range(start, periods)

    # Per-property revenue base and seasonal phase, drawn once so each property is
    # internally consistent across its periods.
    base_revenue = {
        idx: rng.uniform(400_000, 2_500_000) for idx in range(1, properties + 1)
    }
    phase = {idx: rng.uniform(0, 2 * math.pi) for idx in range(1, properties + 1)}

    file_count = 0
    malformed_count = 0
    for idx in range(1, properties + 1):
        for period_idx, period in enumerate(months):
            rows = build_rows(
                idx, period, period_idx, rng, base_revenue[idx], phase[idx]
            )
            path = out / f"{property_id(idx)}_{period}.csv"

            # Seed the malformed file by dropping the LABOR rows entirely.
            if idx == MALFORMED_PROPERTY and period == MALFORMED_PERIOD:
                rows = [row for row in rows if row["section"] != "LABOR"]
                malformed_count += 1

            write_csv(path, rows)
            file_count += 1

    # Build the answer key only from properties that actually exist in this run.
    key: dict[str, object] = {"seed": seed}
    if properties >= SPIKE_PROPERTY and SPIKE_PERIOD in months:
        key["spike"] = {
            "property_id": property_id(SPIKE_PROPERTY),
            "period": SPIKE_PERIOD,
            "labor_pct_min": SPIKE_LABOR_PCT_MIN,
        }
    drift_present = [property_id(i) for i in DRIFT_PROPERTIES if i <= properties]
    if len(drift_present) == len(DRIFT_PROPERTIES):
        key["drift_cluster"] = {
            "property_ids": drift_present,
            "slope_min": DRIFT_SLOPE_MIN,
        }
    if properties >= MALFORMED_PROPERTY and MALFORMED_PERIOD in months:
        key["malformed"] = {
            "property_id": property_id(MALFORMED_PROPERTY),
            "period": MALFORMED_PERIOD,
            "defect": MALFORMED_DEFECT,
        }

    answer_key.parent.mkdir(parents=True, exist_ok=True)
    answer_key.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")

    click.echo(
        f"Wrote {file_count} files to {out} "
        f"({malformed_count} malformed). Answer key at {answer_key}."
    )


if __name__ == "__main__":
    main()
