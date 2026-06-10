"""Tests for aggregate.py against a hand-checked fixture.

Two properties over three periods, with labor_pct chosen so every derived column can be
verified by manual arithmetic:

    P001 labor_pct: 0.20, 0.30, 0.40   (revenue 1000, labor 200/300/400)
    P002 labor_pct: 0.50, 0.50, 0.50   (revenue 1000, labor 500/500/500)

Hand-computed expectations:
    delta  P001: None, 0.10, 0.10        P002: None, 0.00, 0.00
    slope  P001: 0.10 per period         P002: 0.00
    z (population, two properties per period) is -1.0 for P001 and +1.0 for P002 in every
    period, since each period has exactly two symmetric values.
"""

from __future__ import annotations

import pytest

from aggregate import aggregate_rows

PERIODS = ["2025-01", "2025-02", "2025-03"]
LABOR_BY_PROPERTY = {
    "P001": [200.0, 300.0, 400.0],
    "P002": [500.0, 500.0, 500.0],
}
REVENUE = 1000.0


def _tidy_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for property_id, labors in LABOR_BY_PROPERTY.items():
        for period, labor in zip(PERIODS, labors):
            rows.append(
                {
                    "property_id": property_id,
                    "period": period,
                    "section": "REVENUE",
                    "line_code": "REV_ROOMS",
                    "line_label": "Rooms Revenue",
                    "amount": REVENUE,
                }
            )
            rows.append(
                {
                    "property_id": property_id,
                    "period": period,
                    "section": "LABOR",
                    "line_code": "LAB_ROOMS",
                    "line_label": "Rooms Labor",
                    "amount": labor,
                }
            )
    return rows


@pytest.fixture
def analytics() -> dict[tuple[str, str], dict[str, object]]:
    rows = aggregate_rows(_tidy_rows())
    return {(row["property_id"], row["period"]): row for row in rows}


def test_row_count(analytics) -> None:
    assert len(analytics) == 6


def test_totals_and_labor_pct(analytics) -> None:
    assert analytics[("P001", "2025-01")]["total_revenue"] == pytest.approx(1000.0)
    assert analytics[("P001", "2025-01")]["total_labor"] == pytest.approx(200.0)
    assert analytics[("P001", "2025-01")]["labor_pct"] == pytest.approx(0.20)
    assert analytics[("P001", "2025-03")]["labor_pct"] == pytest.approx(0.40)
    assert analytics[("P002", "2025-02")]["labor_pct"] == pytest.approx(0.50)


def test_labor_pct_delta(analytics) -> None:
    assert analytics[("P001", "2025-01")]["labor_pct_delta"] is None
    assert analytics[("P001", "2025-02")]["labor_pct_delta"] == pytest.approx(0.10)
    assert analytics[("P001", "2025-03")]["labor_pct_delta"] == pytest.approx(0.10)
    assert analytics[("P002", "2025-01")]["labor_pct_delta"] is None
    assert analytics[("P002", "2025-02")]["labor_pct_delta"] == pytest.approx(0.0)


def test_labor_pct_slope_repeated_per_property(analytics) -> None:
    for period in PERIODS:
        assert analytics[("P001", period)]["labor_pct_slope"] == pytest.approx(0.10)
        assert analytics[("P002", period)]["labor_pct_slope"] == pytest.approx(0.0)


def test_labor_pct_z_within_period(analytics) -> None:
    for period in PERIODS:
        assert analytics[("P001", period)]["labor_pct_z_within_period"] == pytest.approx(
            -1.0
        )
        assert analytics[("P002", period)]["labor_pct_z_within_period"] == pytest.approx(
            1.0
        )
