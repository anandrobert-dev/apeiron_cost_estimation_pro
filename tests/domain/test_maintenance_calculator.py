"""
Tests for app.domain.maintenance_calculator – Pure domain logic.
No DB fixtures needed.
"""

from app.domain.maintenance_calculator import (
    calculate_maintenance_forecast,
    calculate_cumulative_maintenance,
)


class TestMaintenanceForecast:
    def test_default_forecast(self):
        forecast = calculate_maintenance_forecast(100000, 15, 3)
        assert len(forecast) == 3
        assert forecast[0]["annual_cost"] == 15000
        assert forecast[2]["cumulative_cost"] == 45000

    def test_single_year(self):
        forecast = calculate_maintenance_forecast(200000, 20, 1)
        assert len(forecast) == 1
        assert forecast[0]["annual_cost"] == 40000

    def test_zero_cost(self):
        forecast = calculate_maintenance_forecast(0, 15, 5)
        assert all(f["annual_cost"] == 0 for f in forecast)

    def test_five_years_default(self):
        forecast = calculate_maintenance_forecast(100000)
        assert len(forecast) == 5
        assert forecast[4]["cumulative_cost"] == 75000


class TestCumulativeMaintenance:
    def test_basic(self):
        forecast = calculate_maintenance_forecast(100000, 15, 3)
        assert calculate_cumulative_maintenance(forecast) == 45000

    def test_empty(self):
        assert calculate_cumulative_maintenance([]) == 0.0
