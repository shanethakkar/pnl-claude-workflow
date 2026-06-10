# Standard operating procedure: monthly labor cost review

For the accountant. No code, no jargon. Four steps.

## What you need

- The Claude desktop app with Cowork, on a paid plan.
- The pnl-labor-analysis Skill installed once (your administrator or the setup guide handles
  this).
- This period's P&L files, one CSV per property, named like `P017_2025-07.csv`.

## The four steps

1. Put this period's P&L files in your month-end folder.

2. Open Cowork and choose "Work in a folder".

3. Select your month-end folder.

4. Type one sentence, for example:

   > Review labor cost across these P&Ls.

That is it. Claude runs the review and writes the results into the same folder.

## What you get back

In your folder you will find:

- `report.md`: the written review. It flags properties with unusual labor cost this period,
  properties trending up over the year, any single-month spikes, and any files that had data
  problems. Open it, read it, share it.
- A `_pnl_output` folder containing `analytics.csv`, a spreadsheet-friendly table of the
  numbers behind the report.

## If something looks off

- If the report says a file was quarantined, that file had a data problem (for example a
  missing labor section). Re-export that property's file and run the review again.
- If Claude cannot find your files, check that they are CSVs named like
  `P017_2025-07.csv` and that you selected the right folder.
