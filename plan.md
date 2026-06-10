# Build Plan

Living plan for building the pnl-skill. Updated as work proceeds and as new things come
up. The authoritative requirements are in [docs/SPEC.md](docs/SPEC.md); this file tracks
how we are executing them and where we currently are. Decisions are logged in
[decisions.md](decisions.md).

Last updated: 2026-06-10

## Current status

**Phase 3 complete. Building Phase 4 (pipeline orchestration).**

## Phase tracker

Legend: [ ] not started, [~] in progress, [x] done, [-] out of scope this session.

- [x] **Setup** Tooling and access checks. uv + Python 3.12 verified, all core deps
  install and import, git initialized, remote set, push access confirmed, living docs
  created.
- [x] **Phase 0 Scaffold and decisions.** Directory tree from spec section 4, ADR-0001
  to ADR-0005. Gate PASSED: tree exists, `uv run python -c "import duckdb, pandera, click"`
  succeeds, ADRs present. See `docs/findings/phase-0.md`.
- [x] **Phase 1 Synthetic generator and answer key.** `tools/generate.py`, write
  `data/answer_key.json` from actual seeded values. Gate PASSED: 1200 files + 1 malformed
  file + matching answer key, spike file spot-checked by hand. See
  `docs/findings/phase-1.md`.
- [x] **Phase 2 Extraction, schema, validation.** `schema.py` (raw + tidy pandera
  schemas), `extract.py` (pure functions), `validate.py` (accepted rows + quarantine
  reasons). Gate PASSED: test_extract.py and test_validate.py pass (14 tests), malformed
  fixture quarantines with a clear reason. See `docs/findings/phase-2.md`.
- [x] **Phase 3 Aggregation.** `aggregate.py` via DuckDB producing the compact table.
  Gate PASSED: test_aggregate.py passes (5 tests) with all four derived columns verified
  against manual arithmetic. See `docs/findings/phase-3.md`.
- [ ] **Phase 4 Pipeline orchestration.** `pipeline.py` wiring extract, validate,
  aggregate, writing `analytics.csv`, `quarantine.csv`, `run_manifest.json`. Gate: full
  run on `data/synthetic` completes, manifest reconciles inputs minus quarantine.
- [ ] **Phase 5 Adversarial acceptance.** `test_acceptance.py` recovers the three seeded
  anomalies with generic rules. Gate: all three recovered within tolerance, else stop.
- [ ] **Phase 6 Author SKILL.md.** Frontmatter, body, both reference files, report
  template, runtime `requirements.txt`. Gate: under 500 lines, description per spec 11.1,
  references resolve.
- [ ] **Phase 7 Skill triggering and reasoning eval (dev side).** `evals/evals.json` with
  the three prompts; run the Skill directly in Claude Code against the synthetic folder;
  grade against spec section 12 assertions. Gate: report recovers all three findings,
  uses the fixed template, invoked `pipeline.py` rather than reading raw CSVs.
- [-] **Phase 8 Package, install in Cowork, SOP, demo.** User owns the Cowork install and
  screen recording. Agent deliverables: zip the Skill folder, write the one-page SOP and
  the demo script. The live Cowork run and recording are done by the user.

## Open questions and things that came up

- None blocking right now. New items get added here as they surface, with the resolution
  recorded in [decisions.md](decisions.md) once decided.

## Notes for the next agent

- Start by reading [CLAUDE.md](CLAUDE.md), then this file, then [decisions.md](decisions.md).
- Do not advance past a failed phase gate. Write the `docs/findings/` note before
  committing each phase.
- The synthetic data is gitignored and regenerated deterministically with seed 42.
