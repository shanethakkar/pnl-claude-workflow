"""Pipeline orchestrator (SPEC.md section 8).

Wires extraction, validation, and aggregation, then writes three outputs to the output
folder:
- analytics.csv:    the compact table the model reads (SPEC.md section 6.3).
- quarantine.csv:   one row per rejected file with the reason (ADR-0004).
- run_manifest.json: the audit trail: inputs seen, row counts, quarantine count, a content
                     hash per input file, and a timestamp.

The model invokes this script. It never analyzes raw CSVs directly (ADR-0001). The pipeline
exits non-zero only on its own failure. A quarantined input is a normal, reported outcome,
not a pipeline failure.

Usage:
    python pipeline.py --input <folder-of-csvs> --out <folder>/_pnl_output

If --out is omitted it defaults to a _pnl_output subfolder inside the input folder, so
results land where the user can see them.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import click

from aggregate import ANALYTICS_COLUMNS, aggregate_rows
from validate import QUARANTINE_COLUMNS, validate_paths

TOOL_NAME = "pnl-labor-analysis"
TOOL_VERSION = "0.1.0"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(
    path: Path, columns: list[str], rows: list[dict[str, object]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col) for col in columns})


def run_pipeline(input_dir: Path, out_dir: Path) -> dict[str, object]:
    """Run the full pipeline. Returns the manifest dict.

    Discovers CSV files directly in input_dir (non-recursive, so a nested output folder is
    never reprocessed), validates and aggregates them, and writes the three outputs.
    """
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(input_dir.glob("*.csv"), key=lambda p: p.name)

    accepted_rows, quarantined = validate_paths(list(paths))
    analytics = aggregate_rows(accepted_rows)

    _write_csv(out_dir / "analytics.csv", ANALYTICS_COLUMNS, analytics)
    _write_csv(out_dir / "quarantine.csv", QUARANTINE_COLUMNS, quarantined)

    quarantined_names = {entry["filename"] for entry in quarantined}
    inputs = [
        {
            "filename": path.name,
            "sha256": _sha256(path),
            "status": "quarantined" if path.name in quarantined_names else "accepted",
        }
        for path in paths
    ]

    manifest: dict[str, object] = {
        "tool": TOOL_NAME,
        "version": TOOL_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "output_dir": str(out_dir),
        "files_seen": len(paths),
        "files_accepted": len(paths) - len(quarantined),
        "files_quarantined": len(quarantined),
        "rows_extracted": len(accepted_rows),
        "analytics_rows": len(analytics),
        "inputs": inputs,
    }
    (out_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


@click.command()
@click.option(
    "--input",
    "input_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Folder of P&L CSV files.",
)
@click.option(
    "--out",
    "out_dir",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Output folder. Defaults to <input>/_pnl_output.",
)
def main(input_dir: Path, out_dir: Path | None) -> None:
    """Reduce a folder of P&L CSVs into analytics.csv, quarantine.csv, and a manifest."""
    if out_dir is None:
        out_dir = input_dir / "_pnl_output"
    manifest = run_pipeline(input_dir, out_dir)
    click.echo(
        f"Processed {manifest['files_seen']} files: "
        f"{manifest['files_accepted']} accepted, "
        f"{manifest['files_quarantined']} quarantined. "
        f"Wrote {manifest['analytics_rows']} analytics rows to {out_dir}."
    )


if __name__ == "__main__":
    main()
