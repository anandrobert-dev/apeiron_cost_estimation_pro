"""
Apeiron CostEstimation Pro – Project Service
=============================================
Use case: CRUD projects and modules.
Imports: Persistence (project_repository, audit_repository).
"""

from app.persistence.repositories.project_repository import ProjectRepository
from app.persistence.repositories.audit_repository import AuditRepository


class ProjectService:
    """Orchestrates project and module CRUD."""

    def __init__(self, repo: ProjectRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit = audit_repo

    # ── Projects ──
    def create_project(self, **kwargs) -> dict:
        proj = self.repo.create(**kwargs)
        self.audit.log("projects", int(proj.id), "CREATE")
        return self._proj_to_dict(proj)

    def get_project(self, project_id: int) -> dict | None:
        proj = self.repo.get_with_modules(project_id)
        if not proj:
            return None
        return self._proj_to_dict(proj, include_modules=True)

    def get_all_projects(self, status: str | None = None) -> list[dict]:
        projects = self.repo.get_all(status=status)
        return [self._proj_to_dict(p) for p in projects]

    def update_project(self, project_id: int, **kwargs) -> dict | None:
        proj = self.repo.update(project_id, **kwargs)
        if not proj:
            return None
        self.audit.log("projects", project_id, "UPDATE")
        return self._proj_to_dict(proj)

    def delete_project(self, project_id: int) -> bool:
        self.audit.log("projects", project_id, "DELETE")
        return self.repo.delete(project_id)

    # ── Modules ──
    def add_module(self, project_id: int, **kwargs) -> dict:
        mod = self.repo.add_module(project_id, **kwargs)
        return self._mod_to_dict(mod)

    def update_module(self, module_id: int, **kwargs) -> dict | None:
        mod = self.repo.update_module(module_id, **kwargs)
        if not mod:
            return None
        return self._mod_to_dict(mod)

    def delete_module(self, module_id: int) -> bool:
        return self.repo.delete_module(module_id)

    # ── Region ──
    def get_region_multiplier(self, region_id: int) -> float:
        return self.repo.get_region_multiplier(region_id)

    # ── Helpers ──
    @staticmethod
    def _proj_to_dict(proj, include_modules: bool = False) -> dict:
        d = {
            "id": int(proj.id),
            "name": str(proj.name),
            "client_name": str(proj.client_name),
            "description": str(proj.description),
            "app_type": str(proj.app_type),
            "complexity": str(proj.complexity),
            "estimated_loc": int(proj.estimated_loc),
            "function_points": int(proj.function_points),
            "region_id": int(proj.region_id) if proj.region_id else None,
            "stage_planning_pct": proj.stage_planning_pct,
            "stage_design_pct": proj.stage_design_pct,
            "stage_development_pct": proj.stage_development_pct,
            "stage_testing_pct": proj.stage_testing_pct,
            "stage_deployment_pct": proj.stage_deployment_pct,
            "maintenance_buffer_pct": proj.maintenance_buffer_pct,
            "risk_contingency_pct": proj.risk_contingency_pct,
            "profit_margin_pct": proj.profit_margin_pct,
            "estimated_duration_months": proj.estimated_duration_months,
            "status": proj.status,
        }
        if include_modules:
            d["modules"] = [ProjectService._mod_to_dict(m) for m in (proj.modules or [])]
        return d

    @staticmethod
    def _mod_to_dict(mod) -> dict:
        return {
            "id": mod.id,
            "project_id": mod.project_id,
            "name": mod.name,
            "description": mod.description,
            "employee_id": mod.employee_id,
            "estimated_hours": mod.estimated_hours,
            "hourly_rate_override": mod.hourly_rate_override,
            "cost": mod.cost,
        }
