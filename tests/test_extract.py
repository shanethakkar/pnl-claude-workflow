"""Tests for extract.py: filename parsing and the pure tidy transform."""

from __future__ import annotations

import pytest

from extract import extract_file, parse_filename, to_tidy_rows


def test_parse_filename_valid() -> None:
    assert parse_filename("P017_2025-07.csv") == ("P017", "2025-07")


@pytest.mark.parametrize(
    "name",
    ["not-a-pnl.csv", "P17_2025-07.csv", "P017_2025-7.csv", "P017_2025-07.txt"],
)
def test_parse_filename_rejects_bad_names(name: str) -> None:
    with pytest.raises(ValueError):
        parse_filename(name)


def test_to_tidy_rows_is_pure_and_coerces_amount() -> None:
    raw = [
        {
            "section": "REVENUE",
            "line_code": "REV_ROOMS",
            "line_label": "Rooms Revenue",
            "amount": "600000.00",
        }
    ]
    raw_snapshot = [dict(row) for row in raw]
    tidy = to_tidy_rows(raw, "P001", "2025-01")
    assert tidy == [
        {
            "property_id": "P001",
            "period": "2025-01",
            "section": "REVENUE",
            "line_code": "REV_ROOMS",
            "line_label": "Rooms Revenue",
            "amount": 600000.00,
        }
    ]
    assert isinstance(tidy[0]["amount"], float)
    # Pure: the input was not mutated.
    assert raw == raw_snapshot


def test_to_tidy_rows_rejects_non_numeric_amount() -> None:
    raw = [
        {
            "section": "REVENUE",
            "line_code": "REV_ROOMS",
            "line_label": "Rooms Revenue",
            "amount": "n/a",
        }
    ]
    with pytest.raises(ValueError):
        to_tidy_rows(raw, "P001", "2025-01")


def test_extract_file_valid_fixture_exact_rows(valid_dir) -> None:
    rows = extract_file(valid_dir / "P001_2025-01.csv")
    assert len(rows) == 9
    assert all(row["property_id"] == "P001" for row in rows)
    assert all(row["period"] == "2025-01" for row in rows)

    revenue = sum(r["amount"] for r in rows if r["section"] == "REVENUE")
    labor = sum(r["amount"] for r in rows if r["section"] == "LABOR")
    assert revenue == 1_000_000.00
    assert labor == 300_000.00
    # The fixture is hand-built so labor_pct is exactly 0.30.
    assert labor / revenue == pytest.approx(0.30)

    first = rows[0]
    assert first == {
        "property_id": "P001",
        "period": "2025-01",
        "section": "REVENUE",
        "line_code": "REV_ROOMS",
        "line_label": "Rooms Revenue",
        "amount": 600000.00,
    }
