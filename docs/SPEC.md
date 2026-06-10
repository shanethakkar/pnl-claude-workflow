# LedgerLens: Claude Skill Build Spec

Agent-ready build plan for Claude Code. Execute phase by phase. Stop and report if any acceptance gate fails before propagating results forward.

Project name `LedgerLens` is a placeholder and can be renamed in one pass. Skill identifier is `pnl-labor-analysis`.

---

## 1. Purpose

Build a Claude Skill that lets a non-technical hotel accountant analyze labor and payroll cost across a large portfolio of property P&L statements without touching code. The user drops a folder of P&L CSVs, types one plain-English instruction, and receives a consistent report that ranks properties on labor cost within a period and trends each property over time. Deterministic Python does extraction, validation, and aggregation. The model does the interpretive reasoning on a compact table only.

This is a portfolio artifact for the Highgate Enterprise AI Insights role. It must demonstrate first-principles, non-coder-facing design, not a one-off script.

Target surface is Cowork, the Claude Desktop workspace for non-coders. The accountant points Cowork at a local folder of P&L files, types one instruction, and the Skill runs in Cowork's sandbox and writes a saved report back into the folder. Build and test happen in Claude Code. The Skill ships self-contained so Cowork installs and runs it with no code from the user. claude.ai chat with a zipped folder is a fallback only.

## 2. The core architecture

Five stages. The model never ingests raw files. We reduce first, reason second. This is what solves the context-limit problem at portfolio scale.

1. Extraction. Parse each P&L CSV into one fixed tidy schema. Pure functions, deterministic.
2. Validation. Check each file against the schema. Quarantine and report malformed files. Garbage-in guard.
3. Aggregation. Collapse all files into one compact analytics table using DuckDB. Pre-compute labor percentage, period-over-period deltas, and cross-property z-scores so the heavy math is auditable, not model-guessed.
4. Reasoning. The model reads the compact table and quarantine list, flags idiosyncrasies, and explains trends. This is the layer that cannot be hard-coded.
5. Output. A fixed report template produced identically on every run.

## 3. Non-negotiable design principles

These are the best practices this build is graded on. Honor all of them.

Engineering discipline:
- Pure-function I/O boundaries. `extract` and `aggregate` logic take inputs and return outputs with no hidden state and no side effects beyond declared file writes.
- Scale guardrail. Never load the full set of CSVs into a pandas DataFrame at once. Stream per file during extraction, and use DuckDB for the aggregation step.
- Audit trail. Every pipeline run writes a manifest recording inputs seen, rows extracted, files quarantined, and a content hash per input file.
- ADR discipline. Record each binding decision as a numbered ADR in `docs/adr/`.
- Per-phase findings notes. After each phase, write a short findings note in `docs/findings/` recording what was built, what was verified, and any open issues.
- Documented limitations. Maintain `docs/LIMITATIONS.md` as you go.

Evaluation integrity:
- The synthetic data generator seeds anomalies by explicit construction and records them in an answer key. The detection pipeline uses generic statistical rules only and has no knowledge of the answer key. This avoids circularity between generator and detector.
- The answer key is used only by tests, never by the pipeline or the Skill.
- Acceptance gate. If the pipeline fails to recover the seeded anomalies within tolerance, stop and report. Do not advance to packaging.

Skill-authoring best practices:
- Progressive disclosure. Keep `SKILL.md` under 500 lines. Push detail into `references/`. Scripts are executed, not read into context.
- The `description` field is the trigger. Write it to state what the Skill does and when to use it, and make it slightly assertive to avoid undertriggering.
- Imperative instructions in the body. Explain why a step matters rather than stacking bare commands.
- The Skill must be self-contained so it zips and runs standalone. All runtime code lives inside the Skill folder.
- Principle of lack of surprise. No behavior the user would not expect from the description.

Writing style for all docs, reports, and prose this build produces:
- No em-dashes anywhere. Use commas, colons, and periods.
- En-dashes for numeric ranges only.
- Direct human prose. Hard numbers over hedged figures.

