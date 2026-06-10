# Eval results: Phase 7 skill triggering and reasoning

Date: 2026-06-10
Environment: Claude Code (dev side). The Skill was used directly against the synthetic
folder, following SKILL.md: run `scripts/pipeline.py`, then read only `analytics.csv` and
`quarantine.csv`, then write `report.md` from the fixed template. The live Cowork
triggering run is Phase 8 and is owned by the user.

The produced report is saved as `evals/sample_report.md` (a copy was also written to the
working folder `data/synthetic/report.md` as the Skill does).

## Prompts

All three prompts in `evals.json` drive the same deterministic pipeline run and the same
report. They differ only in framing (month-end review, payroll cost review, data-problems
first), and the report answers all three:

1. month-end-review: unusual labor this period and year-long trends. Answered by
   "Properties to review this period" (2025-12 outliers) and "Properties trending up".
2. payroll-cost-review: idiosyncrasies across properties and over time. Answered by the
   cross-property outliers, the trend cluster, and the single-period spike.
3. data-problems-first: data problems before the labor summary. Answered by "Data quality"
   appearing first, listing the quarantined file before any analysis.

## Grading against the section 12 assertions

| # | Assertion | Result | Evidence in report |
|---|-----------|--------|--------------------|
| 1 | Names P017 as a labor spike in 2025-07 | PASS | "Single-period spikes": P017 2025-07 jumped 0.154 to labor_pct 0.470, z 6.03; also led in Summary. |
| 2 | Identifies P040 to P044 as an upward trend | PASS | "Properties trending up over time" lists exactly P040–P044 with slope ~0.015 per period. |
| 3 | Lists P088 2025-09 as a quarantine or data-quality issue | PASS | "Data quality" lists P088 2025-09 with the missing-LABOR reason, before any analysis. |
| 4 | Follows the fixed template sections | PASS | Sections match report-template.md in order: Data quality, Properties to review this period, Properties trending up over time, Single-period spikes, Summary. |
| 5 | Invoked pipeline.py and did not read raw CSVs | PASS | The analysis used pipeline outputs (analytics.csv, quarantine.csv) only. The raw CSVs were never opened for analysis. |

## Grounding check

Every figure in the report traces to a column in `analytics.csv` or a row in
`quarantine.csv`. No figure was recomputed or invented (ADR-0001, SPEC.md section 10).

## Outcome

All five assertions pass for all three prompts. No revision to the SKILL.md rubric was
needed.
