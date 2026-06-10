"""Tests for validate.py: acceptance, quarantine, and clear reasons."""

from __future__ import annotations

from validate import validate_file, validate_paths


def test_valid_file_is_accepted(valid_dir) -> None:
    rows, quarantine = validate_file(valid_dir / "P001_2025-01.csv")
    assert quarantine is None
    assert rows is not None
    assert len(rows) == 9


def test_missing_labor_rows_quarantined_with_reason(malformed_dir) -> None:
    rows, quarantine = validate_file(malformed_dir / "P088_2025-09.csv")
    assert rows is None
    assert quarantine is not None
    assert quarantine["property_id"] == "P088"
    assert quarantine["period"] == "2025-09"
    reason = quarantine["reason"]
    assert "missing required line codes" in reason
    # All three LABOR codes are named.
    assert "LAB_ROOMS" in reason
    assert "LAB_FNB" in reason
    assert "LAB_ADMIN" in reason


def test_negative_amount_quarantined(malformed_dir) -> None:
    rows, quarantine = validate_file(malformed_dir / "P003_2025-01.csv")
    assert rows is None
    assert quarantine is not None
    assert "non-positive amount" in quarantine["reason"]
    assert "LAB_FNB" in quarantine["reason"]


def test_unknown_code_and_missing_required_quarantined(malformed_dir) -> None:
    rows, quarantine = validate_file(malformed_dir / "P004_2025-01.csv")
    assert rows is None
    assert quarantine is not None
    reason = quarantine["reason"]
    assert "unknown line codes: LAB_MYSTERY" in reason
    assert "missing required line codes: LAB_ADMIN" in reason


def test_bad_filename_quarantined(malformed_dir) -> None:
    rows, quarantine = validate_file(malformed_dir / "not-a-pnl.csv")
    assert rows is None
    assert quarantine is not None
    assert quarantine["property_id"] == "UNKNOWN"
    assert "convention" in quarantine["reason"]


def test_validate_paths_separates_accepted_and_quarantined(
    valid_dir, malformed_dir
) -> None:
    paths = [
        valid_dir / "P001_2025-01.csv",
        malformed_dir / "P088_2025-09.csv",
        malformed_dir / "P003_2025-01.csv",
        malformed_dir / "P004_2025-01.csv",
        malformed_dir / "not-a-pnl.csv",
    ]
    accepted, quarantined = validate_paths(paths)
    # Only the one valid file is accepted: 9 rows.
    assert len(accepted) == 9
    assert len(quarantined) == 4
    quarantined_ids = {entry["filename"] for entry in quarantined}
    assert "P088_2025-09.csv" in quarantined_ids
    assert "not-a-pnl.csv" in quarantined_ids
