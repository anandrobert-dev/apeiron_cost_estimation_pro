"""
Apeiron CostEstimation Pro – Maintenance Calculator (Domain)
============================================================
Maintenance forecasting logic.
NO imports from persistence, application, or ui layers.
"""


def calculate_maintenance_forecast(
    development_cost: float,
    annual_pct: float = 15.0,
    years: int = 5,
) -> list[dict]:
    """
    Annual Maintenance = annual_pct% of Development Cost.
    Returns list of dicts per year.
    """
    annual = round(development_cost * annual_pct / 100, 2)
    forecast = []
    for y in range(1, years + 1):
        forecast.append({
            "year": y,
            "annual_cost": annual,
            "cumulative_cost": round(annual * y, 2),
        })
    return forecast


def calculate_cumulative_maintenance(forecast: list[dict]) -> float:
    """Sum total maintenance cost across all forecast years."""
    if not forecast:
        return 0.0
    return forecast[-1]["cumulative_cost"]
