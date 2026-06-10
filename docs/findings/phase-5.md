# Phase 5 findings: Adversarial acceptance

Date: 2026-06-10

## What was built

- `tests/test_acceptance.py`. The hard gate. It generates a fresh synthetic portfolio and
  answer key, runs the full pipeline end to end via subprocess (exactly as the Skill
  would), then recovers the three seeded anomalies using only generic statistical rules.
  The pipeline never reads the answer key; only this test does, and only to compare the
  recovered results against the planted ground truth (ADR-0005).

## Generic rules used (no hardcoded property knowledge)

- Spike: the property with the highest `labor_pct_z_within_period` in 2025-07 must equal
  the answer key's spike property, and its `labor_pct` must exceed `labor_pct_min` (0.45).
- Drift cluster: the five properties with the highest `labor_pct_slope` must be exactly the
  answer key's drift cluster, each above `slope_min` (0.012).
- Malformed: the answer key's malformed property and period must appear in `quarantine.csv`
  with a reason mentioning LABOR.

## What was verified

- `uv run pytest tests/test_acceptance.py`: 3 passed.
  - Highest z in 2025-07 is P017, labor_pct above 0.45.
  - Top five slopes are exactly P040 to P044, each above 0.012.
  - P088 2025-09 is in the quarantine list with a LABOR reason.
- Full suite `uv run pytest`: 25 passed.

## Gate result

PASS. All three seeded anomalies recovered within tolerance by generic rules. The detector
finds planted truth without being told where it is. Proceeding to Phase 6.
