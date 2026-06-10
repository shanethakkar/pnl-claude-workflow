# pnl-skill

A Claude Skill that lets a non-technical accountant analyze labor and payroll cost across a large portfolio of property P&L statements without touching code. Drop a folder of P&L CSVs, type one plain-English instruction, and get a consistent report that ranks properties on labor cost within a period and trends each property over time.

The design principle: **reduce first, reason second.** Deterministic Python extracts, validates, and aggregates every file into one compact analytics table. The model reads only that table and never ingests raw files, which keeps the analysis reproducible and within the context window at portfolio scale.

## Status

Early build. See [plan.md](plan.md) for the live build plan and current phase, and [decisions.md](decisions.md) for the running decision log. The full specification lives in [docs/SPEC.md](docs/SPEC.md).

## Quick start (developer machine)

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 (uv installs it on first run).

```bash
# Install dependencies
uv sync

# Generate the synthetic 100-property, 12-period portfolio (1200 files + answer key)
uv run python tools/generate.py --out data/synthetic --answer-key data/answer_key.json \
  --properties 100 --periods 12 --start 2025-01 --seed 42

# Run the pipeline over a folder of CSVs
uv run python skill/pnl-labor-analysis/scripts/pipeline.py \
  --input data/synthetic --out data/synthetic/_pnl_output

# Run the tests
uv run pytest
```

## Repository layout

See [docs/SPEC.md](docs/SPEC.md) section 4 for the full tree. Key locations:

- `skill/pnl-labor-analysis/` — the shippable, self-contained Claude Skill.
- `tools/generate.py` — dev-time synthetic data generator, not part of the Skill.
- `tests/` — unit and adversarial acceptance tests.
- `docs/` — spec, ADRs, per-phase findings, and limitations.
