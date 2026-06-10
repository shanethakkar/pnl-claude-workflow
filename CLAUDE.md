# pnl-skill

A Claude Skill that analyzes labor cost across a portfolio of hotel P&L statements.
Deterministic Python extracts, validates, and aggregates. The model reasons over a
compact table only and never ingests raw files.

This file orients any agent working in this repo. Read it first, then read
[plan.md](plan.md) for the current phase and [decisions.md](decisions.md) for why
things are the way they are. The authoritative requirements are in
[docs/SPEC.md](docs/SPEC.md); when this file and the spec disagree, the spec wins and
this file should be corrected.

## The one idea that governs everything

Reduce first, reason second. Five stages: extract, validate, aggregate, reason, output.
The first three are deterministic Python and own every number. The model only reads the
compact `analytics.csv` and the quarantine list, and writes narrative. The model must
never recompute a figure or invent one that is not in `analytics.csv`. This is what makes
the output reproducible and keeps the whole portfolio inside the context window.

## Hard rules (these are graded, do not break them)

- **Pure-function I/O boundaries.** `extract` and `aggregate` logic take inputs and
  return outputs, with no hidden state and no side effects beyond declared file writes.
- **Scale guardrail.** Never load the full set of CSVs into a pandas DataFrame at once.
  Stream per file during extraction. Use DuckDB for aggregation. Per-file pandas use on a
  single 9-row file (for pandera validation) is fine; loading the portfolio is not.
- **Audit trail.** Every pipeline run writes `run_manifest.json` recording inputs seen,
  rows extracted, files quarantined, and a content hash per input file.
- **Quarantine, never silently drop.** A malformed file goes to `quarantine.csv` with a
  reason. The pipeline exits non-zero only on its own failure, never because an input was
  quarantined.
- **Evaluation integrity.** The generator seeds anomalies and records `answer_key.json`.
  The answer key is used only by tests, never by the pipeline or the Skill. The detector
  uses generic statistical rules and has no knowledge of the answer key.
- **Acceptance gate.** If the pipeline cannot recover the seeded anomalies within
  tolerance, stop and report. Do not advance to packaging on top of a broken detector.

## Working agreement for agents

- **Document as you go.** Update [plan.md](plan.md) when the plan changes and append to
  [decisions.md](decisions.md) when a decision is made, in the same change that causes it.
  These two files plus the per-phase notes in `docs/findings/` are how the next agent
  picks up. Do not let them drift from reality.
- **ADRs are formal, decisions.md is the running log.** Binding architectural decisions
  get a numbered ADR in `docs/adr/`. `decisions.md` is the lighter human-readable journal
  that links out to ADRs and records the smaller calls too.
- **One commit per phase** unless a phase genuinely needs more. End each phase with a
  findings note in `docs/findings/` before committing.
- **Phase gates are real.** Each build phase in the spec ends with an acceptance gate. Do
  not advance past a failed gate; stop and report instead.

## Prose style (applies to all docs, reports, and code comments)

- No em-dashes anywhere. Use commas, colons, and periods.
- En-dashes for numeric ranges only (for example 2025-01 to 2025-12, or P040–P044).
- Direct human prose. Hard numbers over hedged figures.

## Numbers vs narrative

The pipeline owns all figures and writes `analytics.csv`. The model interprets them,
writes `report.md` into the user's working folder, and must not recompute or invent
numbers. State this in `SKILL.md` so the reasoning stays grounded.

## Environment and tooling

- Python 3.12, managed with `uv`. The project is non-packaged (`tool.uv.package = false`);
  run things with `uv run`.
- Dev dependencies: `click` (CLIs), `pandera[pandas]` (validation), `duckdb` (aggregation),
  `pyarrow` (columnar I/O), `pytest` (tests, dev side only).
- The Skill folder ships its own `requirements.txt` with only its runtime deps so the
  Cowork sandbox can pip-install them on first use.
- `git` and `uv` are present on this machine. The GitHub CLI (`gh`) is not installed; git
  pushes to `origin` use HTTPS via the system credential manager.
- Sandbox fallback: if PyPI egress is blocked in Cowork, fall back to the standard-library
  `sqlite3` for the aggregation step. Record whichever path is used in a findings note.

## Commands

```bash
# Install / sync dependencies
uv sync

# Generate synthetic data and answer key
uv run python tools/generate.py --out data/synthetic --answer-key data/answer_key.json \
  --properties 100 --periods 12 --start 2025-01 --seed 42

# Run the pipeline
uv run python skill/pnl-labor-analysis/scripts/pipeline.py \
  --input <folder-of-csvs> --out <folder>/_pnl_output

# Tests
uv run pytest
```

## Key paths

- `skill/pnl-labor-analysis/` — the shippable, self-contained Skill (all runtime code here).
- `skill/pnl-labor-analysis/scripts/` — `pipeline.py` orchestrator plus `extract.py`,
  `validate.py`, `aggregate.py`, `schema.py`.
- `tools/generate.py` — dev-only synthetic generator, never part of the Skill.
- `data/synthetic/` — generated CSVs (gitignored, regenerate with seed 42).
- `data/answer_key.json` — seeded anomalies, test-only.
- `docs/adr/`, `docs/findings/`, `docs/LIMITATIONS.md` — decisions, phase notes, limits.
