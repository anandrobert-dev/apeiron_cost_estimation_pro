"""
Apeiron CostEstimation Pro – Estimate Repository
=================================================
All database operations for Estimate, Actual, and MaintenanceRecord entities.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import Estimate, Actual, MaintenanceRecord


class EstimateRepository(BaseRepository):
    """Repository for Estimate CRUD operations."""

    def save_estimate(self, project_id: int, estimate_data: dict) -> Estimate:
        """Save or update an estimate for a project."""
        existing = self.get_by_project(project_id)
        if existing:
            for key, val in estimate_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, val)
            self.session.commit()
            return existing
        est = Estimate(project_id=project_id, **estimate_data)
        self.session.add(est)
        self.session.commit()
        return est

    def get_by_project(self, project_id: int) -> Estimate | None:
        """Get the estimate for a project."""
        return self.session.query(Estimate).filter_by(project_id=project_id).first()

    def save_maintenance_records(
        self, project_id: int, forecast: list[dict]
    ) -> list[MaintenanceRecord]:
        """Save maintenance forecast records for a project (replaces existing)."""
        # Delete existing records
        self.session.query(MaintenanceRecord).filter_by(project_id=project_id).delete()
        records = []
        for entry in forecast:
            rec = MaintenanceRecord(
                project_id=project_id,
                year=int(entry["year"]),
                annual_cost=float(entry["annual_cost"]),
            )
            self.session.add(rec)
            records.append(rec)
        self.session.commit()
        return records

    def save_actual(self, project_id: int, actual_cost: float, **kwargs) -> Actual:
        """Save or update actual cost for a project."""
        existing = self.get_actual(project_id)
        if existing:
            existing.actual_cost = float(actual_cost)  # type: ignore[assignment]
            for key, val in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, val)
            self.session.commit()
            return existing
        actual = Actual(project_id=project_id, actual_cost=float(actual_cost), **kwargs)
        self.session.add(actual)
        self.session.commit()
        return actual

    def get_actual(self, project_id: int) -> Actual | None:
        """Get the actual cost record for a project."""
        return self.session.query(Actual).filter_by(project_id=project_id).first()
