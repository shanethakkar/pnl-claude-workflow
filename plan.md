# Build Plan

Living plan for building the pnl-skill. Updated as work proceeds and as new things come
up. The authoritative requirements are in [docs/SPEC.md](docs/SPEC.md); this file tracks
how we are executing them and where we currently are. Decisions are logged in
[decisions.md](decisions.md).

Last updated: 2026-06-10

## Current status

**All agent-buildable phases complete (0 through 7, plus the Phase 8 agent portion).**

What remains is user-owned and cannot be done from Claude Code: install the zip in Cowork,
run the demo prompt end to end, and record the two-minute walkthrough. The checklist is in
`docs/DEMO.md`. Deliverable to send interviewers: the repo plus
`dist/pnl-labor-analysis-v0.1.0.zip`.

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
- [x] **Phase 4 Pipeline orchestration.** `pipeline.py` wiring extract, validate,
  aggregate, writing `analytics.csv`, `quarantine.csv`, `run_manifest.json`. Gate PASSED:
  full run on `data/synthetic` (1199 accepted, 1 quarantined), manifest reconciles, plus
  3 CI-safe pipeline tests. See `docs/findings/phase-4.md`.
- [x] **Phase 5 Adversarial acceptance.** `test_acceptance.py` recovers the three seeded
  anomalies with generic rules. Gate PASSED: all three recovered within tolerance (full
  suite 25 tests green). See `docs/findings/phase-5.md`.
- [x] **Phase 6 Author SKILL.md.** Frontmatter, body, both reference files, report
  template, runtime `requirements.txt`. Gate PASSED: SKILL.md is 107 lines, description per
  spec 11.1, references resolve, Skill is self-contained. See `docs/findings/phase-6.md`.
- [x] **Phase 7 Skill triggering and reasoning eval (dev side).** `evals/evals.json` with
  the three prompts; ran the Skill directly in Claude Code against the synthetic folder;
  graded against spec section 12 assertions. Gate PASSED (dev side): all five assertions
  pass, report at `evals/sample_report.md`. See `docs/findings/phase-7.md`.
- [~] **Phase 8 Package, install in Cowork, SOP, demo.** Agent portion COMPLETE:
  `tools/build_skill.py` + `dist/pnl-labor-analysis-v0.1.0.zip` (verified runs standalone),
  `docs/SOP.md`, `docs/DEMO.md`, `docs/LIMITATIONS.md`. See `docs/findings/phase-8.md`.
  Remaining (user-owned): Cowork install, end-to-end demo run, screen recording.

## Open questions and things that came up

- sqlite3 egress fallback (ADR-0002) is documented but not implemented in code. It only
  matters if the Cowork sandbox blocks PyPI so the dependency install fails. If the
  user's live run hits that, implement the fallback then. Tracked in docs/LIMITATIONS.md.
- New items get added here as they surface, with the resolution recorded in
  [decisions.md](decisions.md) once decided.

## Notes for the next agent

- Start by reading [CLAUDE.md](CLAUDE.md), then this file, then [decisions.md](decisions.md).
- Do not advance past a failed phase gate. Write the `docs/findings/` note before
  committing each phase.
- The synthetic data is gitignored and regenerated deterministically with seed 42.
