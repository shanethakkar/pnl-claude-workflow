# Portfolio Labor Cost Review: 2025-01 to 2025-12

## Data quality

One file was quarantined and excluded from the analysis:

- P088, 2025-09: missing required line codes: LAB_ADMIN, LAB_FNB, LAB_ROOMS. The LABOR
  section is absent, so labor cost cannot be computed for this property and period.

All other 1199 property-period files passed validation.

## Properties to review this period

These are the properties whose labor cost stands out from the rest of the portfolio in the
latest period, 2025-12. The z-score says how far a property sits from its peers that period,
measured in standard deviations, so a z above 2 means clearly higher labor cost than the
portfolio that month. All five flagged properties are well above that line.

- P041: labor_pct 0.430, z 3.44
- P042: labor_pct 0.427, z 3.37
- P040: labor_pct 0.426, z 3.33
- P043: labor_pct 0.424, z 3.28
- P044: labor_pct 0.420, z 3.16

No other property exceeded a z-score of 2.0 in 2025-12.

## Properties trending up over time

Five properties show a sustained upward drift in labor cost across the year rather than a
single bad month. Each has a labor_pct slope near 0.015 per period, which is a rise of about
1.5 points of labor percentage every month, taking them from roughly 0.26 at the start of
the year to roughly 0.42 by 2025-12.

- P040: slope 0.0153 per period
- P042: slope 0.0153 per period
- P043: slope 0.0150 per period
- P044: slope 0.0149 per period
- P041: slope 0.0147 per period

No other property showed a comparable sustained rise. The next highest slope in the
portfolio was 0.0049, roughly a third of the cluster's rate.

## Single-period spikes

One property shows a sharp one-period jump that is not part of a sustained trend:

- P017, 2025-07: labor_pct jumped 0.154 in a single period to 0.470, against a baseline near
  0.30 in its other months. This is the largest single-period move in the portfolio and the
  highest within-period z-score anywhere this year at 6.03.

A few properties had smaller one-period jumps near 0.09 to 0.10 (for example P078 in 2025-08
and P021 in 2025-10), but these are an order below the P017 spike and sit within normal
month-to-month noise.

## Summary

The single most urgent item is P017 in 2025-07, where labor cost spiked to 47 percent of
revenue for one month against a 30 percent baseline, the largest outlier in the portfolio.
Separately, five properties, P040 through P044, are on a steady upward labor-cost trend,
rising about 1.5 points per month and reaching roughly 42 percent by year end, so they need
a structural review rather than a one-month fix. One file, P088 for 2025-09, could not be
analyzed because its labor rows were missing and should be re-exported. Everything else in
the portfolio sat in a normal band around 30 percent with mild seasonal variation.
