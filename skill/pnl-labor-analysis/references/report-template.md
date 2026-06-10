# Report template

Follow this template verbatim when writing `report.md` into the user's working folder. The
same structure every run is what makes month-over-month reports comparable. Fill each
section from `analytics.csv` and `quarantine.csv` only. Do not add or drop sections. Do not
recompute or invent figures. No em-dashes anywhere; use commas, colons, and periods.

Replace the {braced} placeholders with real content and remove the braces.

---

# Portfolio Labor Cost Review: {period range, for example 2025-01 to 2025-12}

## Data quality

{If any files were quarantined, list each one with its property, period, and reason, one per
line, so the reader sees the gaps in the data before any analysis. If none were
quarantined, write exactly: All files passed validation.}

## Properties to review this period

{The cross-property outliers for the latest period. List each property whose
labor_pct_z_within_period exceeds 2.0, ranked highest z first, with its labor_pct and its
z-score. Explain the z-score in one plain sentence, for example: a z-score of 3 means this
property's labor cost is three standard deviations above its peers this period. If none
exceed 2.0, say so.}

## Properties trending up over time

{The properties with a sustained upward trend, identified by a high labor_pct_slope. List
each with its slope, framed as a multi-period rise rather than a single spike, for example:
labor cost rising about 1.5 points per period across the year. If none show a sustained
rise, say so.}

## Single-period spikes

{Properties with a large one-period jump, identified by labor_pct_delta. Name the property
and period and give the delta. Distinguish these from sustained trends. If none, say so.}

## Summary

{Three to five sentences in plain language for an accountant. Lead with the single most
important finding. Name the properties and periods that need attention and why. Keep it
direct and use the hard numbers from analytics.csv.}
