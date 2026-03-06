"""
Apeiron CostEstimation Pro – Estimation Calculator (Domain)
===========================================================
Full estimation pipeline: stage distribution, infra/stack,
risk/buffer, final pricing, analytics.
NO imports from persistence, application, or ui layers.
"""

from app.domain.constants import DEFAULT_STAGES


def calculate_stage_distribution(
    total_cost: float,
    planning_pct: float = 10.0,
    design_pct: float = 15.0,
    development_pct: float = 60.0,
    testing_pct: float = 10.0,
    deployment_pct: float = 5.0,
) -> dict:
    """
    Distribute total cost across project stages by percentage.
    Returns dict: stage_name → cost.
    """
    stages = {
        "Planning": planning_pct,
        "Design": design_pct,
        "Development": development_pct,
        "Testing": testing_pct,
        "Deployment": deployment_pct,
    }
    distribution = {}
    for stage, pct in stages.items():
        distribution[stage] = round(total_cost * pct / 100, 2)
    return distribution


def calculate_infra_stack_total(
    infra_costs: list[float],
    stack_costs: list[float],
) -> dict:
    """
    Sum all infra and stack costs.
    Accepts plain float lists, not ORM objects.
    """
    infra_total = sum(infra_costs)
    stack_total = sum(stack_costs)
    return {
        "infra_total": round(infra_total, 2),
        "stack_total": round(stack_total, 2),
        "combined_total": round(infra_total + stack_total, 2),
    }


def calculate_gross_cost(labor_total: float, infra_stack_total: float) -> float:
    """Gross cost = adjusted labor + infra + stack."""
    return round(labor_total + infra_stack_total, 2)


def calculate_risk_buffer(
    gross_cost: float,
    maintenance_buffer_pct: float = 15.0,
    risk_contingency_pct: float = 10.0,
) -> dict:
    """
    Safe Cost = Gross Cost + Maintenance Buffer + Risk Contingency.
    """
    maintenance_buffer = round(gross_cost * maintenance_buffer_pct / 100, 2)
    risk_contingency = round(gross_cost * risk_contingency_pct / 100, 2)
    safe_cost = round(gross_cost + maintenance_buffer + risk_contingency, 2)
    return {
        "gross_cost": gross_cost,
        "maintenance_buffer": maintenance_buffer,
        "risk_contingency": risk_contingency,
        "safe_cost": safe_cost,
    }


def calculate_final_price(safe_cost: float, profit_margin_pct: float = 20.0) -> dict:
    """
    Final Price = Safe Cost + Profit.
    """
    profit = round(safe_cost * profit_margin_pct / 100, 2)
    final = round(safe_cost + profit, 2)
    return {
        "safe_cost": safe_cost,
        "profit_amount": profit,
        "profit_margin_pct": profit_margin_pct,
        "final_price": final,
    }


def cost_per_function_point(total_cost: float, function_points: int) -> float:
    """Cost per function point. Returns 0 if no FPs."""
    if function_points <= 0:
        return 0.0
    return round(total_cost / function_points, 2)


def burn_rate_monthly(total_cost: float, duration_months: float) -> float:
    """Monthly burn rate = total / duration."""
    if duration_months <= 0:
        return 0.0
    return round(total_cost / duration_months, 2)


def revenue_margin(final_price: float, safe_cost: float) -> float:
    """Revenue Margin % = (Revenue - Cost) / Revenue × 100."""
    if final_price <= 0:
        return 0.0
    return round((final_price - safe_cost) / final_price * 100, 2)


def contribution_margin(final_price: float, variable_cost: float) -> float:
    """Contribution Margin = Final Price - Variable Cost."""
    return round(final_price - variable_cost, 2)
