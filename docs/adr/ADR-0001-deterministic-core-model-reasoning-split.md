# ADR-0001: Deterministic core, model reasoning split

Status: Accepted
Date: 2026-06-10

## Context

The Skill must analyze labor cost across a large portfolio of P&L files, up to 100
properties over 12 periods, which is 1200 files. Feeding raw files to the model does not
scale: it blows the context window, produces non-reproducible numbers, and cannot be
audited. Numbers computed by a language model are not trustworthy for finance.

## Decision

Split the system into a deterministic core and a model reasoning layer. The deterministic
Python core extracts, validates, and aggregates every file into one compact analytics
table. The model reads only that compact table plus the quarantine list. The model never
ingests raw files and never computes a number. It interprets the precomputed figures and
writes narrative.

## Consequences

- Reproducible. The same inputs always yield the same `analytics.csv`, so two runs differ
  only in prose, not in figures.
- Auditable. Every figure traces to a deterministic step with a manifest and content
  hashes.
- Fits the context window. The model reads about 1200 rows, not thousands of raw files.
- The model layer is restricted to the one job it is good at: explaining patterns a human
  would otherwise eyeball. This is stated explicitly in `SKILL.md`.

## Alternatives considered

- Feed raw CSVs to the model directly. Rejected: does not scale, not reproducible, not
  auditable.
- Have the model write the aggregation code per run. Rejected: non-deterministic and
  unauditable across runs.
