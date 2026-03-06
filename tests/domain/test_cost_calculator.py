"""
Tests for app.domain.cost_calculator – Pure domain logic.
No DB fixtures needed.
"""

import pytest
from app.domain.cost_calculator import (
    compute_hourly_from_salary,
    calculate_module_cost,
    calculate_total_labor,
    calculate_total_hours,
    hours_to_person_months,
)


class TestComputeHourlyFromSalary:
    def test_default_percentages(self):
        result = compute_hourly_from_salary(50000)
        # total_pct = 12 + 8.33 + 4 + 5 + 3 = 32.33%
        assert result["total_add_on_pct"] == pytest.approx(32.33)
        assert result["real_monthly_cost"] == pytest.approx(66165.0, rel=0.01)
        expected_hourly = round(66165.0 / 22 / 8, 2)
        assert result["hourly_cost"] == pytest.approx(expected_hourly, rel=0.01)

    def test_zero_salary(self):
        result = compute_hourly_from_salary(0)
        assert result["real_monthly_cost"] == 0.0
        assert result["hourly_cost"] == 0.0

    def test_custom_percentages(self):
        result = compute_hourly_from_salary(
            100000, pf_pct=10, bonus_pct=10, leave_pct=5,
            infra_pct=5, admin_pct=5
        )
        assert result["real_monthly_cost"] == 135000.0
        assert result["hourly_cost"] == round(135000 / 22 / 8, 2)

    def test_high_salary(self):
        result = compute_hourly_from_salary(1_000_000)
        assert result["real_monthly_cost"] > 1_000_000
        assert result["hourly_cost"] > 0


class TestCalculateModuleCost:
    def test_basic(self):
        assert calculate_module_cost(500, 100) == 50000.0

    def test_with_region_multiplier(self):
        assert calculate_module_cost(500, 100, 4.0) == 200000.0

    def test_zero_hours(self):
        assert calculate_module_cost(500, 0) == 0.0

    def test_zero_rate(self):
        assert calculate_module_cost(0, 100) == 0.0


class TestCalculateTotalLabor:
    def test_simple(self):
        result = calculate_total_labor([50000, 60000])
        assert result["raw_labor_total"] == 110000.0
        assert result["adjusted_labor_total"] == 110000.0

    def test_with_multipliers(self):
        result = calculate_total_labor([50000], 1.3, 1.35)
        assert result["adjusted_labor_total"] == pytest.approx(87750.0)

    def test_empty(self):
        result = calculate_total_labor([])
        assert result["raw_labor_total"] == 0.0
        assert result["adjusted_labor_total"] == 0.0


class TestCalculateTotalHours:
    def test_basic(self):
        assert calculate_total_hours([100, 200, 300]) == 600

    def test_empty(self):
        assert calculate_total_hours([]) == 0


class TestHoursToPersonMonths:
    def test_exact(self):
        assert hours_to_person_months(176) == 1.0
        assert hours_to_person_months(352) == 2.0

    def test_zero(self):
        assert hours_to_person_months(0) == 0.0

    def test_negative(self):
        assert hours_to_person_months(-10) == 0.0
