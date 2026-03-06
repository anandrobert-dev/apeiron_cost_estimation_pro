"""
Tests for ProjectService.
"""

import pytest
from app.persistence.repositories.project_repository import ProjectRepository
from app.persistence.repositories.audit_repository import AuditRepository
from app.application.project_service import ProjectService


class TestProjectService:

    @pytest.fixture
    def service(self, db_session):
        repo = ProjectRepository(db_session)
        audit = AuditRepository(db_session)
        return ProjectService(repo, audit)

    def test_create_project(self, service):
        result = service.create_project(name="TestProj", client_name="Client A")
        assert result["name"] == "TestProj"
        assert result["id"] is not None

    def test_get_project_with_modules(self, db_session, service):
        proj = service.create_project(name="WithModules")
        service.add_module(proj["id"], name="Auth", estimated_hours=40.0)
        service.add_module(proj["id"], name="Dashboard", estimated_hours=60.0)

        fetched = service.get_project(proj["id"])
        assert fetched is not None
        assert len(fetched["modules"]) == 2

    def test_get_all_projects(self, service):
        service.create_project(name="P1")
        service.create_project(name="P2")
        all_proj = service.get_all_projects()
        assert len(all_proj) == 2

    def test_update_project(self, service):
        proj = service.create_project(name="Original")
        updated = service.update_project(proj["id"], name="Updated")
        assert updated["name"] == "Updated"

    def test_delete_project(self, service):
        proj = service.create_project(name="ToDelete")
        assert service.delete_project(proj["id"]) is True
        assert service.get_project(proj["id"]) is None

    def test_module_crud(self, service):
        proj = service.create_project(name="ModProj")
        mod = service.add_module(proj["id"], name="API", estimated_hours=30.0)
        assert mod["name"] == "API"

        updated = service.update_module(mod["id"], estimated_hours=50.0)
        assert updated["estimated_hours"] == 50.0

        assert service.delete_module(mod["id"]) is True
