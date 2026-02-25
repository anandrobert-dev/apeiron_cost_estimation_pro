"""
Apeiron CostEstimation Pro – Unit Tests for Financial Logic
============================================================
Tests cover: employee costs, labor calculation, risk/buffer,
stage distribution, maintenance forecast, variance, formatting.
"""

import pytest
from unittest.mock import MagicMock
from app.logic import (
    compute_hourly_from_salary,
    get_complexity_multiplier,
    get_app_type_adjustment,
    calculate_module_cost,
    calculate_total_labor_cost,
    calculate_total_hours,
    hours_to_person_months,
    calculate_stage_distribution,
    calculate_infra_stack_total,
    calculate_risk_buffer,
    calculate_final_price,
    calculate_maintenance_forecast,
    calculate_variance,
    cost_per_function_point,
    burn_rate_monthly,
    revenue_margin,
    contribution_margin,
    format_inr,
    run_full_estimation,
)


# ──────────────────────────────────────────────
# EMPLOYEE COST MODELING
# ──────────────────────────────────────────────
class TestEmployeeCost:
    def test_default_percentages(self):
        result = compute_hourly_from_salary(50000)
        # total_pct = 12 + 8.33 + 4 + 5 + 3 = 32.33%
        assert result["total_add_on_pct"] == pytest.approx(32.33)
        # real_monthly = 50000 * 1.3233 = 66165.0
        assert result["real_monthly_cost"] == pytest.approx(66165.0, rel=0.01)
        # hourly = 66165 / 22 / 8
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
        # total_pct = 35, real_monthly = 100000 * 1.35 = 135000
        assert result["real_monthly_cost"] == 135000.0
        assert result["hourly_cost"] == round(135000 / 22 / 8, 2)


# ──────────────────────────────────────────────
# COMPLEXITY & APP TYPE
# ──────────────────────────────────────────────
class TestMultipliers:
    def _mock_session(self, multiplier_value):
        session = MagicMock()
        query = MagicMock()
        record = MagicMock()
        record.multiplier = multiplier_value
        session.query.return_value = query
        query.filter_by.return_value = query
        query.first.return_value = record
        return session

    def test_complexity_known(self):
        session = self._mock_session(0.8)
        assert get_complexity_multiplier(session, "Simple") == 0.8

    def test_complexity_unknown(self):
        session = MagicMock()
        session.query().filter_by().first.return_value = None
        assert get_complexity_multiplier(session, "Unknown") == 1.0

    def test_app_type_known(self):
        session = self._mock_session(1.35)
        assert get_app_type_adjustment(session, "AI") == 1.35

    def test_app_type_unknown(self):
        session = MagicMock()
        session.query().filter_by().first.return_value = None
        assert get_app_type_adjustment(session, "Unknown") == 1.0


# ──────────────────────────────────────────────
# MODULE & LABOR COST
# ──────────────────────────────────────────────
class TestLaborCost:
    def _mock_module(self, name="Module1", hours=100, hourly=500, override=None):
        mod = MagicMock()
        mod.name = name
        mod.estimated_hours = hours
        mod.hourly_rate_override = override
        if override is None:
            emp = MagicMock()
            emp.hourly_cost = hourly
            mod.employee = emp
        else:
            mod.employee = None
        mod.cost = 0
        return mod

    def test_module_cost_basic(self):
        mod = self._mock_module(hours=100, hourly=500)
        cost = calculate_module_cost(mod)
        assert cost == 50000.0

    def test_module_cost_with_region(self):
        mod = self._mock_module(hours=100, hourly=500)
        cost = calculate_module_cost(mod, region_multiplier=4.0)
        assert cost == 200000.0

    def test_module_cost_with_override(self):
        mod = self._mock_module(hours=50, hourly=500, override=1000)
        cost = calculate_module_cost(mod)
        assert cost == 50000.0

    def _mock_session(self, cx_mult, app_mult):
        session = MagicMock()
        def side_effect(model):
            q = MagicMock()
            rec = MagicMock()
            if model.__name__ == 'ComplexityMultiplier':
                rec.multiplier = cx_mult
            else:
                rec.multiplier = app_mult
            q.filter_by.return_value.first.return_value = rec
            return q
        session.query.side_effect = side_effect
        return session

    def test_total_labor_cost(self):
        m1 = self._mock_module("A", 100, 500)
        m2 = self._mock_module("B", 200, 300)
        session = self._mock_session(1.0, 1.0)
        result = calculate_total_labor_cost(session, [m1, m2], "Medium", "Productivity")
        # raw = 50000 + 60000 = 110000, cx=1.0, app=1.0
        assert result["raw_labor_total"] == 110000.0
        assert result["adjusted_labor_total"] == 110000.0

    def test_total_labor_cost_complex_ai(self):
        m1 = self._mock_module("A", 100, 500)
        session = self._mock_session(1.3, 1.35)
        result = calculate_total_labor_cost(session, [m1], "Complex", "AI")
        # raw = 50000, cx=1.3, app=1.35 → 50000 * 1.3 * 1.35 = 87750
        assert result["adjusted_labor_total"] == pytest.approx(87750.0)


# ──────────────────────────────────────────────
# HOURS & PERSON-MONTHS
# ──────────────────────────────────────────────
class TestHours:
    def test_total_hours(self):
        m1 = MagicMock()
        m1.estimated_hours = 100
        m2 = MagicMock()
        m2.estimated_hours = 200
        assert calculate_total_hours([m1, m2]) == 300

    def test_person_months(self):
        assert hours_to_person_months(176) == 1.0
        assert hours_to_person_months(352) == 2.0
        assert hours_to_person_months(0) == 0.0


