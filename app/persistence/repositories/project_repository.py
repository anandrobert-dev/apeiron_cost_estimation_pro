"""
Apeiron CostEstimation Pro – Project Repository
================================================
All database operations for Project and ProjectModule entities.
"""

from sqlalchemy.orm import joinedload
from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import Project, ProjectModule, RegionMultiplier


class ProjectRepository(BaseRepository):
    """Repository for Project CRUD operations."""

    def create(self, **kwargs) -> Project:
        """Create a new project."""
        project = Project(**kwargs)
        self.session.add(project)
        self.session.commit()
        return project

    def get_by_id(self, project_id: int) -> Project | None:
        """Get project by ID."""
        return self.session.query(Project).filter_by(id=project_id).first()

    def get_with_modules(self, project_id: int) -> Project | None:
        """Get project with eagerly loaded modules."""
        return (
            self.session.query(Project)
            .options(joinedload(Project.modules))
            .filter_by(id=project_id)
            .first()
        )

    def get_all(self, status: str | None = None) -> list[Project]:
        """Get all projects, optionally filtered by status."""
        query = self.session.query(Project)
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def update(self, project_id: int, **kwargs) -> Project | None:
        """Update project fields."""
        project = self.get_by_id(project_id)
        if not project:
            return None
        for key, val in kwargs.items():
            setattr(project, key, val)
        self.session.commit()
        return project

    def delete(self, project_id: int) -> bool:
        """Delete a project by ID (cascades to modules, estimates, etc.)."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.session.delete(project)
        self.session.commit()
        return True

    def get_region_multiplier(self, region_id: int) -> float:
        """Get region multiplier value by region ID."""
        region = self.session.query(RegionMultiplier).filter_by(id=region_id).first()
        return region.multiplier if region else 1.0

    def add_module(self, project_id: int, **kwargs) -> ProjectModule:
        """Add a module to a project."""
        module = ProjectModule(project_id=project_id, **kwargs)
        self.session.add(module)
        self.session.commit()
        return module

    def update_module(self, module_id: int, **kwargs) -> ProjectModule | None:
        """Update a project module."""
        module = self.session.query(ProjectModule).filter_by(id=module_id).first()
        if not module:
            return None
        for key, val in kwargs.items():
            setattr(module, key, val)
        self.session.commit()
        return module

    def delete_module(self, module_id: int) -> bool:
        """Delete a project module by ID."""
        module = self.session.query(ProjectModule).filter_by(id=module_id).first()
        if not module:
            return False
        self.session.delete(module)
        self.session.commit()
        return True
