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

# Portfolio labor cost analysis

## 1. What this Skill does and when

This Skill analyzes labor and payroll cost across a folder of property P&L statements. Use
it whenever someone points you at a folder of monthly or periodic P&L CSV files and wants to
compare labor cost across properties, find properties with unusual labor cost, or track how
each property's labor cost moves over time. It is built for month-end reviews, payroll cost
audits, and multi-property cost comparisons.

The Skill works by reducing first and reasoning second. Deterministic Python extracts,
validates, and aggregates every file into one compact table. You then reason over that
compact table. This is what lets the analysis cover hundreds of files reproducibly and
within the context window.

## 2. Numbers versus narrative (read this first)

The pipeline owns every number. You own the narrative. The pipeline writes `analytics.csv`
with all the figures already computed: labor percentage, period-over-period change, trend
slope, and a cross-property z-score. Your job is to interpret those figures and explain
them, not to recompute them. Do not recalculate labor percentages, do not estimate, and do
not state any figure that is not present in `analytics.csv`. This is what keeps the output
grounded and reproducible.

## 3. Inputs

A folder of P&L CSV files following the layout in `references/extraction-schema.md`. Each
file is one property for one period, named like `P017_2025-07.csv`. If the folder path is
unclear or you cannot see the files, ask the user to confirm the path before continuing.

## 4. Setup

On first use, install the Skill's dependencies by running this from the Skill directory:

```
pip install -r requirements.txt
```

Skip this if the dependencies are already present. If the sandbox blocks internet access and
the install fails, tell the user, since the pipeline needs these packages to run.

## 5. Workflow

Run the pipeline, then read its outputs. Do not open or analyze the raw CSV files yourself.

1. Run the pipeline with the user's folder as input:

   ```
   python scripts/pipeline.py --input <working-folder> --out <working-folder>/_pnl_output
   ```

   This reduces hundreds of files into one compact table so the analysis is reproducible and
   fits the context window. It writes three files into the output folder:
   - `analytics.csv`: one row per property per period, with all figures precomputed.
   - `quarantine.csv`: one row per rejected file, with the reason.
   - `run_manifest.json`: the audit trail of what was processed.

2. Read `analytics.csv` and `quarantine.csv` from the output folder. These two files are
   your entire evidence base. The column meanings are in `references/extraction-schema.md`.

## 6. Analysis rubric

Work through these in order.

1. Data quality first. Look at `quarantine.csv`. Report every quarantined file, with its
   property, period, and reason, before any analysis, so the user sees the gaps in the data
   up front. A quarantined file is a normal outcome, not an error.

2. Cross-property outliers. Within each period, flag properties whose
   `labor_pct_z_within_period` exceeds 2.0. The z-score says how far a property's labor cost
   sits from its peers in the same period, measured in standard deviations, so a z above 2
   means clearly higher labor cost than the rest of the portfolio that period. Explain it in
   plain terms for the reader.

3. Within-property trends. Flag properties whose `labor_pct_slope` shows a sustained rise
   across periods. The slope is the per-period change in labor percentage, so a positive
   slope repeated across the year is a steady upward drift, not a one-off.

4. Single-period spikes. Separately, flag large one-period jumps using `labor_pct_delta`.
   Distinguish a one-period spike from a sustained trend, since they call for different
   responses.

5. Grounding. Use only figures present in `analytics.csv`. Do not recompute or estimate.

## 7. Output

Write the report to `report.md` in the user's working folder, following the template in
`references/report-template.md` exactly. Saving the file means the user keeps something they
can open and share, and `analytics.csv` is already saved alongside it. After writing the
file, give a short plain-language summary in chat that names the properties and periods that
need attention.

If the user asks for a spreadsheet, an `.xlsx` export of the analytics table is an optional
extra. The required deliverable is `report.md` plus the saved `analytics.csv`.
