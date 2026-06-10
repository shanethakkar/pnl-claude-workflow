"""Build the shippable Skill zip (dev-time only).

Zips the self-contained Skill folder for installation in Cowork, excluding __pycache__ and
compiled files. The zip's top-level folder is the Skill name so Cowork unpacks it cleanly.
Keep the version in the filename so updates are a clean re-install (SPEC.md section 13).

Usage:
    uv run python tools/build_skill.py
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skill" / "pnl-labor-analysis"
SKILL_PARENT = SKILL_DIR.parent
VERSION = "0.1.0"
OUT_PATH = REPO_ROOT / "dist" / f"pnl-labor-analysis-v{VERSION}.zip"


def build() -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(OUT_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for dirpath, dirnames, filenames in os.walk(SKILL_DIR):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for filename in filenames:
                if filename.endswith((".pyc", ".pyo")):
                    continue
                full = Path(dirpath) / filename
                arcname = full.relative_to(SKILL_PARENT)
                archive.write(full, arcname)
                count += 1
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)} with {count} files.")
    return OUT_PATH


if __name__ == "__main__":
    build()
