# pnl-skill

A Claude Skill that lets a non-technical user analyze labor and payroll cost across a large portfolio of hotel P&L statements. Drop a folder of CSVs, type one sentence, and get a consistent written report.

**Core design principle: reduce first, reason second.** Deterministic Python owns every number. The model reads only a compact analytics table and writes narrative. This keeps the analysis reproducible at portfolio scale and prevents the model from inventing or recomputing figures.

## What it does

Given a folder of property P&L CSVs (one file per property per period), the pipeline:

1. **Extracts** each file into a tidy long format: `property_id, period, section, line_code, line_label, amount`
2. **Validates** structure (required line codes, no unknown codes, non-negative amounts) and quarantines malformed files with a human-readable reason instead of silently dropping them
3. **Aggregates** across the portfolio in DuckDB, computing labor percentage, period-over-period delta, OLS slope across the year, and within-period z-score
4. **Reasons** over the compact analytics table only: the model never opens a raw CSV
5. **Outputs** a written report following a fixed template into the user's working folder

A single prompt from a non-technical user triggers the full pipeline and delivers the report.

## Key engineering decisions

**Scale guardrail** ([ADR-0002](docs/adr/ADR-0002-duckdb-for-aggregation.md)): The pipeline never loads the full portfolio into a pandas DataFrame. Extraction streams one file at a time; aggregation runs in DuckDB with SQL window functions (LAG, regr_slope, stddev_pop). A 1200-file, 100-property portfolio fits in a single DuckDB query that returns one row per property per period.

**Quarantine over silent drop** ([ADR-0004](docs/adr/ADR-0004-validation-quarantine-over-silent-drop.md)): A malformed file gets a row in `quarantine.csv` with a specific, actionable reason ("missing required line codes: LAB_ADMIN, LAB_FNB, LAB_ROOMS"). The pipeline exits cleanly; only the malformed file is excluded.

**Deterministic core, model reasoning only** ([ADR-0001](docs/adr/ADR-0001-deterministic-core-model-reasoning-split.md)): Every figure in the report traces directly to a column in `analytics.csv`. The model is instructed (in SKILL.md) that it must not recompute or invent any number. This is what makes the output auditable.

**Adversarial acceptance gate** ([ADR-0005](docs/adr/ADR-0005-seeded-answer-key-generic-detector.md)): The synthetic data generator seeds three anomaly types (a single-period spike, a five-property drift cluster, a malformed file) and records the exact values in `data/answer_key.json`. The acceptance test uses only generic statistical rules (highest z-score, top-five OLS slopes, quarantine scan) and never reads the answer key. This ensures the detector is genuinely independent of the generator.

**Audit trail**: Every pipeline run writes `run_manifest.json` with a SHA-256 hash per input file, the count of rows extracted and quarantined, and the full list of inputs seen.

## Verified results

All 25 tests pass, including the adversarial acceptance gate:

| Anomaly | Method | Result |
|---------|--------|--------|
| P017 single-period labor spike (2025-07, labor_pct 0.47) | Highest z-score in that period | Recovered, labor_pct >= 0.45 floor |
| P040-P044 sustained upward drift (slope ~0.015/period) | Top-5 OLS slopes, each >= 0.012 | All five recovered |
| P088 2025-09 malformed (missing LABOR section) | Scan quarantine.csv for property/period | Quarantined, "LAB" in reason |

The Skill was also run end-to-end in Claude Code against the synthetic portfolio (1199 accepted, 1 quarantined) and graded against five assertions from the spec. All five passed. See [evals/results.md](evals/results.md) and the produced report at [evals/sample_report.md](evals/sample_report.md).

## Sample output (excerpt)

From the actual run over 100 properties, 12 periods (2025-01 to 2025-12):

> **Single-period spikes**
> P017, 2025-07: labor_pct jumped 0.154 in a single period to 0.470, against a baseline near 0.30 in its other months. This is the largest single-period move in the portfolio and the highest within-period z-score anywhere this year at 6.03.

> **Summary**
> The single most urgent item is P017 in 2025-07, where labor cost spiked to 47 percent of revenue for one month against a 30 percent baseline, the largest outlier in the portfolio. Separately, five properties, P040 through P044, are on a steady upward labor-cost trend, rising about 1.5 points per month and reaching roughly 42 percent by year end, so they need a structural review rather than a one-month fix. One file, P088 for 2025-09, could not be analyzed because its labor rows were missing and should be re-exported.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
# Install dependencies
uv sync

# Generate the 100-property, 12-period synthetic portfolio (1200 files + answer key)
uv run python tools/generate.py --out data/synthetic --answer-key data/answer_key.json \
  --properties 100 --periods 12 --start 2025-01 --seed 42

# Run the pipeline over the synthetic data
uv run python skill/pnl-labor-analysis/scripts/pipeline.py \
  --input data/synthetic --out data/synthetic/_pnl_output

# Run all tests (unit + adversarial acceptance gate)
uv run pytest
```

`data/synthetic/` is gitignored and regenerated deterministically with `--seed 42`. `data/answer_key.json` is tracked.

## Installing the Skill in Claude Cowork

The shippable Skill is `dist/pnl-labor-analysis-v0.1.0.zip`. To install:

1. Open Claude Desktop, go to Cowork, click Customize, then Skills
2. Upload the zip, enable code execution and file creation
3. Open Cowork, choose "Work in a folder," select a folder of P&L CSVs
4. Type a plain-English prompt: "Here is our month-end folder of property P&Ls. Which hotels have unusual labor costs this period, and which are trending up over the year?"

The full SOP for non-technical users is at [docs/SOP.md](docs/SOP.md).

## Repository layout

```
skill/pnl-labor-analysis/   Shippable Skill (SKILL.md, scripts/, references/)
  scripts/
    pipeline.py             Orchestrator: extract -> validate -> aggregate -> write outputs
    extract.py              Pure functions: parse filename, tidy long format
    validate.py             Structural checks + pandera schema; writes quarantine.csv
    aggregate.py            DuckDB aggregation: labor_pct, delta, slope, z-score
    schema.py               Canonical line dictionary + pandera schemas
  references/
    extraction-schema.md    Column definitions, filename convention, quarantine reasons
    report-template.md      Fixed five-section template the model must follow
  requirements.txt          Runtime deps for sandbox pip install
tools/
  generate.py               Dev-only synthetic data generator, not part of the Skill
  build_skill.py            Reproducible zip builder
tests/                      Unit and adversarial acceptance tests (25 total)
evals/                      Eval prompts, grading criteria, sample report, results
docs/
  SPEC.md                   Full specification
  adr/                      Five numbered architectural decision records
  findings/                 Per-phase findings notes (one per build phase)
  SOP.md                    Four-step SOP for the non-technical user
  DEMO.md                   Two-minute demo walkthrough and shot list
  LIMITATIONS.md            Honest scope: synthetic data, canonical layout, platform
dist/
  pnl-labor-analysis-v0.1.0.zip   The installable Skill
data/
  answer_key.json           Seeded anomaly ground truth (test-only, not read by pipeline)
```

## Documentation

- [docs/SPEC.md](docs/SPEC.md): Full specification and phase-by-phase requirements
- [docs/adr/](docs/adr/): Architectural decision records (ADR-0001 to ADR-0005)
- [docs/findings/](docs/findings/): Per-phase build notes
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md): What this is and is not
- [plan.md](plan.md): Build phase tracker
- [decisions.md](decisions.md): Running decision log
