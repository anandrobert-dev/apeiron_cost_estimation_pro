---
name: Test Generator
description: Write comprehensive tests for PyQt6 desktop app following layer-by-layer strategy with AAA pattern
---

# Test Generator Skill - Desktop Edition

## Purpose

Generate robust, maintainable tests following the **AAA (Arrange-Act-Assert)** pattern. Test each layer independently using appropriate fixtures and test doubles.

**Strategy:** Test Domain (100%) → Persistence (80%+) → Application (80%+) → UI (50%+)

---

## When To Use

### ✅ USE for:
- Pure logic testing (Domain layer) - always
- Repository testing (Persistence) - with in-memory DB
- Service testing (Application) - with fake repos
- Component testing (UI) - integration level
- Edge case coverage
- Regression testing (before refactoring)

### ❌ DON'T:
- Test without clear AAA structure
- Mix test concerns (domain test shouldn't care about UI)
- Use real DB in every test (use in-memory for speed)
- Test implementation details (test behavior, not structure)

---

## Test Strategy by Layer

### Layer 1: Domain Tests (100% Coverage)

**Goal:** Every pure function tested, all paths covered

**Setup:**
```python
# tests/domain/test_cost_calculator.py
import pytest
from app.domain.cost_calculator import CostCalculator

# ❌ NO fixtures needed for Domain
# ❌ NO DB dependency
# ❌ NO mocks needed (pure functions)
```

**Pattern:**
```python
def test_calculate_module_cost_basic():
    # ARRANGE - Create instance, set inputs
    calc = CostCalculator()
    hourly_rate = 500.0
    hours = 40.0
    region_mult = 1.0
    
    # ACT - Call pure function
    result = calc.calculate_module_cost(hourly_rate, hours, region_mult)
    
    # ASSERT - Check output
    assert result == 20000.0
    assert isinstance(result, float)

def test_calculate_module_cost_with_region_multiplier():
    # ARRANGE
    calc = CostCalculator()
    
    # ACT
    result = calc.calculate_module_cost(500.0, 40.0, 1.2)
    
    # ASSERT
    assert result == 24000.0

def test_calculate_module_cost_edge_case_zero_hours():
    # ARRANGE
    calc = CostCalculator()
    
    # ACT
    result = calc.calculate_module_cost(500.0, 0, 1.0)
    
    # ASSERT
    assert result == 0.0

def test_calculate_module_cost_edge_case_invalid_input():
    # ARRANGE
    calc = CostCalculator()
    
    # ACT + ASSERT (using pytest)
    with pytest.raises(TypeError):
        calc.calculate_module_cost("not_a_number", 40.0, 1.0)
```

**Checklist:**
```
Domain Layer Tests:
□ Happy path (normal inputs)
□ Edge cases (zero, negative, max, min)
□ Type validation (wrong input types)
□ All code paths covered
□ No DB access needed
□ No fixtures needed
□ Pure functions only
```

---

### Layer 2: Persistence Tests (80%+ Coverage)

**Goal:** All CRUD operations work correctly with DB

**Setup in conftest.py:**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.persistence.models import Base

@pytest.fixture
def db_session():
    """In-memory SQLite for testing"""
    # Create in-memory DB
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
```

**Pattern:**
```python
# tests/persistence/test_employee_repository.py
import pytest
from app.persistence.repositories.employee_repository import EmployeeRepository
from app.persistence.models import Employee

def test_create_employee(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    
    # ACT
    emp = repo.create(
        name="John Doe",
        role="Developer",
        base_salary=100000
    )
    
    # ASSERT
    assert emp.id is not None
    assert emp.name == "John Doe"
    assert emp.base_salary == 100000

def test_get_employee_by_id(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    emp = repo.create("Jane Smith", "Manager", 150000)
    emp_id = emp.id
    
    # ACT
    fetched = repo.get_by_id(emp_id)
    
    # ASSERT
    assert fetched is not None
    assert fetched.name == "Jane Smith"

def test_get_employee_not_found(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    
    # ACT
    fetched = repo.get_by_id(999)
    
    # ASSERT
    assert fetched is None

def test_update_employee(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    emp = repo.create("Bob", "Dev", 100000)
    emp_id = emp.id
    
    # ACT
    updated = repo.update(emp_id, base_salary=120000)
    
    # ASSERT
    assert updated.base_salary == 120000

def test_delete_employee(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    emp = repo.create("Alice", "QA", 80000)
    emp_id = emp.id
    
    # ACT
    result = repo.delete(emp_id)
    fetched = repo.get_by_id(emp_id)
    
    # ASSERT
    assert result is True
    assert fetched is None

def test_get_all_employees(db_session):
    # ARRANGE
    repo = EmployeeRepository(db_session)
    repo.create("Emp1", "Dev", 100000)
    repo.create("Emp2", "QA", 80000)
    repo.create("Emp3", "Mgr", 150000)
    
    # ACT
    employees = repo.get_all()
    
    # ASSERT
    assert len(employees) == 3
```

**Checklist:**
```
Persistence Layer Tests:
□ Create (new records)
□ Read (by ID, all, filtered)
□ Update (field changes persist)
□ Delete (record removed)
□ Edge cases (duplicate key, not found, null fields)
□ Transactions (rollback on error)
□ In-memory DB used (fast, isolated)
□ No application logic tested (just data access)
```

---

### Layer 3: Application Tests (80%+ Coverage)

**Goal:** Services work correctly with fake repositories

**Setup in conftest.py:**
```python
# Continued in tests/conftest.py

@pytest.fixture
def fake_employee_repo():
    """Fake repository (no DB)"""
    class FakeEmployeeRepository:
        def __init__(self):
            self.employees = {}
            self.next_id = 1
        
        def create(self, name, role, salary):
            emp_id = self.next_id
            self.next_id += 1
            self.employees[emp_id] = {
                "id": emp_id,
                "name": name,
                "role": role,
                "base_salary": salary
            }
            return self.employees[emp_id]
        
        def get_by_id(self, emp_id):
            return self.employees.get(emp_id)
        
        def get_all(self):
            return list(self.employees.values())
    
    return FakeEmployeeRepository()
```

**Pattern:**
```python
# tests/application/test_employee_service.py
import pytest
from app.domain.cost_calculator import CostCalculator
from app.application.employee_service import EmployeeService

def test_create_employee_calculates_costs(fake_employee_repo):
    # ARRANGE
    calc = CostCalculator()
    service = EmployeeService(calc, fake_employee_repo)
    
    # ACT
    result = service.create_employee(
        name="John",
        role="Dev",
        base_salary=100000
    )
    
    # ASSERT
    assert result["name"] == "John"
    assert result["hourly_cost"] > 0

def test_list_all_employees(fake_employee_repo):
    # ARRANGE
    fake_employee_repo.create("Emp1", "Dev", 100000)
    fake_employee_repo.create("Emp2", "QA", 80000)
    calc = CostCalculator()
    service = EmployeeService(calc, fake_employee_repo)
    
    # ACT
    employees = service.get_all_employees()
    
    # ASSERT
    assert len(employees) == 2
    assert all("hourly_cost" in e for e in employees)

def test_service_returns_plain_dicts(fake_employee_repo):
    # ARRANGE
    calc = CostCalculator()
    service = EmployeeService(calc, fake_employee_repo)
    
    # ACT
    result = service.create_employee("John", "Dev", 100000)
    
    # ASSERT
    assert isinstance(result, dict)  # NOT ORM object
    assert "hourly_cost" in result
    assert "real_monthly_cost" in result

def test_service_handles_missing_employee(fake_employee_repo):
    # ARRANGE
    calc = CostCalculator()
    service = EmployeeService(calc, fake_employee_repo)
    
    # ACT + ASSERT
    with pytest.raises(ValueError):
        service.get_employee_with_costs(999)
```

**Checklist:**
```
Application Layer Tests:
□ All use cases tested
□ Services compose domain + persistence correctly
□ Returns plain dicts (not ORM)
□ Error handling (exceptions raised appropriately)
□ Dependency injection working (fakes accepted)
□ No direct DB calls (uses repos only)
□ Happy path + error paths
```

---

### Layer 4: UI Tests (50%+ Coverage)

**Goal:** Main workflows work, basic integration

**Pattern:**
```python
# tests/ui/test_estimation_tab.py
import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from app.ui.tabs.estimation_tab import EstimationTab
from app.application.estimation_service import EstimationService

@pytest.fixture  
def qapp():
    """QApplication needed for PyQt6 widgets"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_estimation_tab_renders(qapp, fake_estimation_service):
    # ARRANGE
    tab = EstimationTab(fake_estimation_service)
    
    # ACT
    tab.show()
    
    # ASSERT
    assert tab is not None
    assert tab.isVisible()

def test_estimate_button_calls_service(qapp, fake_estimation_service):
    # ARRANGE
    fake_estimation_service.estimate_project = MagicMock(
        return_value={"total_cost": 100000}
    )
    tab = EstimationTab(fake_estimation_service)
    tab.project_input.setText("1")
    
    # ACT
    tab._on_calculate()
    
    # ASSERT
    fake_estimation_service.estimate_project.assert_called_once()
    assert "100000" in tab.result_label.text()

def test_invalid_input_shows_error(qapp, fake_estimation_service):
    # ARRANGE
    tab = EstimationTab(fake_estimation_service)
    tab.project_input.setText("invalid")
    
    # ACT
    tab._on_calculate()
    
    # ASSERT
    assert "Error" in tab.result_label.text()
```

**Checklist:**
```
UI Layer Tests:
□ Main widgets render without crashing
□ Button clicks trigger actions
□ Error messages display
□ Service integration working
□ Use fakes for services (not real DB)
□ Minimal coverage (main workflows only)
```

---

## AAA Pattern (STRICT)

Every test MUST follow:

```python
def test_feature_name():
    # ===== ARRANGE (Setup) =====
    # Create objects, set initial state
    calc = CostCalculator()
    hours = 40
    rate = 500
    
    # ===== ACT (Execute) =====
    # Call the function/method being tested
    result = calc.calculate_cost(rate, hours)
    
    # ===== ASSERT (Verify) =====
    # Check that result is correct
    assert result == 20000
```

**Why this matters:**
- **Clear structure** – Reader immediately sees: setup → action → check
- **Easy to debug** – Fail on which part? Arrange/Act/Assert tells you
- **Reusable** – Can copy pattern for similar tests

---

## Test File Organization

```
tests/
├── conftest.py                    # Shared fixtures
│   ├── db_session fixture
│   ├── fake_repo fixtures
│   ├── qapp fixture (for PyQt6)
│   └── any shared test data
│
├── domain/
│   ├── test_cost_calculator.py
│   ├── test_estimation_calculator.py
│   └── test_variance_calculator.py
│
├── persistence/
│   ├── test_employee_repository.py
│   ├── test_project_repository.py
│   └── test_estimate_repository.py
│
├── application/
│   ├── test_employee_service.py
│   ├── test_estimation_service.py
│   └── test_export_service.py
│
└── ui/
    ├── test_estimation_tab.py
    └── test_components.py
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific layer
pytest tests/domain/ -v       # Fast! No DB
pytest tests/persistence/ -v  # Medium speed
pytest tests/application/ -v  # Medium speed
pytest tests/ui/ -v           # Slowest (GUI)

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run one test file
pytest tests/domain/test_cost_calculator.py -v

# Run one test
pytest tests/domain/test_cost_calculator.py::test_calculate_basic -v
```

---

## Coverage Targets

| Layer | Target | Why |
|-------|--------|-----|
| Domain | 100% | Pure functions, testable |
| Persist | 80%+ | DB interaction complex, edge cases matter |
| App | 80%+ | Use cases critical |
| UI | 50%+ | PyQt6 hard to test, focus on critical flows |

**Strategy:** Count lines of code and ensure coverage approaches targets.

```bash
pytest --cov=app --cov-report=term-missing

# Output shows which lines NOT covered
# Focus on Domain layer coverage first
```

---

## Common Testing Patterns

### Pattern 1: Testing Pure Domain Function

```python
@pytest.mark.parametrize("input,expected", [
    (10, 100),
    (20, 400),
    (0, 0),
    (-5, None),  # error case
])
def test_calculate_various_inputs(input, expected):
    calc = CostCalculator()
    if expected is None:
        with pytest.raises(ValueError):
            calc.calculate(input)
    else:
        assert calc.calculate(input) == expected
```

### Pattern 2: Testing Repository CRUD

```python
def test_repo_full_lifecycle(db_session):
    repo = EmployeeRepository(db_session)
    
    # CREATE
    emp = repo.create("John", "Dev", 100000)
    emp_id = emp.id
    
    # READ
    fetched = repo.get_by_id(emp_id)
    assert fetched.name == "John"
    
    # UPDATE
    updated = repo.update(emp_id, base_salary=120000)
    assert updated.base_salary == 120000
    
    # DELETE
    repo.delete(emp_id)
    assert repo.get_by_id(emp_id) is None
```

### Pattern 3: Testing Service Integration

```python
def test_service_orchestrates_correctly(fake_repo):
    svc = MyService(fake_repo, CostCalculator())
    
    # Arrange repo mock
    fake_repo.get_by_id = MagicMock(return_value={"id": 1, "cost": 1000})
    
    # Act
    result = svc.process_estimate(1)
    
    # Assert service called repo & calculator
    fake_repo.get_by_id.assert_called_once_with(1)
    assert result["final_cost"] > 0
```

---

## Integration with Workflow

This skill aligns with **TESTING phase** in orchestrator.md:

1. Generator completes code
2. Reviewer approves (no violations)
3. Test Generator writes comprehensive tests
4. **Goal:** 100% Domain, 80%+ Persist, 80%+ App, 50%+ UI coverage
5. All tests pass
6. Feature complete

**Success:** All tests pass + coverage targets met

---

## Example Output

```
================================ test session starts ==================================
platform linux -- Python 3.11.0, pytest-7.0.0, ...
collected 67 items

tests/domain/test_cost_calculator.py ................          [ 22%]
tests/persistence/test_employee_repository.py ......           [ 31%]
tests/application/test_employee_service.py ........             [ 42%]
tests/ui/test_estimation_tab.py ...                            [ 46%]

======================= 67 passed in 2.34s =======================

======================= Coverage Report =======================
Name                                      Stmts   Miss  Cover
------------------------------------------------------------
app/domain/cost_calculator.py                45      0   100%
app/persistence/repositories/employee.py    30      6    80%
app/application/employee_service.py         35      7    80%
app/ui/tabs/estimation_tab.py              50     25    50%
------------------------------------------------------------
TOTAL                                      160     38    76%
```

✅ **Coverage targets met** → Feature approved

