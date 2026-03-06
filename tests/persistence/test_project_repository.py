"""
Tests for ProjectRepository.
"""

import pytest
from app.persistence.models import RegionMultiplier
from app.persistence.repositories.project_repository import ProjectRepository


class TestProjectRepository:

    def test_create_project(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="TestProject", client_name="Client A")
        assert proj.id is not None
        assert proj.name == "TestProject"

    def test_get_by_id(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="Proj1")
        found = repo.get_by_id(proj.id)
        assert found is not None
        assert found.name == "Proj1"

    def test_get_all(self, db_session):
        repo = ProjectRepository(db_session)
        repo.create(name="P1", status="draft")
        repo.create(name="P2", status="active")
        repo.create(name="P3", status="draft")

        assert len(repo.get_all()) == 3
        assert len(repo.get_all(status="draft")) == 2
        assert len(repo.get_all(status="active")) == 1

    def test_update_project(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="Original")
        updated = repo.update(proj.id, name="Updated", complexity="Complex")
        assert updated.name == "Updated"
        assert updated.complexity == "Complex"

    def test_delete_project(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="ToDelete")
        assert repo.delete(proj.id) is True
        assert repo.get_by_id(proj.id) is None

    def test_add_module(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="WithModules")
        mod = repo.add_module(proj.id, name="Auth Module", estimated_hours=40.0)
        assert mod.id is not None
        assert mod.project_id == proj.id

    def test_update_module(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="ModProj")
        mod = repo.add_module(proj.id, name="UI Module", estimated_hours=20.0)
        updated = repo.update_module(mod.id, estimated_hours=30.0)
        assert updated.estimated_hours == 30.0

    def test_delete_module(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="DelModProj")
        mod = repo.add_module(proj.id, name="Temp Module")
        assert repo.delete_module(mod.id) is True
        assert repo.delete_module(mod.id) is False

    def test_get_region_multiplier(self, db_session):
        region = RegionMultiplier(region_name="India", multiplier=1.0)
        db_session.add(region)
        db_session.commit()

        repo = ProjectRepository(db_session)
        assert repo.get_region_multiplier(region.id) == 1.0
        assert repo.get_region_multiplier(9999) == 1.0  # default

    def test_get_with_modules(self, db_session):
        repo = ProjectRepository(db_session)
        proj = repo.create(name="EagerProj")
        repo.add_module(proj.id, name="Mod1", estimated_hours=10.0)
        repo.add_module(proj.id, name="Mod2", estimated_hours=20.0)

        loaded = repo.get_with_modules(proj.id)
        assert loaded is not None
        assert len(loaded.modules) == 2