## 4. Repository layout

```
ledgerlens/
├── README.md
├── pyproject.toml                       # uv-managed
├── CLAUDE.md                            # seed in section 14
├── docs/
│   ├── adr/                             # numbered decision records
│   ├── findings/                        # one note per phase
│   └── LIMITATIONS.md
├── data/
│   ├── synthetic/                       # generated P&L CSVs land here
│   └── answer_key.json                  # seeded anomalies, test-only
├── tools/
│   └── generate.py                      # dev-time synthetic generator, NOT part of the Skill
├── tests/
│   ├── fixtures/                        # hand-checked tiny inputs
│   ├── test_extract.py
│   ├── test_validate.py
│   ├── test_aggregate.py
│   └── test_acceptance.py               # adversarial: recover seeded anomalies
└── skill/
    └── pnl-labor-analysis/              # the shippable Skill, self-contained
        ├── SKILL.md
        ├── requirements.txt            # runtime deps the Cowork sandbox pip-installs
        ├── scripts/
        │   ├── pipeline.py              # CLI orchestrator the model invokes
        │   ├── extract.py
        │   ├── validate.py
        │   ├── aggregate.py
        │   └── schema.py
        ├── references/
        │   ├── extraction-schema.md
        │   └── report-template.md
        └── assets/                      # reserved
```

The generator lives in `tools/` because the accountant never runs it. It exists to create synthetic data for the demo and the tests. The Skill folder is fully self-contained so it can be zipped and installed in Cowork, which runs its scripts in a sandbox.

## 5. Tech stack and environment

Two environments. Build and test run on the developer machine with Python 3.12 managed by `uv`. The Skill runs inside the Cowork sandbox, which installs the Skill's own `requirements.txt` with pip on first use.

- `click` for all CLIs.
- `pandera` for schema validation.
- `duckdb` for the aggregation step.
- `pyarrow` available for columnar I/O if needed.
- `pytest` for tests, developer side only.
- Standard library `csv` and streaming reads for per-file extraction. Do not pull all files into pandas.

`pyproject.toml` declares the dev dependencies. The Skill folder also carries a minimal `requirements.txt` listing only its runtime deps, duckdb, pandera, click, and pyarrow, so the Cowork sandbox can install them. Provide `uv run` entry points for the generator and the pipeline.

Sandbox dependency check. The first thing to verify in the Cowork dry run is that the sandbox can pip-install from PyPI. If egress is blocked for the session, either enable it or fall back to the standard-library `sqlite3` for the aggregation step, which needs no install and handles 1200 rows without issue. Record whichever path is used in a findings note.

## 6. Data contracts

### 6.1 Raw synthetic P&L CSV

One CSV per property per period. Filename convention:

```
{property_id}_{period}.csv          e.g. P017_2025-07.csv
```

Each CSV is a simple two-section monthly P&L for one property and one period. Columns:

```
section,line_code,line_label,amount
```

Sections present: `REVENUE`, `LABOR`, `OTHER_EXPENSE`. Required line codes:

- `REVENUE`: `REV_ROOMS`, `REV_FNB`, `REV_OTHER`
- `LABOR`: `LAB_ROOMS`, `LAB_FNB`, `LAB_ADMIN`
- `OTHER_EXPENSE`: `EXP_UTILITIES`, `EXP_MAINT`, `EXP_OTHER`

Amounts are positive numbers in USD. A valid file contains exactly these nine rows.

### 6.2 Tidy long row, the extraction schema

`extract.py` turns one CSV into rows of:

```
property_id: str        # from filename
period:      str        # from filename, ISO month YYYY-MM
section:     str        # REVENUE | LABOR | OTHER_EXPENSE
line_code:   str
line_label:  str
amount:      float
```

This fixed schema is the rubric. The model never re-interprets a P&L layout because every file is normalized here once. The canonical line dictionary is documented in `references/extraction-schema.md`.

