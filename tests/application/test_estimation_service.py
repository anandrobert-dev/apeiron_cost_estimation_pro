"""
Tests for EstimationService.
"""

import pytest
from app.persistence.repositories.multiplier_repository import MultiplierRepository
from app.application.estimation_service import EstimationService


class TestEstimationService:

    @pytest.fixture
    def service(self, db_session):
        repo = MultiplierRepository(db_session)
        repo.upsert_complexity("Simple", 0.8)
        repo.upsert_complexity("Medium", 1.0)
        repo.upsert_complexity("Complex", 1.4)
        repo.upsert_app_type("Productivity", 1.0)
        repo.upsert_app_type("E-commerce", 1.3)
        return EstimationService(repo)

    def test_basic_estimation(self, service):
        modules = [
            {"name": "Auth", "hourly_rate": 500.0, "estimated_hours": 40},
            {"name": "Dashboard", "hourly_rate": 500.0, "estimated_hours": 60},
        ]
        result = service.run_estimation(
            modules=modules,
            complexity="Medium",
            app_type="Productivity",
            region_multiplier=1.0,
            infra_costs=[5000.0, 3000.0],
            stack_costs=[2000.0],
            maintenance_buffer_pct=15.0,
            risk_contingency_pct=10.0,
            profit_margin_pct=20.0,
            function_points=100,
            estimated_duration_months=6.0,
        )

        assert "labor" in result
        assert "infra_stack" in result
        assert "gross_cost" in result
        assert "risk_buffer" in result
        assert "final_pricing" in result
        assert "stage_distribution" in result
        assert "maintenance_forecast" in result
        assert "analytics" in result

        # Labor: (500*40*1.0 + 500*60*1.0) * 1.0 * 1.0 = 50000
        assert result["labor"]["adjusted_labor_total"] == 50000.0
        assert result["labor"]["complexity_multiplier"] == 1.0
        assert result["labor"]["app_type_adjustment"] == 1.0
        assert len(result["labor"]["module_costs"]) == 2

        # Infra+Stack: 5000+3000=8000 infra, 2000 stack
        assert result["infra_stack"]["infra_total"] == 8000.0
        assert result["infra_stack"]["stack_total"] == 2000.0

        # Gross: 50000 + 10000 = 60000
        assert result["gross_cost"] == 60000.0

        # Final price should be > safe cost
        assert result["final_pricing"]["final_price"] > result["risk_buffer"]["safe_cost"]

    def test_complex_estimation(self, service):
        modules = [
            {"name": "Core", "hourly_rate": 600.0, "estimated_hours": 100},
        ]
        result = service.run_estimation(
            modules=modules,
            complexity="Complex",
            app_type="E-commerce",
            region_multiplier=1.5,
            infra_costs=[10000.0],
            stack_costs=[5000.0],
            maintenance_buffer_pct=15.0,
            risk_contingency_pct=10.0,
            profit_margin_pct=25.0,
        )

        # Module cost: 600 * 100 * 1.5 = 90000
        # Adjusted: 90000 * 1.4 * 1.3 = 163800
        assert result["labor"]["adjusted_labor_total"] == 163800.0
        assert result["labor"]["complexity_multiplier"] == 1.4
        assert result["labor"]["app_type_adjustment"] == 1.3

    def test_analytics_present(self, service):
        modules = [
            {"name": "API", "hourly_rate": 400.0, "estimated_hours": 80},
        ]
        result = service.run_estimation(
            modules=modules,
            complexity="Medium",
            app_type="Productivity",
            region_multiplier=1.0,
            infra_costs=[],
            stack_costs=[],
            maintenance_buffer_pct=15.0,
            risk_contingency_pct=10.0,
            profit_margin_pct=20.0,
            function_points=50,
            estimated_duration_months=4.0,
        )

        analytics = result["analytics"]
        assert analytics["total_hours"] == 80
        assert analytics["person_months"] > 0
        assert analytics["cost_per_function_point"] > 0
        assert analytics["burn_rate_monthly"] > 0

    def test_maintenance_forecast(self, service):
        modules = [
            {"name": "Backend", "hourly_rate": 500.0, "estimated_hours": 100},
        ]
        result = service.run_estimation(
            modules=modules,
            complexity="Medium",
            app_type="Productivity",
            region_multiplier=1.0,
            infra_costs=[],
            stack_costs=[],
            maintenance_buffer_pct=15.0,
            risk_contingency_pct=10.0,
            profit_margin_pct=20.0,
            maintenance_years=3,
            maintenance_annual_pct=15.0,
        )

        assert len(result["maintenance_forecast"]) == 3
        assert result["maintenance_forecast"][0]["year"] == 1