# ──────────────────────────────────────────────
# STAGE DISTRIBUTION
# ──────────────────────────────────────────────
class TestStageDistribution:
    def test_default_distribution(self):
        dist = calculate_stage_distribution(100000)
        assert dist["Planning"] == 10000
        assert dist["Design"] == 15000
        assert dist["Development"] == 60000
        assert dist["Testing"] == 10000
        assert dist["Deployment"] == 5000
        assert sum(dist.values()) == 100000

    def test_custom_distribution(self):
        dist = calculate_stage_distribution(
            200000, planning_pct=20, design_pct=20,
            development_pct=40, testing_pct=15, deployment_pct=5
        )
        assert dist["Planning"] == 40000
        assert dist["Development"] == 80000


# ──────────────────────────────────────────────
# RISK & BUFFER
# ──────────────────────────────────────────────
class TestRiskBuffer:
    def test_default_risk(self):
        result = calculate_risk_buffer(100000)
        assert result["maintenance_buffer"] == 15000
        assert result["risk_contingency"] == 10000
        assert result["safe_cost"] == 125000

    def test_custom_risk(self):
        result = calculate_risk_buffer(200000, 20, 15)
        assert result["maintenance_buffer"] == 40000
        assert result["risk_contingency"] == 30000
        assert result["safe_cost"] == 270000


# ──────────────────────────────────────────────
# FINAL PRICE
# ──────────────────────────────────────────────
class TestFinalPrice:
    def test_default_profit(self):
        result = calculate_final_price(125000)
        assert result["profit_amount"] == 25000
        assert result["final_price"] == 150000

    def test_zero_profit(self):
        result = calculate_final_price(100000, 0)
        assert result["final_price"] == 100000


# ──────────────────────────────────────────────
# MAINTENANCE FORECAST
# ──────────────────────────────────────────────
class TestMaintenance:
    def test_default_forecast(self):
        forecast = calculate_maintenance_forecast(100000, 15, 3)
        assert len(forecast) == 3
        assert forecast[0]["annual_cost"] == 15000
        assert forecast[2]["cumulative_cost"] == 45000

    def test_single_year(self):
        forecast = calculate_maintenance_forecast(200000, 20, 1)
        assert len(forecast) == 1
        assert forecast[0]["annual_cost"] == 40000


# ──────────────────────────────────────────────
# VARIANCE
# ──────────────────────────────────────────────
class TestVariance:
    def test_perfect_estimate(self):
        result = calculate_variance(100000, 103000)
        assert result["variance_pct"] == 3.0
        assert result["is_perfect"] is True
        assert "PERFECT" in result["classification"]

    def test_controlled(self):
        result = calculate_variance(100000, 108000)
        assert result["variance_pct"] == 8.0
        assert "Controlled" in result["classification"]

    def test_moderate(self):
        result = calculate_variance(100000, 115000)
        assert "Moderate" in result["classification"]

    def test_high_risk(self):
        result = calculate_variance(100000, 125000)
        assert "High Risk" in result["classification"]

    def test_zero_estimated(self):
        result = calculate_variance(0, 100)
        assert result["classification"] == "N/A"


# ──────────────────────────────────────────────
# ANALYTICS
# ──────────────────────────────────────────────
class TestAnalytics:
    def test_cost_per_fp(self):
        assert cost_per_function_point(100000, 200) == 500.0
        assert cost_per_function_point(100000, 0) == 0.0

    def test_burn_rate(self):
        assert burn_rate_monthly(600000, 6) == 100000.0
        assert burn_rate_monthly(600000, 0) == 0.0

    def test_revenue_margin(self):
        assert revenue_margin(150000, 125000) == pytest.approx(16.67, rel=0.01)
        assert revenue_margin(0, 125000) == 0.0

    def test_contribution_margin(self):
        assert contribution_margin(150000, 60000) == 90000.0


# ──────────────────────────────────────────────
# CURRENCY FORMAT
# ──────────────────────────────────────────────
class TestCurrencyFormat:
    def test_small_number(self):
        assert format_inr(500) == "₹500.00"

    def test_thousands(self):
        assert format_inr(50000) == "₹50,000.00"

    def test_lakhs(self):
        assert format_inr(150000) == "₹1,50,000.00"

    def test_crores(self):
        assert format_inr(10000000) == "₹1,00,00,000.00"

    def test_negative(self):
        result = format_inr(-50000)
        assert result.startswith("-₹")

    def test_zero(self):
        assert format_inr(0) == "₹0.00"


# ──────────────────────────────────────────────
# FULL ESTIMATION PIPELINE
# ──────────────────────────────────────────────
class TestFullEstimation:
    def test_full_pipeline(self):
        mod = MagicMock()
        mod.name = "Core"
        mod.estimated_hours = 200
        mod.hourly_rate_override = None
        emp = MagicMock()
        emp.hourly_cost = 400
        mod.employee = emp
        mod.cost = 0

        session = MagicMock()
        def side_effect(model):
            q = MagicMock()
            rec = MagicMock()
            rec.multiplier = 1.0
            q.filter_by.return_value.first.return_value = rec
            return q
        session.query.side_effect = side_effect
        
        result = run_full_estimation(
            session=session,
            modules=[mod],
            complexity="Medium",
            app_type="Productivity",
            region_multiplier=1.0,
            infra_items=[],
            stack_items=[],
            maintenance_buffer_pct=15,
            risk_contingency_pct=10,
            profit_margin_pct=20,
            function_points=100,
            estimated_duration_months=6,
        )

        assert result["gross_cost"] > 0
        assert result["risk_buffer"]["safe_cost"] > result["gross_cost"]
        assert result["final_pricing"]["final_price"] > result["risk_buffer"]["safe_cost"]
        assert len(result["stage_distribution"]) == 5
        assert len(result["maintenance_forecast"]) == 5
        assert result["analytics"]["person_months"] > 0



