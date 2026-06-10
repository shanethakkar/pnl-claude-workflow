"""Canonical line dictionary and pandera schemas.

This module is the single source of truth for what a valid P&L file looks like
(SPEC.md sections 6.1 and 6.2, ADR-0003). The generator, the extractor, and the
validator all conform to the dictionary defined here. The Skill is self-contained, so
this file does not import from the dev-time generator in tools/.

Two pandera schemas:
- RAW_SCHEMA validates the four columns of a raw P&L CSV: types, allowed values, and
  positive amounts.
- TIDY_SCHEMA validates the six-column tidy long row that extraction produces.

Cross-row structural checks (exactly the nine required lines, no duplicates, no unknown
codes) live in validate.py so that each failure can be quarantined with a clear reason.
"""

from __future__ import annotations

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

# Canonical line dictionary: section to list of (line_code, line_label).
LINE_DICT: dict[str, list[tuple[str, str]]] = {
    "REVENUE": [
        ("REV_ROOMS", "Rooms Revenue"),
        ("REV_FNB", "Food and Beverage Revenue"),
        ("REV_OTHER", "Other Revenue"),
    ],
    "LABOR": [
        ("LAB_ROOMS", "Rooms Labor"),
        ("LAB_FNB", "Food and Beverage Labor"),
        ("LAB_ADMIN", "Administrative Labor"),
    ],
    "OTHER_EXPENSE": [
        ("EXP_UTILITIES", "Utilities"),
        ("EXP_MAINT", "Maintenance"),
        ("EXP_OTHER", "Other Expense"),
    ],
}

SECTIONS: list[str] = list(LINE_DICT)

# line_code to its owning section, and the full set of valid codes.
CODE_TO_SECTION: dict[str, str] = {
    code: section for section, lines in LINE_DICT.items() for code, _ in lines
}
LINE_CODES: list[str] = list(CODE_TO_SECTION)

# The exact set of line codes a valid file must contain, no more and no fewer.
REQUIRED_CODES: frozenset[str] = frozenset(LINE_CODES)

RAW_COLUMNS: list[str] = ["section", "line_code", "line_label", "amount"]
TIDY_COLUMNS: list[str] = ["property_id", "period", *RAW_COLUMNS]

RAW_SCHEMA = DataFrameSchema(
    {
        "section": Column(str, Check.isin(SECTIONS)),
        "line_code": Column(str, Check.isin(LINE_CODES)),
        "line_label": Column(str),
        "amount": Column(float, Check.gt(0)),
    },
    coerce=True,
    strict=True,
)

TIDY_SCHEMA = DataFrameSchema(
    {
        "property_id": Column(str, Check.str_matches(r"^P\d{3}$")),
        "period": Column(str, Check.str_matches(r"^\d{4}-\d{2}$")),
        "section": Column(str, Check.isin(SECTIONS)),
        "line_code": Column(str, Check.isin(LINE_CODES)),
        "line_label": Column(str),
        "amount": Column(float, Check.gt(0)),
    },
    coerce=True,
    strict=True,
)
