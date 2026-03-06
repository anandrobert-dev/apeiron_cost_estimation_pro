"""
Apeiron CostEstimation Pro – Export Service
===========================================
Use case: Generate client-facing PDF proposals.
Imports: Persistence (estimate_repository, project_repository)
         + proposal_generator module.
"""

from app.persistence.repositories.project_repository import ProjectRepository
from app.persistence.repositories.estimate_repository import EstimateRepository
from app.utils.proposal_generator import generate_proposal_pdf
from app.utils.formatting import format_inr


class ExportService:
    """Orchestrates proposal PDF generation."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        estimate_repo: EstimateRepository,
    ):
        self.project_repo = project_repo
        self.estimate_repo = estimate_repo

    def generate_proposal(
        self,
        project_id: int,
        filepath: str,
        payment_terms: str = "",
        include_maintenance: bool = True,
        maintenance_years: int = 1,
    ) -> str:
        """Generate a PDF proposal for the given project. Returns filepath."""
        project = self.project_repo.get_with_modules(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        estimate = self.estimate_repo.get_by_project(project_id)
        if not estimate:
            raise ValueError(f"No estimation found for project {project_id}")

        # Build stage distribution from project percentages
        stage_distribution = {
            "Planning": estimate.gross_cost * project.stage_planning_pct / 100,
            "Design": estimate.gross_cost * project.stage_design_pct / 100,
            "Development": estimate.gross_cost * project.stage_development_pct / 100,
            "Testing": estimate.gross_cost * project.stage_testing_pct / 100,
            "Deployment": estimate.gross_cost * project.stage_deployment_pct / 100,
        }

        # Maintenance
        maint_records = project.maintenance_records
        maint_annual = maint_records[0].annual_cost if maint_records else 0

        return generate_proposal_pdf(
            filepath=filepath,
            project_name=str(project.name),
            client_name=str(project.client_name),
            app_type=str(project.app_type),
            complexity=str(project.complexity),
            description=str(project.description),
            timeline_months=float(project.estimated_duration_months),
            scope_modules=[str(m.name) for m in project.modules],
            final_price=float(estimate.final_price),
            stage_distribution=stage_distribution,
            maintenance_annual=float(maint_annual),
            maintenance_years=maintenance_years,
            payment_terms=payment_terms,
            include_maintenance=include_maintenance,
        )

    def get_proposal_preview(self, project_id: int) -> dict | None:
        """Return data for proposal preview (no PDF generation)."""
        project = self.project_repo.get_with_modules(project_id)
        if not project:
            return None
        estimate = self.estimate_repo.get_by_project(project_id)
        return {
            "project_name": str(project.name),
            "client_name": str(project.client_name),
            "app_type": str(project.app_type),
            "complexity": str(project.complexity),
            "description": str(project.description),
            "timeline_months": float(project.estimated_duration_months),
            "modules": [str(m.name) for m in project.modules],
            "final_price": float(estimate.final_price) if estimate else 0.0,
            "has_estimate": estimate is not None,
        }
