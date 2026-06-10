# Phase 1 findings: Synthetic generator and answer key

Date: 2026-06-10

## What was built

- `tools/generate.py`, a click CLI that writes one CSV per property per period following
  the data contract in SPEC.md section 6.1, and writes `data/answer_key.json` from the
  actual seeded constants.
- The generator is the only component that knows the anomaly locations. It records
  conservative test floors in the answer key (`labor_pct_min` 0.45 below the constructed
  0.47, `slope_min` 0.012 below the constructed 0.015). The detector never reads this file
  (ADR-0005).

## How the anomalies are constructed

- Spike: `P017` `2025-07` has labor_pct forced to 0.47. Every other P017 period sits at the
  ~0.30 baseline, so the spike is a single-period event, not a trend.
- Drift cluster: `P040` to `P044` start near 0.26 and rise 0.015 per period.
- Malformed: `P088` `2025-09` is written with the three LABOR rows dropped, so it has six
  rows and no LABOR section.
- All other properties sit near a 0.30 baseline with mild seasonal revenue variation and
  small noise. Per-property revenue base and seasonal phase are drawn once so each property
  is internally consistent across periods.

## What was verified by hand

- File count: 1200 files written, 1 reported malformed.
- Answer key matches the seeded values and lists P017, P040–P044, and P088.
- Spike file `P017_2025-07.csv`: revenue 704,688.78, labor 331,203.73, labor_pct 0.470,
  above the 0.45 floor.
- Malformed file `P088_2025-09.csv`: six rows, no LABOR section.
- Drift `P040` trend: 0.259 rising to 0.426 over the 12 periods, slope about 0.015.
- Normal `P001` trend: fluctuates flat around 0.30 with no upward drift.

## Reproducibility

- Deterministic given `--seed`. Default run is seed 42. The synthetic folder is gitignored
  and regenerated with the command in README.md and CLAUDE.md.

## Gate result

PASS. 1200 files plus one malformed file, answer key matches seeded values, file count and
the spike file spot-checked by hand. Proceeding to Phase 2.
