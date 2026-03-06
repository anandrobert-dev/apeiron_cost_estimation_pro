"""
Tests for app.domain.estimation_calculator – Pure domain logic.
No DB fixtures needed.
"""

import pytest
from app.domain.estimation_calculator import (
    calculate_stage_distribution,
    calculate_infra_stack_total,
    calculate_gross_cost,
    calculate_risk_buffer,
    calculate_final_price,
    cost_per_function_point,
    burn_rate_monthly,
    revenue_margin,
    contribution_margin,
)


class TestStageDistribution:
    def test_default(self):
        dist = calculate_stage_distribution(100000)
        assert dist["Planning"] == 10000
        assert dist["Design"] == 15000
        assert dist["Development"] == 60000
        assert dist["Testing"] == 10000
        assert dist["Deployment"] == 5000
        assert sum(dist.values()) == 100000

    def test_custom(self):
        dist = calculate_stage_distribution(
            200000, planning_pct=20, design_pct=20,
            development_pct=40, testing_pct=15, deployment_pct=5
        )
        assert dist["Planning"] == 40000
        assert dist["Development"] == 80000

    def test_zero_cost(self):
        dist = calculate_stage_distribution(0)
        assert all(v == 0 for v in dist.values())


class TestInfraStackTotal:
    def test_basic(self):
        result = calculate_infra_stack_total([1000, 2000], [500, 1500])
        assert result["infra_total"] == 3000
        assert result["stack_total"] == 2000
        assert result["combined_total"] == 5000

    def test_empty(self):
        result = calculate_infra_stack_total([], [])
        assert result["combined_total"] == 0


class TestGrossCost:
    def test_basic(self):
        assert calculate_gross_cost(100000, 5000) == 105000


class TestRiskBuffer:
    def test_default(self):
        result = calculate_risk_buffer(100000)
        assert result["maintenance_buffer"] == 15000
        assert result["risk_contingency"] == 10000
        assert result["safe_cost"] == 125000

    def test_custom(self):
        result = calculate_risk_buffer(200000, 20, 15)
        assert result["maintenance_buffer"] == 40000
        assert result["risk_contingency"] == 30000
        assert result["safe_cost"] == 270000

    def test_zero_cost(self):
        result = calculate_risk_buffer(0)
        assert result["safe_cost"] == 0


class TestFinalPrice:
    def test_default(self):
        result = calculate_final_price(125000)
        assert result["profit_amount"] == 25000
        assert result["final_price"] == 150000

    def test_zero_profit(self):
        result = calculate_final_price(100000, 0)
        assert result["final_price"] == 100000


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
