"""Adversarial acceptance test (SPEC.md section 9 Phase 5, ADR-0005).

Generates a fresh synthetic portfolio and answer key, runs the full pipeline end to end via
subprocess (exactly as the Skill would), then recovers the seeded anomalies using only
generic statistical rules. The pipeline never sees the answer key. Only this test reads it,
and only to compare the recovered results against the planted ground truth.

This is the gate that proves the detector finds planted truth without being told where it
is. If any assertion here fails, stop and report. Do not advance to packaging.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "tools" / "generate.py"
PIPELINE = REPO_ROOT / "skill" / "pnl-labor-analysis" / "scripts" / "pipeline.py"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="module")
def acceptance_run(tmp_path_factory) -> dict[str, object]:
    """Generate data, run the pipeline, and return analytics, quarantine, and the key."""
    base = tmp_path_factory.mktemp("acceptance")
    data_dir = base / "synthetic"
    answer_key_path = base / "answer_key.json"
    out_dir = data_dir / "_pnl_output"

    subprocess.run(
        [
            sys.executable, str(GENERATOR),
            "--out", str(data_dir),
            "--answer-key", str(answer_key_path),
            "--properties", "100",
            "--periods", "12",
            "--start", "2025-01",
            "--seed", "42",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [sys.executable, str(PIPELINE), "--input", str(data_dir), "--out", str(out_dir)],
        check=True,
        capture_output=True,
    )

    analytics = _read_csv(out_dir / "analytics.csv")
    quarantine = _read_csv(out_dir / "quarantine.csv")
    answer_key = json.loads(answer_key_path.read_text(encoding="utf-8"))
    return {"analytics": analytics, "quarantine": quarantine, "answer_key": answer_key}


def test_spike_is_highest_z_in_its_period(acceptance_run) -> None:
    """Generic rule: the highest within-period z-score in 2025-07 is the spike."""
    spike = acceptance_run["answer_key"]["spike"]
    period = spike["period"]

    in_period = [row for row in acceptance_run["analytics"] if row["period"] == period]
    top = max(in_period, key=lambda row: float(row["labor_pct_z_within_period"]))

    assert top["property_id"] == spike["property_id"]
    assert float(top["labor_pct"]) >= spike["labor_pct_min"]


def test_drift_cluster_is_top_five_slopes(acceptance_run) -> None:
    """Generic rule: the five highest labor_pct_slope properties are the drift cluster."""
    drift = acceptance_run["answer_key"]["drift_cluster"]
    expected = set(drift["property_ids"])

    # labor_pct_slope is repeated per property, so collapse to one value per property.
    slope_by_property: dict[str, float] = {}
    for row in acceptance_run["analytics"]:
        slope_by_property[row["property_id"]] = float(row["labor_pct_slope"])

    ranked = sorted(slope_by_property.items(), key=lambda item: item[1], reverse=True)
    top_five = ranked[:5]
    top_five_ids = {property_id for property_id, _ in top_five}

    assert top_five_ids == expected
    for _, slope in top_five:
        assert slope >= drift["slope_min"]


def test_malformed_file_is_quarantined(acceptance_run) -> None:
    """The malformed file appears in quarantine.csv."""
    malformed = acceptance_run["answer_key"]["malformed"]
    rows = acceptance_run["quarantine"]
    match = [
        row
        for row in rows
        if row["property_id"] == malformed["property_id"]
        and row["period"] == malformed["period"]
    ]
    assert len(match) == 1
    assert "LAB" in match[0]["reason"]
