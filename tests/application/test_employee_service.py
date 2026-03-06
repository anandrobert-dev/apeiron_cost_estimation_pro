"""
Tests for EmployeeService.
"""

import pytest
from app.persistence.repositories.employee_repository import EmployeeRepository
from app.persistence.repositories.audit_repository import AuditRepository
from app.application.employee_service import EmployeeService


class TestEmployeeService:

    @pytest.fixture
    def service(self, db_session):
        repo = EmployeeRepository(db_session)
        audit = AuditRepository(db_session)
        return EmployeeService(repo, audit)

    def test_create_and_get(self, service):
        result = service.create_employee("Alice", "Developer", 100_000.0)
        assert result["name"] == "Alice"
        assert result["role"] == "Developer"
        assert result["hourly_cost"] > 0
        assert result["id"] is not None

        fetched = service.get_employee(result["id"])
        assert fetched is not None
        assert fetched["name"] == "Alice"

    def test_get_all(self, service):
        service.create_employee("A", "Dev", 50_000.0)
        service.create_employee("B", "QA", 60_000.0)
        all_emps = service.get_all_employees()
        assert len(all_emps) == 2

    def test_update(self, service):
        result = service.create_employee("Bob", "Dev", 80_000.0)
        originally = result["hourly_cost"]
        updated = service.update_employee(result["id"], base_salary=120_000.0)
        assert updated is not None
        assert updated["hourly_cost"] > originally

    def test_delete(self, service):
        result = service.create_employee("Charlie", "QA", 70_000.0)
        assert service.delete_employee(result["id"]) is True
        assert service.get_employee(result["id"]) is None

    def test_preview_costs(self, service):
        preview = service.preview_costs(100_000.0)
        assert "hourly_cost" in preview
        assert "real_monthly_cost" in preview
        assert preview["hourly_cost"] > 0

    def test_audit_trail(self, db_session, service):
        result = service.create_employee("Audited", "Dev", 90_000.0)
        from app.persistence.repositories.audit_repository import AuditRepository
        audit = AuditRepository(db_session)
        logs = audit.get_for_record("employees", result["id"])
        assert len(logs) >= 1
        assert logs[0].action == "CREATE"
