# ADR-0003: Fixed extraction schema as the rubric

Status: Accepted
Date: 2026-06-10

## Context

P&L statements vary in layout. If the model re-parsed each layout, output would drift month
over month and could not be compared across properties. The system needs one stable shape
that every file is normalized into exactly once.

## Decision

Define a single fixed extraction schema, the tidy long row:
`property_id, period, section, line_code, line_label, amount`. `extract.py` turns one CSV
into rows of this schema, parsing `property_id` and `period` from the filename. The
canonical line dictionary (sections, line codes, labels) is documented in
`references/extraction-schema.md` and enforced by a pandera schema. This fixed schema is the
rubric: the model never re-interprets a P&L layout because normalization happens once,
deterministically.

## Consequences

- Output is stable and comparable across properties and periods.
- Adding a new real-world layout becomes a mapping step into this schema, not a change to
  everything downstream.
- The schema doubles as validation: a file that does not map cleanly is quarantined.

## Alternatives considered

- Let the model infer structure per file. Rejected: non-reproducible, not comparable,
  not auditable.
- A wider schema with one column per line item. Rejected: brittle to layout changes and
  awkward for the windowed aggregation; tidy long is the natural shape for DuckDB.
