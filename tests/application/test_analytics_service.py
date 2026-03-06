"""
Tests for AnalyticsService.
"""

import pytest
from app.persistence.repositories.estimate_repository import EstimateRepository
from app.persistence.models import Project, Estimate
from app.application.analytics_service import AnalyticsService


class TestAnalyticsService:

    @pytest.fixture
    def service(self, db_session):
        # Seed a project and estimate
        proj = Project(name="AnalProj", status="active")
        db_session.add(proj)
        db_session.flush()

        est = Estimate(
            project_id=proj.id,
            total_labor_cost=50000.0,
            gross_cost=60000.0,
            safe_cost=75000.0,
            final_price=90000.0,
        )
        db_session.add(est)
        db_session.commit()

        repo = EstimateRepository(db_session)
        return AnalyticsService(repo), proj.id

    def test_get_variance_no_actual(self, service):
        svc, pid = service
        result = svc.get_variance(pid)
        assert result is not None
        assert result["estimated"] == 90000.0
        assert result["actual"] is None
        assert result["variance"] is None

    def test_save_actual_and_variance(self, service):
        svc, pid = service
        svc.save_actual(pid, 85000.0)
        result = svc.get_variance(pid)
        assert result["actual"] == 85000.0
        assert result["variance"] is not None
        assert "variance_pct" in result["variance"]

    def test_no_estimate(self, db_session):
        proj = Project(name="NoEstProj", status="draft")
        db_session.add(proj)
        db_session.commit()

        repo = EstimateRepository(db_session)
        svc = AnalyticsService(repo)
        assert svc.get_variance(proj.id) is None
