"""
Apeiron CostEstimation Pro – Estimation Service
================================================
Use case: Run a full cost estimation pipeline.
Imports: Domain (cost_calculator, estimation_calculator, maintenance_calculator)
         + Persistence (multiplier_repository, employee_repository).
"""

from app.domain.cost_calculator import (
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
)
from app.domain.maintenance_calculator import calculate_maintenance_forecast
from app.domain.constants import DEFAULT_STAGES
from app.persistence.repositories.multiplier_repository import MultiplierRepository


class EstimationService:
    """Orchestrates the full estimation pipeline."""

    def __init__(self, multiplier_repo: MultiplierRepository):
        self.multiplier_repo = multiplier_repo

    def run_estimation(
        self,
        modules: list[dict],
        complexity: str,
        app_type: str,
        region_multiplier: float,
        infra_costs: list[float],
        stack_costs: list[float],
        maintenance_buffer_pct: float,
        risk_contingency_pct: float,
        profit_margin_pct: float,
        stage_pcts: dict | None = None,
        function_points: int = 0,
        estimated_duration_months: float = 0.0,
        maintenance_years: int = 5,
        maintenance_annual_pct: float = 15.0,
    ) -> dict:
        """
        Run the complete estimation pipeline.

        Parameters
        ----------
        modules : list[dict]
            Each dict: {"name": str, "hourly_rate": float, "estimated_hours": float}
        complexity : str
            Complexity level name (e.g. "Medium").
        app_type : str
            App type name (e.g. "E-commerce").
        region_multiplier : float
            Region cost multiplier.
        infra_costs : list[float]
            List of individual infra cost values.
        stack_costs : list[float]
            List of individual stack cost values.
        """
        # 1. Module costs
        module_cost_details = []
        raw_costs = []
        for mod in modules:
            cost = calculate_module_cost(
                mod["hourly_rate"], mod["estimated_hours"], region_multiplier
            )
            module_cost_details.append({
                "name": mod["name"],
                "hours": mod["estimated_hours"],
                "cost": cost,
            })
            raw_costs.append(cost)

        # 2. Multipliers from DB
        cx_mult = self.multiplier_repo.get_complexity_multiplier(complexity)
        app_adj = self.multiplier_repo.get_app_type_multiplier(app_type)

        # 3. Labor
        labor = calculate_total_labor(raw_costs, cx_mult, app_adj)

        # 4. Infra + Stack
        infra_stack = calculate_infra_stack_total(infra_costs, stack_costs)

        # 5. Gross cost
        gross = calculate_gross_cost(labor["adjusted_labor_total"], infra_stack["combined_total"])

        # 6. Risk buffer
        risk = calculate_risk_buffer(gross, maintenance_buffer_pct, risk_contingency_pct)

        # 7. Final price
        final = calculate_final_price(risk["safe_cost"], profit_margin_pct)

        # 8. Stage distribution
        sp = stage_pcts or DEFAULT_STAGES
        stages = calculate_stage_distribution(
            labor["adjusted_labor_total"],
            sp.get("Planning", 10),
            sp.get("Design", 15),
            sp.get("Development", 60),
            sp.get("Testing", 10),
            sp.get("Deployment", 5),
        )

        # 9. Maintenance
        dev_cost = stages.get("Development", 0)
        maintenance = calculate_maintenance_forecast(
            dev_cost, maintenance_annual_pct, maintenance_years
        )

        # 10. Analytics
        hours_list = [m["estimated_hours"] for m in modules]
        total_hours = calculate_total_hours(hours_list)
        pm = hours_to_person_months(total_hours)
        cpfp = cost_per_function_point(final["final_price"], function_points)
        br = burn_rate_monthly(final["final_price"], estimated_duration_months)
        rm = revenue_margin(final["final_price"], risk["safe_cost"])

        return {
            "labor": {
                "module_costs": module_cost_details,
                "raw_labor_total": labor["raw_labor_total"],
                "complexity_multiplier": cx_mult,
                "app_type_adjustment": app_adj,
                "adjusted_labor_total": labor["adjusted_labor_total"],
            },
            "infra_stack": infra_stack,
            "gross_cost": gross,
            "risk_buffer": risk,
            "final_pricing": final,
            "stage_distribution": stages,
            "maintenance_forecast": maintenance,
            "analytics": {
                "total_hours": total_hours,
                "person_months": pm,
                "cost_per_function_point": cpfp,
                "burn_rate_monthly": br,
                "revenue_margin_pct": rm,
            },
        }
