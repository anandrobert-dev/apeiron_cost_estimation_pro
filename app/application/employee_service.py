"""
Apeiron CostEstimation Pro – Employee Service
==============================================
Use case: CRUD employees with cost calculation.
Imports: Domain (cost_calculator) + Persistence (employee_repository, audit_repository).
"""

from app.domain.cost_calculator import compute_hourly_from_salary
from app.persistence.repositories.employee_repository import EmployeeRepository
from app.persistence.repositories.audit_repository import AuditRepository


class EmployeeService:
    """Orchestrates employee CRUD and cost calculation."""

    def __init__(self, repo: EmployeeRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit = audit_repo

    # ── READ ──
    def get_employee(self, emp_id: int) -> dict | None:
        emp = self.repo.get_by_id(emp_id)
        if not emp:
            return None
        return self._to_dict(emp)

    def get_all_employees(self, active_only: bool = True) -> list[dict]:
        employees = self.repo.get_all(active_only=active_only)
        return [self._to_dict(e) for e in employees]

    def get_roles(self) -> list[str]:
        return self.repo.get_roles()

    # ── CREATE ──
    def create_employee(
        self,
        name: str,
        role: str,
        base_salary: float,
        pf_pct: float = 12.0,
        bonus_pct: float = 8.33,
        leave_pct: float = 4.0,
        infra_pct: float = 5.0,
        admin_pct: float = 3.0,
    ) -> dict:
        emp = self.repo.create(
            name, role, base_salary,
            pf_pct=pf_pct, bonus_pct=bonus_pct, leave_pct=leave_pct,
            infra_pct=infra_pct, admin_pct=admin_pct,
        )
        self.audit.log("employees", int(emp.id), "CREATE")
        return self._to_dict(emp)

    # ── UPDATE ──
    def update_employee(self, emp_id: int, **kwargs) -> dict | None:
        emp = self.repo.update(emp_id, **kwargs)
        if not emp:
            return None
        self.audit.log("employees", emp_id, "UPDATE")
        return self._to_dict(emp)

    # ── DELETE ──
    def delete_employee(self, emp_id: int) -> bool:
        self.audit.log("employees", emp_id, "DELETE")
        return self.repo.delete(emp_id)

    # ── COST PREVIEW (no DB required) ──
    def preview_costs(
        self,
        base_salary: float,
        pf_pct: float = 12.0,
        bonus_pct: float = 8.33,
        leave_pct: float = 4.0,
        infra_pct: float = 5.0,
        admin_pct: float = 3.0,
    ) -> dict:
        """Pure domain calculation – no persistence side effects."""
        return compute_hourly_from_salary(
            base_salary, pf_pct, bonus_pct, leave_pct, infra_pct, admin_pct
        )

    # ── Helpers ──
    @staticmethod
    def _to_dict(emp) -> dict:
        return {
            "id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "base_salary": emp.base_salary,
            "pf_pct": emp.pf_pct,
            "bonus_pct": emp.bonus_pct,
            "leave_pct": emp.leave_pct,
            "infra_pct": emp.infra_pct,
            "admin_pct": emp.admin_pct,
            "real_monthly_cost": emp.real_monthly_cost,
            "hourly_cost": emp.hourly_cost,
            "is_active": emp.is_active,
        }
