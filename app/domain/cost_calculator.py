"""
Apeiron CostEstimation Pro – Cost Calculator (Domain)
=====================================================
Pure employee/labor cost calculations.
NO imports from persistence, application, or ui layers.
"""

from app.domain.constants import (
    WORKING_DAYS_PER_MONTH,
    WORKING_HOURS_PER_DAY,
    DEFAULT_PF_PCT,
    DEFAULT_BONUS_PCT,
    DEFAULT_LEAVE_PCT,
    DEFAULT_INFRA_PCT,
    DEFAULT_ADMIN_PCT,
)


def compute_hourly_from_salary(
    base_salary: float,
    pf_pct: float = DEFAULT_PF_PCT,
    bonus_pct: float = DEFAULT_BONUS_PCT,
    leave_pct: float = DEFAULT_LEAVE_PCT,
    infra_pct: float = DEFAULT_INFRA_PCT,
    admin_pct: float = DEFAULT_ADMIN_PCT,
) -> dict:
    """
    Standalone employee cost calculation without DB objects.

    Real Monthly = Base × (1 + total_pct/100)
    Hourly = Real Monthly / 22 / 8

    Returns dict with total_add_on_pct, real_monthly_cost, hourly_cost.
    """
    total_pct = pf_pct + bonus_pct + leave_pct + infra_pct + admin_pct
    real_monthly = round(base_salary * (1 + total_pct / 100), 2)
    hourly = round(real_monthly / WORKING_DAYS_PER_MONTH / WORKING_HOURS_PER_DAY, 2)
    return {
        "total_add_on_pct": total_pct,
        "real_monthly_cost": real_monthly,
        "hourly_cost": hourly,
    }


def calculate_module_cost(
    hourly_rate: float,
    estimated_hours: float,
    region_multiplier: float = 1.0,
) -> float:
    """
    Module cost = hourly_rate × estimated_hours × region_multiplier.
    Pure function – accepts plain values, not ORM objects.
    """
    return round(hourly_rate * estimated_hours * region_multiplier, 2)


def calculate_total_labor(
    module_costs: list[float],
    complexity_multiplier: float = 1.0,
    app_type_adjustment: float = 1.0,
) -> dict:
    """
    Total Labor Cost = Σ(module_cost) × complexity_mult × app_type_adj.
    Returns breakdown dict.
    """
    raw_total = sum(module_costs)
    adjusted_total = round(raw_total * complexity_multiplier * app_type_adjustment, 2)
    return {
        "raw_labor_total": round(raw_total, 2),
        "complexity_multiplier": complexity_multiplier,
        "app_type_adjustment": app_type_adjustment,
        "adjusted_labor_total": adjusted_total,
    }


def calculate_total_hours(hours_list: list[float]) -> float:
    """Sum of estimated hours across all modules."""
    return sum(hours_list)


def hours_to_person_months(hours: float) -> float:
    """Convert hours to person-months (22 days × 8 hours = 176)."""
    if hours <= 0:
        return 0.0
    return round(hours / (WORKING_DAYS_PER_MONTH * WORKING_HOURS_PER_DAY), 2)