### 6.3 Compact analytics table, what the model reads

`aggregate.py` produces `analytics.csv`, one row per property per period, capped at 100 properties × 12 periods, so 1200 rows that fit in context comfortably.

```
property_id
period
total_revenue                 # sum of REVENUE
total_labor                   # sum of LABOR
labor_pct                     # total_labor / total_revenue
labor_pct_delta               # labor_pct minus prior period for same property, null at period 1
labor_pct_slope               # OLS slope of labor_pct over all periods for this property, repeated on each row
labor_pct_z_within_period     # z-score of this labor_pct vs all properties in the same period
```

Compute everything deterministically in DuckDB. These columns are the audit-grade math. The model interprets them, it does not recompute them.

### 6.4 Answer key, test-only

`data/answer_key.json` records what the generator seeded:

```json
{
  "seed": 42,
  "spike": {"property_id": "P017", "period": "2025-07", "labor_pct_min": 0.45},
  "drift_cluster": {"property_ids": ["P040","P041","P042","P043","P044"], "slope_min": 0.012},
  "malformed": {"property_id": "P088", "period": "2025-09", "defect": "missing LABOR subtotal row"}
}
```

## 7. Seeded anomalies

The generator plants exactly these, by construction, so the eval has independent ground truth:

- Spike. `P017` in `2025-07` has labor multiplied so `labor_pct` jumps to roughly 0.47 against a baseline near 0.30.
- Drift cluster. `P040` through `P044` have `labor_pct` rising about 1.5 points per period across the 12 periods, a slow upward trend rather than a single spike.
- Malformed file. `P088` in `2025-09` is written with a missing `LABOR` row so validation must quarantine it.

All other properties sit in a realistic band with mild seasonal revenue variation and small random noise. Use the seed so runs are reproducible.

## 8. CLI contracts

Generator:

```
uv run python tools/generate.py \
  --out data/synthetic \
  --answer-key data/answer_key.json \
  --properties 100 \
  --periods 12 \
  --start 2025-01 \
  --seed 42
```

Pipeline, the command the Skill invokes:

```
python skill/pnl-labor-analysis/scripts/pipeline.py \
  --input <working-folder-of-csvs> \
  --out <working-folder>/_ledgerlens_output
```

The default `--out` is a `_ledgerlens_output` subfolder inside the user's working folder, so results land where the user can see them in Cowork, not in a sandbox temp path that disappears. Pipeline outputs there:
- `analytics.csv`, the compact table from 6.3
- `quarantine.csv`, one row per rejected file with the reason
- `run_manifest.json`, inputs seen, row counts, quarantine count, per-file content hash, timestamp

The pipeline must exit non-zero only on its own failure. A quarantined input is a normal, reported outcome, not a pipeline failure. The narrative report is written separately by the model, see section 11.

## 9. Build phases

Each phase ends with an acceptance gate and a findings note in `docs/findings/`. Do not advance past a failed gate.

### Phase 0: Scaffold and decisions
- Initialize repo, `pyproject.toml` via `uv`, directory tree from section 4, `CLAUDE.md` from section 14.
- Write ADR-0001 through ADR-0005 as listed in section 13.
- Gate: tree exists, `uv run python -c "import duckdb, pandera, click"` succeeds, ADRs present.

### Phase 1: Synthetic generator and answer key
- Implement `tools/generate.py` per sections 6.1, 7, 8.
- Write `data/answer_key.json` as the generator runs, derived from the actual seeded values.
- Gate: generates 1200 files for the default run, plus one malformed file, and an answer key that matches the seeded values. Verify file count and one spot-checked spike file by hand.

### Phase 2: Extraction, schema, validation
- Implement `schema.py` with two pandera schemas, raw CSV and tidy long.
- Implement `extract.py` as pure functions, one CSV in, tidy rows out, property and period parsed from filename.
- Implement `validate.py`, returning accepted rows and a quarantine list with reasons.
- Gate: `test_extract.py` and `test_validate.py` pass against `tests/fixtures/`. The malformed fixture quarantines with a clear reason. Valid fixtures extract to the exact expected rows.

