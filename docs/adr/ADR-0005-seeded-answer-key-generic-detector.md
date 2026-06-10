# ADR-0005: Generator-seeded answer key, generic detector

Status: Accepted
Date: 2026-06-10

## Context

We need to prove the pipeline actually finds the anomalies it claims to find. If the same
knowledge that plants an anomaly is also used to detect it, the evaluation is circular and
proves nothing.

## Decision

Separate ground truth from detection. The synthetic generator plants anomalies by explicit
construction (a labor spike, a drift cluster, a malformed file) and records exactly what it
planted in `data/answer_key.json`. The detection pipeline uses only generic statistical
rules: within-period z-scores, an OLS slope per property, period-over-period deltas, and
schema validation. The pipeline and the Skill never read the answer key. The answer key is
used only by tests.

## Consequences

- The acceptance test (Phase 5) is a genuine, independent check: generic rules must recover
  the planted truth without being told what it is.
- If the detector misses a planted anomaly, that is a real signal that the rules or the
  rubric need work, not an artifact of circular knowledge.
- Acceptance gate: if the pipeline cannot recover the seeded anomalies within tolerance,
  stop and report. Do not advance to packaging.

## Alternatives considered

- Hardcode the known property IDs into the detector or test assertions. Rejected: circular,
  proves nothing about generalization.
- No synthetic ground truth, eyeball the output. Rejected: not objectively checkable and
  not reproducible.
