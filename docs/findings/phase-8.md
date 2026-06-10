# Phase 8 findings: Package, SOP, demo (agent portion)

Date: 2026-06-10

This phase is split. The agent built the package and the documents. The live Cowork install
and the two-minute screen recording are owned by the user, since they cannot be done from
Claude Code.

## What the agent built

- `tools/build_skill.py` and `dist/pnl-labor-analysis-v0.1.0.zip`. The zip is the
  self-contained Skill, 9 files, with `__pycache__` and compiled files excluded. Its
  top-level folder is `pnl-labor-analysis/` so Cowork unpacks it cleanly. The version is in
  the filename so updates are a clean re-install.
- `docs/SOP.md`. The one-page, no-jargon standard operating procedure for the accountant:
  put files in the folder, open Cowork, choose Work in a folder, select it, type one
  sentence, read the saved report.
- `docs/DEMO.md`. The two-minute demo walkthrough script with the four beats and the closing
  line, plus the checklist of what to assert during the live run.
- `docs/LIMITATIONS.md`. The honest scope: synthetic data, canonical-layout assumption, the
  simple statistical method, platform caveats, and the not-yet-implemented sqlite3 egress
  fallback.

## What was verified

- The zip extracts and runs standalone: extracted to a temp folder, ran
  `scripts/pipeline.py` from there against the fixtures, and it produced `analytics.csv`,
  `quarantine.csv`, and `run_manifest.json`. This confirms the Skill is self-contained with
  no dependency on the rest of the repo.

## What remains (user-owned)

- Install the zip in Cowork (Customize, then Skills) with code execution and file creation
  enabled.
- Run the demo prompt against the synthetic folder end to end and confirm: dependencies
  install in the sandbox, `report.md` and `analytics.csv` land in the working folder, the
  quarantine catches P088, and the summary names the P017 spike and the P040 to P044 drift.
- Record the two-minute walkthrough.
- If PyPI egress is blocked in the sandbox, the sqlite3 aggregation fallback (ADR-0002)
  would need to be implemented. See docs/LIMITATIONS.md.

## Gate result

Agent portion COMPLETE. The remaining Cowork install, end-to-end run, and recording are the
user's to perform, with the checklist in docs/DEMO.md.