### Phase 3: Aggregation
- Implement `aggregate.py` using DuckDB to read accepted rows and emit the section 6.3 table.
- Never materialize all raw CSVs in pandas. Stream extraction, hand DuckDB the tidy rows.
- Gate: `test_aggregate.py` passes on a hand-checked fixture where `labor_pct`, `labor_pct_delta`, `labor_pct_slope`, and `labor_pct_z_within_period` are verified against manual arithmetic.

### Phase 4: Pipeline orchestration
- Implement `pipeline.py` wiring extract, validate, aggregate, and writing `analytics.csv`, `quarantine.csv`, `run_manifest.json`.
- Gate: full run on `data/synthetic` completes, writes all three outputs, manifest row counts reconcile with inputs minus quarantine.

### Phase 5: Adversarial acceptance
- Implement `test_acceptance.py`. Run the pipeline on `data/synthetic`, then assert against `data/answer_key.json` using generic rules, not hardcoded property knowledge:
  - The property with the highest `labor_pct_z_within_period` in `2025-07` is `P017` and its `labor_pct` exceeds the answer-key minimum.
  - The five properties with the highest `labor_pct_slope` are exactly the drift cluster, each above the slope minimum.
  - `P088` `2025-09` appears in `quarantine.csv`.
- Gate: all three recovered within tolerance. If not, stop and report. Do not author the Skill on top of a detector that misses planted truth.

### Phase 6: Author SKILL.md
- Write the Skill per section 11. Frontmatter, body, both reference files, the report template.
- Gate: `SKILL.md` under 500 lines, description follows section 11.1, references resolve.

### Phase 7: Skill triggering and reasoning eval
- Save the three test prompts from section 12 to `evals/evals.json`.
- Run claude-with-the-skill on each prompt against the synthetic folder. In Claude Code use the skill directly.
- Grade against the assertions in section 12.
- Gate: the report recovers all three seeded findings, uses the fixed template, and the model invoked `pipeline.py` rather than reading raw CSVs. If a finding is missed, revise the rubric in `SKILL.md` and rerun.

### Phase 8: Package, install in Cowork, SOP, demo
- Zip the Skill folder. Produce the one-page SOP and the demo script from section 13.
- Install the Skill in Cowork and run the demo prompt against the synthetic folder end to end. Confirm dependencies install in the sandbox, `report.md` and `analytics.csv` land in the working folder, the quarantine catches `P088`, and the summary names the `P017` spike and the `P040`–`P044` drift.
- Gate: a clean Cowork install can run the demo prompt and reproduce the saved report. Record the run.

## 10. Output ownership rule

The deterministic layer owns numbers. The model owns narrative. The model must not recompute `labor_pct` or invent figures not present in `analytics.csv`. State this in `SKILL.md` so the reasoning stays grounded and reproducible.

## 11. SKILL.md specification

### 11.1 Frontmatter

```yaml
---
name: pnl-labor-analysis
description: >
  Analyze labor and payroll cost across a portfolio of hotel or venue P&L
  statements. Use this whenever someone provides a folder of monthly or
  periodic P&L CSV files and wants to compare labor cost across properties,
  find properties with unusual or outlier labor cost, or track how each
  property's labor cost changes over time. Trigger this for month-end
  reviews, payroll cost audits, multi-property cost comparisons, and any
  request to find idiosyncrasies or trends in labor spend across many
  financial statements, even when the word skill is never used.
---
```

### 11.2 Body outline

Use imperative instructions and explain why each step exists. Sections, in order:

