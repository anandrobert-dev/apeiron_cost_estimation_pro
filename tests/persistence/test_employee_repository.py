"""
Tests for EmployeeRepository.
"""

import pytest
from app.persistence.repositories.employee_repository import EmployeeRepository


class TestEmployeeRepository:

    def test_create_employee(self, db_session):
        repo = EmployeeRepository(db_session)
        emp = repo.create("Alice", "Developer", 100_000.0)
        assert emp.id is not None
        assert emp.name == "Alice"
        assert emp.role == "Developer"
        assert emp.base_salary == 100_000.0
        # recalculate_costs should have been called
        assert emp.real_monthly_cost > 0
        assert emp.hourly_cost > 0

    def test_get_by_id(self, db_session):
        repo = EmployeeRepository(db_session)
        emp = repo.create("Bob", "QA", 80_000.0)
        found = repo.get_by_id(emp.id)
        assert found is not None
        assert found.name == "Bob"

    def test_get_by_id_not_found(self, db_session):
        repo = EmployeeRepository(db_session)
        assert repo.get_by_id(9999) is None

    def test_get_all_active_only(self, db_session):
        repo = EmployeeRepository(db_session)
        repo.create("Active1", "Dev", 50_000.0)
        repo.create("Active2", "QA", 60_000.0)
        emp3 = repo.create("Inactive", "PM", 70_000.0)
        emp3.is_active = False
        db_session.commit()

        active = repo.get_all(active_only=True)
        assert len(active) == 2
        all_emps = repo.get_all(active_only=False)
        assert len(all_emps) == 3

    def test_update_employee(self, db_session):
        repo = EmployeeRepository(db_session)
        emp = repo.create("Charlie", "Dev", 90_000.0)
        old_hourly = emp.hourly_cost

        updated = repo.update(emp.id, base_salary=120_000.0)
        assert updated is not None
        assert updated.base_salary == 120_000.0
        assert updated.hourly_cost > old_hourly

    def test_update_nonexistent(self, db_session):
        repo = EmployeeRepository(db_session)
        assert repo.update(9999, base_salary=50_000.0) is None

    def test_delete_employee(self, db_session):
        repo = EmployeeRepository(db_session)
        emp = repo.create("ToDelete", "QA", 60_000.0)
        assert repo.delete(emp.id) is True
        assert repo.get_by_id(emp.id) is None

    def test_delete_nonexistent(self, db_session):
        repo = EmployeeRepository(db_session)
        assert repo.delete(9999) is False

    def test_get_roles(self, db_session):
        repo = EmployeeRepository(db_session)
        repo.create("A", "Developer", 50_000.0)
        repo.create("B", "QA", 60_000.0)
        repo.create("C", "Developer", 70_000.0)
        roles = repo.get_roles()
        assert set(roles) == {"Developer", "QA"}
