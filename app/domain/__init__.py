"""
Apeiron CostEstimation Pro – Domain Layer
=========================================
Pure business logic: calculations, rules, algorithms.
NO imports from persistence, application, or UI layers.
"""

from app.domain.cost_calculator import (
    compute_hourly_from_salary,
    calculate_module_cost,
    calculate_total_labor,
    calculate_total_hours,
    hours_to_person_months,
)
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
from app.domain.variance_calculator import calculate_variance, classify_variance
from app.domain.maintenance_calculator import (
    calculate_maintenance_forecast,
    calculate_cumulative_maintenance,
)
