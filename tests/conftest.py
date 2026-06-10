"""Test configuration.

The Skill's scripts use flat imports (for example `from schema import ...`) because in the
Cowork sandbox they are run from the scripts directory, which Python places on sys.path
automatically. Tests run from the repo root, so we add the scripts directory to sys.path
here and expose fixture paths as fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "skill" / "pnl-labor-analysis" / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def valid_dir() -> Path:
    return FIXTURES_DIR / "valid"


@pytest.fixture
def malformed_dir() -> Path:
    return FIXTURES_DIR / "malformed"
