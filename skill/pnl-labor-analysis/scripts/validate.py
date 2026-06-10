"""Validation and quarantine (SPEC.md section 6, ADR-0004).

Each file is checked against the canonical schema. A file that passes returns its tidy
rows. A file that fails is quarantined with a clear, human-readable reason rather than
crashing the run or being silently dropped. Structural checks (exactly the nine required
lines, no duplicates, no unknown codes, correct section) run first so the reason names the
specific defect. The pandera TIDY_SCHEMA runs last as the authoritative type guard.

Validation is the garbage-in guard. Reporting quarantined files is a normal outcome, not a
pipeline failure.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from extract import parse_filename, read_raw_rows, to_tidy_rows
from schema import (
    CODE_TO_SECTION,
    LINE_CODES,
    RAW_COLUMNS,
    REQUIRED_CODES,
    TIDY_COLUMNS,
    TIDY_SCHEMA,
)

QUARANTINE_COLUMNS: list[str] = ["filename", "property_id", "period", "reason"]


def _quarantine(
    filename: str, property_id: str, period: str, reason: str
) -> dict[str, str]:
    return {
        "filename": filename,
        "property_id": property_id,
        "period": period,
        "reason": reason,
    }


def _schema_reason(exc: Exception) -> str:
    """Render a pandera schema error as a concise quarantine reason."""
    if isinstance(exc, pa.errors.SchemaErrors):
        cases = exc.failure_cases
        parts: list[str] = []
        for _, row in cases.iterrows():
            parts.append(
                f"{row.get('column')} failed {row.get('check')} "
                f"(value {row.get('failure_case')!r})"
            )
        unique = list(dict.fromkeys(parts))
        return "schema validation failed: " + "; ".join(unique)
    return f"schema validation failed: {exc}"


def validate_file(
    path: str | Path,
) -> tuple[list[dict[str, object]] | None, dict[str, str] | None]:
    """Validate one file.

    Returns (tidy_rows, None) if the file is accepted, or (None, quarantine_entry) if it
    is rejected. Never raises on bad input data; raises only on a programming error.
    """
    name = Path(path).name

    try:
        property_id, period = parse_filename(name)
    except ValueError as exc:
        return None, _quarantine(name, "UNKNOWN", "UNKNOWN", str(exc))

    try:
        header, raw_rows = read_raw_rows(path)
    except (OSError, csv.Error) as exc:
        return None, _quarantine(name, property_id, period, f"could not read file: {exc}")

    missing_cols = sorted(set(RAW_COLUMNS) - set(header or []))
    if missing_cols:
        return None, _quarantine(
            name,
            property_id,
            period,
            f"missing required columns: {', '.join(missing_cols)}",
        )
    if not raw_rows:
        return None, _quarantine(name, property_id, period, "file has no data rows")

    reasons: list[str] = []

    present_codes = [row["line_code"] for row in raw_rows]
    unknown = sorted(set(present_codes) - set(LINE_CODES))
    if unknown:
        reasons.append(f"unknown line codes: {', '.join(unknown)}")
    duplicates = sorted({code for code in present_codes if present_codes.count(code) > 1})
    if duplicates:
        reasons.append(f"duplicate line codes: {', '.join(duplicates)}")
    missing_codes = sorted(REQUIRED_CODES - set(present_codes))
    if missing_codes:
        reasons.append(f"missing required line codes: {', '.join(missing_codes)}")
    wrong_section = sorted(
        {
            row["line_code"]
            for row in raw_rows
            if row["line_code"] in CODE_TO_SECTION
            and row["section"] != CODE_TO_SECTION[row["line_code"]]
        }
    )
    if wrong_section:
        reasons.append(f"line codes in wrong section: {', '.join(wrong_section)}")

    for row in raw_rows:
        value = row.get("amount")
        try:
            amount = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            reasons.append(f"non-numeric amount for {row.get('line_code')}: {value!r}")
            continue
        if amount <= 0:
            reasons.append(f"non-positive amount for {row.get('line_code')}: {amount}")

    if reasons:
        return None, _quarantine(name, property_id, period, "; ".join(reasons))

    # All structural checks passed. Build tidy rows and run the authoritative schema.
    tidy = to_tidy_rows(raw_rows, property_id, period)
    frame = pd.DataFrame(tidy, columns=TIDY_COLUMNS)
    try:
        TIDY_SCHEMA.validate(frame, lazy=True)
    except (pa.errors.SchemaErrors, pa.errors.SchemaError) as exc:
        return None, _quarantine(name, property_id, period, _schema_reason(exc))

    return tidy, None


def validate_paths(
    paths: list[str | Path],
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Validate many files, streaming one at a time (the scale guardrail, ADR-0002).

    Returns the flat list of accepted tidy rows and the list of quarantine entries.
    """
    accepted: list[dict[str, object]] = []
    quarantined: list[dict[str, str]] = []
    for path in sorted(paths, key=lambda p: Path(p).name):
        rows, quarantine_entry = validate_file(path)
        if quarantine_entry is not None:
            quarantined.append(quarantine_entry)
        else:
            assert rows is not None
            accepted.extend(rows)
    return accepted, quarantined
