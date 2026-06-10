# ADR-0004: Validation quarantine over silent drop

Status: Accepted
Date: 2026-06-10

## Context

Real portfolios contain malformed files: missing rows, bad numbers, wrong sections. The
system must be a garbage-in guard. Two failure modes are unacceptable: crashing the whole
run because one file is bad, and silently dropping a bad file so the user never learns their
data had a gap.

## Decision

Validate each file against the pandera schemas. A file that fails is quarantined, not
dropped and not fatal. Each quarantined file produces a row in `quarantine.csv` with the
property, period, and a clear human-readable reason. Accepted rows flow on to aggregation.
The pipeline exits non-zero only on its own failure. A quarantined input is a normal,
reported outcome.

## Consequences

- The user always sees data-quality gaps. The Skill reports quarantined files first, before
  any analysis.
- One bad file cannot take down a 1200-file run.
- The malformed seeded file (`P088` `2025-09`) is the test of this behavior: it must appear
  in `quarantine.csv` with a reason naming the missing LABOR row.

## Alternatives considered

- Fail the run on any bad file. Rejected: one bad file in 1200 should not block the report.
- Silently skip bad files. Rejected: hides data-quality problems from a finance user, which
  is the opposite of the trust this tool is meant to build.
