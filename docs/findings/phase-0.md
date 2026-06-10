# Phase 0 findings: Scaffold and decisions

Date: 2026-06-10

## What was built

- The full directory tree from spec section 4: `docs/adr/`, `docs/findings/`, `data/`,
  `data/synthetic/`, `tools/`, `tests/fixtures/`, `evals/`, and the self-contained Skill
  folder `skill/pnl-labor-analysis/` with `scripts/`, `references/`, and `assets/`.
- `pyproject.toml` as a non-packaged uv application (created during setup).
- ADR-0001 through ADR-0005 in `docs/adr/`, covering the deterministic/model split, DuckDB
  aggregation, the fixed extraction schema, quarantine over silent drop, and the
  seeded-answer-key with generic-detector approach.
- Agent-facing docs created during setup: `CLAUDE.md`, `plan.md`, `decisions.md`.

## What was verified

- Gate command passes: `uv run python -c "import duckdb, pandera, click"` prints OK.
- All five ADRs present in `docs/adr/`.
- Directory tree matches spec section 4.

## Open issues

- None. The output folder is `_pnl_output` (not `_ledgerlens_output`), per the decision to
  drop the LedgerLens placeholder name. Tracked in `decisions.md`.

## Gate result

PASS. Tree exists, import gate succeeds, ADRs present. Proceeding to Phase 1.
