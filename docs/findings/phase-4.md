# Phase 4 findings: Pipeline orchestration

Date: 2026-06-10

## What was built

- `skill/pnl-labor-analysis/scripts/pipeline.py`. A click CLI (`--input`, optional `--out`
  defaulting to `<input>/_pnl_output`) that wires validate then aggregate and writes the
  three outputs:
  - `analytics.csv` (the compact table, SPEC.md section 6.3),
  - `quarantine.csv` (one row per rejected file with the reason),
  - `run_manifest.json` (audit trail: inputs seen, accepted and quarantined counts, rows
    extracted, analytics rows, a sha256 per input file, and a UTC timestamp).
- Files are discovered non-recursively (`input_dir.glob("*.csv")`) so a nested output
  folder is never reprocessed. `run_pipeline` is importable and returns the manifest for
  testing.

## What was verified

Full run on `data/synthetic`:
- Processed 1200 files: 1199 accepted, 1 quarantined. 1199 analytics rows.
- Manifest reconciles: files_seen 1200 == accepted 1199 + quarantined 1, and
  rows_extracted 10791 == accepted 1199 times 9.
- `quarantine.csv` contains exactly `P088_2025-09.csv` with reason
  "missing required line codes: LAB_ADMIN, LAB_FNB, LAB_ROOMS".
- Each manifest input entry carries a 64-character sha256 and a status.

CI-safe unit test `tests/test_pipeline.py` (3 tests) runs the pipeline over a temp folder
seeded from the fixtures (one valid plus four malformed), asserting the three outputs
exist, the manifest reconciles, the quarantine list names the bad files, and the manifest
is valid JSON. This test does not depend on generated data.

## Pipeline exit behavior

The pipeline exits zero on a successful run even when files are quarantined. A quarantined
input is a normal, reported outcome (ADR-0004), not a pipeline failure.

## Gate result

PASS. Full run on data/synthetic completes, writes all three outputs, and the manifest row
counts reconcile with inputs minus quarantine. Proceeding to Phase 5.
