# Phase 7 findings: Skill triggering and reasoning eval (dev side)

Date: 2026-06-10

## What was built

- `evals/evals.json`: the three test prompts from SPEC.md section 12 plus the objective
  assertions.
- `evals/sample_report.md`: the report produced by running the Skill against the synthetic
  folder. A copy was written to the working folder as `data/synthetic/report.md`, as the
  Skill does.
- `evals/results.md`: the grading of the report against the section 12 assertions.

## How the eval was run

In Claude Code, the Skill was used directly per SKILL.md: run `scripts/pipeline.py` on
`data/synthetic`, then read only `analytics.csv` and `quarantine.csv`, then write
`report.md` from the fixed template. The raw CSVs were never opened for analysis. The live
Cowork triggering run is Phase 8 and is owned by the user.

## Findings recovered (from the precomputed columns, not recomputed)

- Spike: P017 in 2025-07, labor_pct 0.470, within-period z 6.03, the largest single-period
  jump and the highest z anywhere in the year.
- Drift cluster: P040–P044 are exactly the five highest slopes (~0.015 per period) and the
  only properties with z above 2.0 in the latest period.
- Quarantine: P088 2025-09 reported first, with the missing-LABOR reason.

## Grading result

All five assertions pass for all three prompts:
1. Names P017 as a 2025-07 spike. PASS.
2. Identifies P040–P044 as an upward trend. PASS.
3. Lists P088 2025-09 as a data-quality issue. PASS.
4. Follows the fixed template sections. PASS.
5. Invoked pipeline.py and did not read raw CSVs. PASS.

No revision to the SKILL.md rubric was needed.

## Gate result

PASS (dev side). The report recovers all three seeded findings, uses the fixed template, and
the analysis was driven by pipeline outputs rather than raw CSVs. The remaining live Cowork
run is Phase 8, owned by the user. Proceeding to the agent portion of Phase 8 (package, SOP,
demo script).
