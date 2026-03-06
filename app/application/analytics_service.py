"""
Apeiron CostEstimation Pro – Analytics Service
===============================================
Use case: Variance analysis between estimated and actual costs.
Imports: Domain (variance_calculator) + Persistence (estimate_repository).
"""

from app.domain.variance_calculator import calculate_variance, classify_variance
from app.persistence.repositories.estimate_repository import EstimateRepository


class AnalyticsService:
    """Orchestrates variance analysis and project analytics."""

    def __init__(self, estimate_repo: EstimateRepository):
        self.estimate_repo = estimate_repo

    def get_variance(self, project_id: int) -> dict | None:
        """
        Calculate variance between estimated and actual costs.
        Returns None if no estimate exists.
        """
        est = self.estimate_repo.get_by_project(project_id)
        actual = self.estimate_repo.get_actual(project_id)
        if not est:
            return None
        result: dict[str, object] = {
            "estimated": float(est.final_price),
            "actual": float(actual.actual_cost) if actual else None,
            "variance": None,
        }
        if actual:
            result["variance"] = calculate_variance(float(est.final_price), float(actual.actual_cost))
        return result

    def save_actual(self, project_id: int, actual_cost: float, **kwargs) -> dict:
        """Save an actual cost for a project and return the variance."""
        actual = self.estimate_repo.save_actual(project_id, actual_cost, **kwargs)
        return {
            "id": actual.id,
            "project_id": actual.project_id,
            "actual_cost": actual.actual_cost,
        }
