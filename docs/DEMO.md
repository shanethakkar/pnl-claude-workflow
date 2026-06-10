# Demo walkthrough (Cowork)

A two-minute screen recording that foregrounds the non-coder experience. The goal is to show
that a person who cannot code drops files in a folder, types one sentence, and gets a
trustworthy report back.

## Before recording

- Generate the synthetic portfolio so the folder holds the 1200 files:

  ```
  uv run python tools/generate.py --out data/synthetic --answer-key data/answer_key.json \
    --properties 100 --periods 12 --start 2025-01 --seed 42
  ```

- Install the Skill in Cowork (Customize, then Skills) with code execution and file creation
  enabled. Use the zip in `dist/`.
- Have the synthetic folder open in a file browser so the file count is visible.

## The recording, four beats

1. Show the folder. Open the folder holding the 1200 synthetic P&L files. Pause on the file
   count so the scale is clear: 1200 files, one per property per month.

2. One sentence in Cowork. Open Cowork, choose "Work in a folder", select the synthetic
   folder, and type a single plain English sentence, for example:

   > Which hotels have unusual labor costs this period, and which are trending up over the
   > year?

   Do not type any code. Do not upload anything.

3. Let it run, then open the report. Let the Skill run. When it finishes, open the saved
   `report.md` from the folder. Point out, in order:
   - The data quality section names the one malformed file, P088 for 2025-09, first.
   - P017 is flagged as a single-month labor spike in 2025-07.
   - P040 through P044 are flagged as a sustained upward trend across the year.
   - The numbers come from the saved `analytics.csv` alongside the report.

4. Optional. Show a Cowork scheduled task pointed at the month-end folder, so the review runs
   itself each month.

## Closing line

1200 files reduced to a 1200-row table the model reads, three seeded anomalies and one
malformed file all recovered, run with zero code and zero uploads.

## What to assert during the live run (Phase 8 gate, user-owned)

- Dependencies install in the sandbox on first run.
- `report.md` and `analytics.csv` land in the working folder.
- The quarantine catches P088.
- The summary names the P017 spike and the P040 to P044 drift.
- A clean Cowork install can reproduce the saved report.

If PyPI egress is blocked in the sandbox so the dependency install fails, record that in a
findings note. The fallback path (standard-library sqlite3 for aggregation) is described in
ADR-0002 and listed in docs/LIMITATIONS.md as not yet implemented.
