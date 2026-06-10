# Phase 6 findings: Author SKILL.md

Date: 2026-06-10

## What was built

- `skill/pnl-labor-analysis/SKILL.md`. Frontmatter per SPEC.md section 11.1 (the assertive
  description that triggers on month-end reviews, payroll audits, and multi-property
  comparisons even when the word skill is not used). Body in the section 11.2 order: what
  and when, numbers versus narrative, inputs, setup, workflow, analysis rubric, output. It
  states the grounding rule up front: the pipeline owns numbers, the model owns narrative,
  and the model must not recompute or invent figures (section 10, ADR-0001).
- `references/extraction-schema.md`. The canonical line dictionary (the rubric), the
  filename convention, what gets quarantined and why, and the analytics column meanings.
- `references/report-template.md`. The fixed report structure to follow verbatim, with
  guidance per section and the prose rules.
- `requirements.txt`. Runtime deps the Cowork sandbox installs: click, pandera[pandas],
  duckdb, pyarrow.

## What was verified

- SKILL.md is 107 lines, well under the 500-line limit (progressive disclosure: detail is
  pushed into references/).
- Both reference files mentioned in SKILL.md resolve.
- The Skill folder is self-contained: every script imports only its siblings in scripts/
  and the runtime deps. Nothing imports from tools/ or elsewhere in the repo.

## Notes

- SKILL.md instructs the model to run `scripts/pipeline.py` and read only `analytics.csv`
  and `quarantine.csv`, never the raw CSVs. This is the behavior Phase 7 grades.
- `scripts/__pycache__/` is gitignored and will be excluded from the Phase 8 zip.

## Gate result

PASS. SKILL.md is under 500 lines, the description follows section 11.1, and the references
resolve. Proceeding to Phase 7.