1. What this Skill does and when. One short paragraph echoing the description.
2. Inputs. A folder of P&L CSVs following the layout in `references/extraction-schema.md`. If the folder is unclear, ask the user to confirm the path.
3. Setup. On first use, install the Skill's dependencies by running `pip install -r requirements.txt`. Skip if they are already present.
4. Workflow.
   - Run `scripts/pipeline.py` with the working folder as input and `<working-folder>/_ledgerlens_output` as output. Explain that this reduces hundreds of files into one compact table so the analysis is reproducible and fits the context window. Do not open or analyze the raw CSVs directly.
   - Read `analytics.csv` and `quarantine.csv` from the output folder.
5. Analysis rubric.
   - Data quality first. Report quarantined files before any analysis so the user sees gaps in the data.
   - Cross-property outliers. Within each period, flag properties whose `labor_pct_z_within_period` exceeds 2.0. Explain the z-score in plain terms.
   - Within-property trends. Flag properties whose `labor_pct_slope` indicates a sustained rise across periods, and separately flag single-period spikes using `labor_pct_delta`.
   - Grounding. Use only figures present in `analytics.csv`. Do not recompute or estimate.
6. Output. Write the report to `report.md` in the user's working folder using the exact template in `references/report-template.md`, then give a short plain-language summary in chat. Saving the file means the user keeps something they can open and share. The `analytics.csv` is already saved alongside it. An `.xlsx` of the analytics table is an optional extra if the user wants a spreadsheet.

### 11.3 references/extraction-schema.md

The canonical line dictionary from section 6.1 and 6.2, plus a short table of contents if it grows past 300 lines. This is the rubric the pipeline enforces.

### 11.4 references/report-template.md

A fixed template the model must follow verbatim and write to `report.md` in the working folder. Suggested structure:

```
# Portfolio Labor Cost Review: {period range}

## Data quality
{quarantined files and reasons, or "All files passed validation."}

## Properties to review this period
{ranked list of cross-property outliers with labor_pct and z-score}

## Properties trending up over time
{drift cluster with slope, framed as a multi-period rise}

## Single-period spikes
{property and period with the delta}

## Summary
{three to five sentence plain-language readout for an accountant}
```

## 12. Evaluation plan

Unit tests cover the deterministic core, Phases 2 and 3. Adversarial acceptance covers recovery of seeded truth, Phase 5. Skill evaluation covers triggering and reasoning, Phase 7.

Test prompts, save to `evals/evals.json`:

1. "Here is our month-end folder of property P&Ls at data/synthetic. Which hotels have unusual labor costs this period, and which are trending up over the year?"
2. "Run a payroll cost review across the P&L files in data/synthetic. Call out idiosyncrasies across properties and over time."
3. "Analyze the P&Ls in data/synthetic and tell me if any files have data problems before you summarize labor cost."

Assertions, objectively checkable:
- The report names `P017` as a labor spike in `2025-07`.
- The report identifies `P040`–`P044` as an upward labor-cost trend.
- The report lists `P088` `2025-09` as a quarantined or data-quality issue.
- The report follows the fixed template sections.
- The model invoked `pipeline.py` and did not read raw CSVs for analysis.

A finding missed at this gate means the rubric, not the pipeline, needs revision. Edit `SKILL.md` and rerun.

## 13. ADRs, packaging, SOP, demo

### ADRs to author in Phase 0
- ADR-0001 Deterministic core, model reasoning split. The model never sees raw files. Rationale: reproducibility, context limits, auditability.
- ADR-0002 DuckDB for aggregation, never pandas-load all files. Rationale: scale guardrail.
- ADR-0003 Fixed extraction schema as the rubric. Rationale: the model never re-parses layouts, so output is stable month over month.
- ADR-0004 Validation quarantine over silent drop. Rationale: garbage-in guard with visibility.
- ADR-0005 Generator-seeded answer key, generic detector. Rationale: independent ground truth, no circularity.

### Packaging
Zip the self-contained `skill/pnl-labor-analysis/` folder. In Cowork, install it through the Customize then Skills flow, with code execution and file creation enabled. No code from the user. Keep the zip versioned so updates are a clean re-install.

