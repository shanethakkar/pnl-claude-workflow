"""Tests for pipeline.py orchestration using the fixtures (CI-safe, no generated data)."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from pipeline import run_pipeline


def _seed_input(tmp_path: Path, valid_dir: Path, malformed_dir: Path) -> Path:
    """Copy one valid file and the four malformed files into a temp input folder."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    shutil.copy(valid_dir / "P001_2025-01.csv", input_dir)
    for name in [
        "P088_2025-09.csv",
        "P003_2025-01.csv",
        "P004_2025-01.csv",
        "not-a-pnl.csv",
    ]:
        shutil.copy(malformed_dir / name, input_dir)
    return input_dir


def test_pipeline_writes_three_outputs_and_reconciles(
    tmp_path, valid_dir, malformed_dir
) -> None:
    input_dir = _seed_input(tmp_path, valid_dir, malformed_dir)
    out_dir = tmp_path / "out"

    manifest = run_pipeline(input_dir, out_dir)

    # All three outputs exist.
    assert (out_dir / "analytics.csv").exists()
    assert (out_dir / "quarantine.csv").exists()
    assert (out_dir / "run_manifest.json").exists()

    # Manifest reconciles: seen == accepted + quarantined.
    assert manifest["files_seen"] == 5
    assert manifest["files_quarantined"] == 4
    assert manifest["files_accepted"] == 1
    assert manifest["files_seen"] == (
        manifest["files_accepted"] + manifest["files_quarantined"]
    )
    assert manifest["rows_extracted"] == manifest["files_accepted"] * 9
    assert manifest["analytics_rows"] == 1

    # Every input has a content hash and a status.
    assert len(manifest["inputs"]) == 5
    assert all(len(entry["sha256"]) == 64 for entry in manifest["inputs"])


def test_pipeline_quarantine_csv_lists_bad_files(
    tmp_path, valid_dir, malformed_dir
) -> None:
    input_dir = _seed_input(tmp_path, valid_dir, malformed_dir)
    out_dir = tmp_path / "out"
    run_pipeline(input_dir, out_dir)

    with (out_dir / "quarantine.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    filenames = {row["filename"] for row in rows}
    assert "P088_2025-09.csv" in filenames
    assert "not-a-pnl.csv" in filenames
    assert len(rows) == 4


def test_pipeline_manifest_is_valid_json(tmp_path, valid_dir, malformed_dir) -> None:
    input_dir = _seed_input(tmp_path, valid_dir, malformed_dir)
    out_dir = tmp_path / "out"
    run_pipeline(input_dir, out_dir)
    loaded = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert loaded["tool"] == "pnl-labor-analysis"
