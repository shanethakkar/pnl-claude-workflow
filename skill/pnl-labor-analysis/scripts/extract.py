"""Extraction: one P&L CSV in, tidy long rows out (SPEC.md section 6.2, ADR-0003).

The transform is a pure function: `to_tidy_rows` takes raw rows plus the property and
period parsed from the filename and returns tidy rows, with no hidden state and no side
effects. `extract_file` is the thin I/O wrapper that reads a file and calls the pure
transform. Validation and quarantine live in validate.py; this module assumes well-formed
input and raises on anything it cannot parse.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from schema import RAW_COLUMNS

# Filename convention: {property_id}_{period}.csv, for example P017_2025-07.csv.
FILENAME_RE = re.compile(r"^(?P<property_id>P\d{3})_(?P<period>\d{4}-\d{2})\.csv$")


def parse_filename(filename: str) -> tuple[str, str]:
    """Parse property_id and period from a filename.

    Raises ValueError if the filename does not match the convention.
    """
    match = FILENAME_RE.match(filename)
    if match is None:
        raise ValueError(
            f"filename does not match the P<id>_<YYYY-MM>.csv convention: {filename}"
        )
    return match.group("property_id"), match.group("period")


def read_raw_rows(path: str | Path) -> tuple[list[str] | None, list[dict[str, str]]]:
    """Read a raw P&L CSV. Returns its header and its rows as dicts of strings.

    This is the I/O boundary. It does no validation beyond CSV parsing.
    """
    path = Path(path)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames
        rows = [dict(row) for row in reader]
    return header, rows


def to_tidy_rows(
    raw_rows: list[dict[str, str]], property_id: str, period: str
) -> list[dict[str, object]]:
    """Pure transform: raw rows plus identity to tidy long rows.

    Coerces amount to float. Raises ValueError on a non-numeric amount.
    """
    tidy: list[dict[str, object]] = []
    for row in raw_rows:
        try:
            amount = float(row["amount"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"non-numeric amount {row.get('amount')!r} for line "
                f"{row.get('line_code')!r}"
            ) from exc
        tidy.append(
            {
                "property_id": property_id,
                "period": period,
                "section": row["section"],
                "line_code": row["line_code"],
                "line_label": row["line_label"],
                "amount": amount,
            }
        )
    return tidy


def extract_file(path: str | Path) -> list[dict[str, object]]:
    """Read one CSV and return tidy rows. Property and period come from the filename."""
    path = Path(path)
    property_id, period = parse_filename(path.name)
    header, raw_rows = read_raw_rows(path)
    if header is None or set(RAW_COLUMNS) - set(header):
        missing = sorted(set(RAW_COLUMNS) - set(header or []))
        raise ValueError(f"missing required columns: {', '.join(missing)}")
    return to_tidy_rows(raw_rows, property_id, period)