### Deployment
For a single demo, a personal install on a Pro or Max plan is enough. For real rollout on Team or Enterprise, an organization owner provisions the Skill once from Organization settings, and it appears for every member enabled by default, so no one uploads anything. Provisioned Skills are uploaded and updated manually, so the architect owns the canonical version and re-provisions on change. For recurring month-end runs, wrap the Skill in a Cowork scheduled task pointed at the month-end folder. Optionally drop a per-folder instruction in that folder so Cowork reaches for the Skill automatically.

### One-page SOP for the accountant
Plain language, no jargon. Four steps: put this period's P&L files in the month-end folder, open Cowork and choose Work in a folder, select that folder, then type one sentence such as "review labor cost across these P&Ls." Read the saved report in the folder.

### Demo walkthrough, Cowork
A two-minute screen recording that foregrounds the non-coder experience:
1. Show the folder holding the 1200 synthetic files.
2. Open Cowork, choose Work in a folder, select it, and type one English sentence.
3. Let the Skill run, then open the saved `report.md`. It ranks properties on labor cost, trends each over 12 periods, flags the three seeded anomalies, and lists the quarantined file first.
4. Optional, show a scheduled task firing on the folder.
The closing line: 1200 files reduced to a 1200-row table the model reads, three seeded anomalies and one malformed file all recovered, run with zero code and zero uploads.

## 14. CLAUDE.md seed

```markdown
# LedgerLens

A Claude Skill that analyzes labor cost across a portfolio of hotel P&L statements.
Deterministic Python extracts, validates, and aggregates. The model reasons over a
compact table only and never ingests raw files.

## Conventions
- Python 3.12, managed with uv. Click for CLIs. Pandera for validation. DuckDB for aggregation.
- Pure-function I/O boundaries for extract and aggregate. No hidden state.
- Scale guardrail: never load all CSVs into pandas. Stream per file, aggregate in DuckDB.
- Every pipeline run writes run_manifest.json with inputs, counts, and per-file hashes.
- Record binding decisions as numbered ADRs in docs/adr. Write a findings note per phase in docs/findings.
- No em-dashes in any prose. En-dashes for numeric ranges only.

## Numbers vs narrative
The pipeline owns all figures and writes analytics.csv. The model interprets them, writes report.md into the user's working folder, and must not recompute or invent numbers.

## Runtime
The Skill ships a requirements.txt. In the Cowork sandbox, install it with pip on first run. Default pipeline output is a _ledgerlens_output subfolder inside the user's working folder. If PyPI egress is blocked, fall back to stdlib sqlite3 for aggregation.

## Evaluation integrity
The generator seeds anomalies and records an answer key used only by tests. The detector
uses generic statistical rules and never reads the answer key. If acceptance tests fail to
recover seeded anomalies, stop and report before advancing.

## Commands
- Generate data: uv run python tools/generate.py --out data/synthetic --answer-key data/answer_key.json --properties 100 --periods 12 --start 2025-01 --seed 42
- Run pipeline: uv run python skill/pnl-labor-analysis/scripts/pipeline.py --input <folder> --out <folder>
- Tests: uv run pytest
```

## 15. Documented limitations to record in docs/LIMITATIONS.md

- Synthetic data is representative, not real GAAP hotel accounting. Line structure is simplified to a single revenue, labor, and other-expense layout.
- Extraction assumes the canonical CSV layout in section 6.1. Real P&Ls vary in format, so a layout-mapping step would be the first addition for production use.
- Cowork is desktop only, on paid plans, and scheduled runs happen only while the machine is awake with the app open.
- Cowork activity is not captured in audit logs or compliance APIs, so a regulated finance team would weigh that before using it on sensitive data. The synthetic demo data carries no such concern.
- Org-wide rollout relies on Team or Enterprise skill provisioning, where updates are manual, so the canonical Skill must be re-provisioned on change.
