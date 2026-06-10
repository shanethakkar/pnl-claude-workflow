# Phase 2 findings: Extraction, schema, validation

Date: 2026-06-10

## What was built

In `skill/pnl-labor-analysis/scripts/`:
- `schema.py`: the canonical line dictionary (single source of truth, ADR-0003) and two
  pandera schemas, `RAW_SCHEMA` (four raw columns) and `TIDY_SCHEMA` (six tidy columns).
  Both enforce allowed sections and line codes, string types, and positive amounts.
- `extract.py`: pure functions. `parse_filename` parses property and period from the
  filename, `to_tidy_rows` is the pure transform (raw rows plus identity to tidy rows,
  with float coercion), and `extract_file` is the thin I/O wrapper.
- `validate.py`: `validate_file` returns either tidy rows or a quarantine entry with a
  clear reason. Structural checks (unknown codes, duplicates, missing required codes,
  wrong section, non-numeric or non-positive amounts) run first so the reason names the
  defect. `TIDY_SCHEMA` runs last as the authoritative guard. `validate_paths` streams
  files one at a time (scale guardrail, ADR-0002).

## Fixtures (hand-checked)

- `valid/P001_2025-01.csv`: clean numbers, labor_pct exactly 0.30.
- `malformed/P088_2025-09.csv`: the three LABOR rows dropped (mirrors the seeded defect).
- `malformed/P003_2025-01.csv`: a negative LABOR amount.
- `malformed/P004_2025-01.csv`: unknown code `LAB_MYSTERY` plus missing `LAB_ADMIN`.
- `malformed/not-a-pnl.csv`: filename does not match the convention.

## What was verified

- `uv run pytest tests/test_extract.py tests/test_validate.py`: 14 passed.
- The valid fixture extracts to the exact expected rows, including the first row and the
  hand-checked revenue (1,000,000), labor (300,000), and labor_pct (0.30).
- The malformed fixture quarantines with a reason naming all three missing LABOR codes.
- Negative amount, unknown code, missing required code, and bad filename each quarantine
  with the expected reason. `to_tidy_rows` does not mutate its input (purity check).

## Design note

The Skill scripts use flat imports (`from schema import ...`) because the Cowork sandbox
runs them from the scripts directory, which Python adds to sys.path automatically. Tests
run from the repo root, so `tests/conftest.py` adds the scripts directory to sys.path.
Recorded in decisions.md.

## Gate result

PASS. test_extract.py and test_validate.py pass against fixtures, the malformed fixture
quarantines with a clear reason, valid fixtures extract to the exact expected rows.
Proceeding to Phase 3.
