"""
Apeiron CostEstimation Pro – Employee Repository
=================================================
All database operations for Employee entities.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import Employee


class EmployeeRepository(BaseRepository):
    """Repository for Employee CRUD operations."""

    def create(self, name: str, role: str, base_salary: float, **overrides) -> Employee:
        """Create a new employee and recalculate costs."""
        emp = Employee(name=name, role=role, base_salary=base_salary, **overrides)
        self.session.add(emp)
        self.session.flush()  # apply column defaults before calculating
        emp.recalculate_costs()
        self.session.commit()
        return emp

    def get_by_id(self, emp_id: int) -> Employee | None:
        """Get employee by ID."""
        return self.session.query(Employee).filter_by(id=emp_id).first()

    def get_all(self, active_only: bool = True) -> list[Employee]:
        """Get all employees, optionally filtered by active status."""
        query = self.session.query(Employee)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    def update(self, emp_id: int, **kwargs) -> Employee | None:
        """Update employee fields and recalculate costs if salary-related."""
        emp = self.get_by_id(emp_id)
        if not emp:
            return None
        for key, val in kwargs.items():
            setattr(emp, key, val)
        emp.recalculate_costs()
        self.session.commit()
        return emp

    def delete(self, emp_id: int) -> bool:
        """Delete an employee by ID."""
        emp = self.get_by_id(emp_id)
        if not emp:
            return False
        self.session.delete(emp)
        self.session.commit()
        return True

    def get_roles(self) -> list[str]:
        """Get distinct employee roles."""
        results = self.session.query(Employee.role).distinct().all()
        return [r[0] for r in results]
