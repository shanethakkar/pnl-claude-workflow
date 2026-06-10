# Extraction schema: the canonical P&L line dictionary

This is the rubric the pipeline enforces. Every input file is normalized into this fixed
shape exactly once, so output is stable and comparable across properties and over time. The
pipeline validates against this dictionary and quarantines any file that does not conform.
You do not need to read raw files to understand their structure: this document is the
structure.

## Filename convention

One CSV per property per period:

```
{property_id}_{period}.csv          for example P017_2025-07.csv
```

- `property_id`: the letter P followed by three digits, for example P017.
- `period`: an ISO month, YYYY-MM, for example 2025-07.

The property and period are parsed from the filename, not from inside the file.

## Raw CSV columns

Each raw file has exactly these four columns:

```
section,line_code,line_label,amount
```

- `section`: one of REVENUE, LABOR, OTHER_EXPENSE.
- `line_code`: a canonical code from the table below.
- `line_label`: a human-readable label.
- `amount`: a positive number in USD.

A valid file contains exactly the nine rows below, one per line code, no more and no fewer.

## Canonical line dictionary

| section       | line_code      | line_label                  |
|---------------|----------------|-----------------------------|
| REVENUE       | REV_ROOMS      | Rooms Revenue               |
| REVENUE       | REV_FNB        | Food and Beverage Revenue   |
| REVENUE       | REV_OTHER      | Other Revenue               |
| LABOR         | LAB_ROOMS      | Rooms Labor                 |
| LABOR         | LAB_FNB        | Food and Beverage Labor     |
| LABOR         | LAB_ADMIN      | Administrative Labor        |
| OTHER_EXPENSE | EXP_UTILITIES  | Utilities                   |
| OTHER_EXPENSE | EXP_MAINT      | Maintenance                 |
| OTHER_EXPENSE | EXP_OTHER      | Other Expense               |

## Tidy long row (what extraction produces)

Each raw row becomes one tidy row with the property and period attached:

```
property_id, period, section, line_code, line_label, amount
```

## What gets quarantined and why

A file is quarantined, not silently dropped, when any of these hold. The quarantine reason
names the specific defect:

- The filename does not match the convention above.
- A required column is missing.
- A required line code is missing (for example a dropped LABOR row).
- A line code is unknown or duplicated, or sits in the wrong section.
- An amount is non-numeric or not positive.

## Compact analytics table (what the analysis reads)

The pipeline writes `analytics.csv`, one row per property per period:

| column                      | meaning                                                        |
|-----------------------------|----------------------------------------------------------------|
| property_id                 | the property                                                   |
| period                      | the ISO month                                                  |
| total_revenue               | sum of the REVENUE lines                                       |
| total_labor                 | sum of the LABOR lines                                         |
| labor_pct                   | total_labor divided by total_revenue                           |
| labor_pct_delta             | labor_pct minus the prior period for the same property, blank at the first period |
| labor_pct_slope             | OLS slope of labor_pct over all periods for this property, repeated on each row |
| labor_pct_z_within_period   | z-score of this labor_pct against all properties in the same period |

These figures are computed deterministically. Use them as given. Do not recompute them.
