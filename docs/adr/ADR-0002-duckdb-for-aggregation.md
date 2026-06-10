# ADR-0002: DuckDB for aggregation, never pandas-load all files

Status: Accepted
Date: 2026-06-10

## Context

Aggregation must collapse up to 1200 files into one compact table, computing sums,
period-over-period deltas, an OLS slope per property, and within-period z-scores. Doing
this by loading every file into a single pandas DataFrame would hold the whole portfolio in
memory at once, which is the exact scale failure this build is graded against.

## Decision

Use DuckDB for the aggregation step. Extraction streams one file at a time into tidy rows.
Those tidy rows are handed to DuckDB, which computes all aggregate columns in SQL,
including window functions for deltas, z-scores, and a regression slope. Never materialize
the full set of raw CSVs in a single pandas DataFrame.

## Consequences

- The heavy math is expressed in auditable SQL, computed once, deterministically.
- Memory stays bounded. DuckDB streams and spills as needed; we never hold all files in
  Python memory.
- Per-file pandas use for pandera validation of a single 9-row frame is still allowed. The
  guardrail is specifically about portfolio-scale loads.

## Fallback

If the Cowork sandbox blocks PyPI egress and DuckDB cannot be installed, fall back to the
standard-library `sqlite3` for aggregation, which needs no install and handles 1200 rows
without issue. Record the path used in a findings note.

## Alternatives considered

- pandas groupby over a concatenated DataFrame. Rejected: violates the scale guardrail.
- Pure Python aggregation. Rejected: the windowed math (slope, z-score, delta) is verbose
  and error prone compared to SQL window functions.
