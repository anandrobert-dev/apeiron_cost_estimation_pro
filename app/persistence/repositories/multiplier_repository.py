"""
Apeiron CostEstimation Pro – Multiplier Repository
===================================================
All database operations for ComplexityMultiplier, AppTypeMultiplier,
and RegionMultiplier entities.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import (
    ComplexityMultiplier,
    AppTypeMultiplier,
    RegionMultiplier,
)


class MultiplierRepository(BaseRepository):
    """Repository for multiplier lookups and CRUD."""

    # ── Complexity ──
    def get_complexity_multiplier(self, name: str) -> float:
        """Get complexity multiplier value by name. Returns 1.0 if not found."""
        rec = self.session.query(ComplexityMultiplier).filter_by(name=name).first()
        return rec.multiplier if rec else 1.0

    def get_all_complexity(self) -> list[ComplexityMultiplier]:
        """Get all complexity multiplier records."""
        return self.session.query(ComplexityMultiplier).all()

    def upsert_complexity(self, name: str, multiplier: float) -> ComplexityMultiplier:
        """Create or update a complexity multiplier."""
        rec = self.session.query(ComplexityMultiplier).filter_by(name=name).first()
        if rec:
            rec.multiplier = multiplier
        else:
            rec = ComplexityMultiplier(name=name, multiplier=multiplier)
            self.session.add(rec)
        self.session.commit()
        return rec

    def delete_complexity(self, complexity_id: int) -> bool:
        """Delete a complexity multiplier by ID."""
        rec = self.session.query(ComplexityMultiplier).filter_by(id=complexity_id).first()
        if not rec:
            return False
        self.session.delete(rec)
        self.session.commit()
        return True

    # ── App Type ──
    def get_app_type_multiplier(self, name: str) -> float:
        """Get app type multiplier value by name. Returns 1.0 if not found."""
        rec = self.session.query(AppTypeMultiplier).filter_by(name=name).first()
        return rec.multiplier if rec else 1.0

    def get_all_app_types(self) -> list[AppTypeMultiplier]:
        """Get all app type multiplier records."""
        return self.session.query(AppTypeMultiplier).all()

    def upsert_app_type(self, name: str, multiplier: float) -> AppTypeMultiplier:
        """Create or update an app type multiplier."""
        rec = self.session.query(AppTypeMultiplier).filter_by(name=name).first()
        if rec:
            rec.multiplier = multiplier
        else:
            rec = AppTypeMultiplier(name=name, multiplier=multiplier)
            self.session.add(rec)
        self.session.commit()
        return rec

    def delete_app_type(self, app_type_id: int) -> bool:
        """Delete an app type multiplier by ID."""
        rec = self.session.query(AppTypeMultiplier).filter_by(id=app_type_id).first()
        if not rec:
            return False
        self.session.delete(rec)
        self.session.commit()
        return True

    # ── Region ──
    def get_region_multiplier(self, region_id: int) -> float:
        """Get region multiplier value by ID. Returns 1.0 if not found."""
        rec = self.session.query(RegionMultiplier).filter_by(id=region_id).first()
        return rec.multiplier if rec else 1.0

    def get_all_regions(self) -> list[RegionMultiplier]:
        """Get all region multiplier records."""
        return self.session.query(RegionMultiplier).all()
