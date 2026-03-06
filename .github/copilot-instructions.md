# Apeiron CostEstimation Pro - Copilot Architecture Instructions

**Project Version:** 2.0.0 (Refactoring to Clean Architecture)  
**Date Created:** March 4, 2026  
**Target Audience:** AI pair programmers + Human developers (6+ months Python experience)

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Layer Responsibilities](#layer-responsibilities)
4. [Dependencies & Imports](#dependencies--imports)
5. [Naming Conventions](#naming-conventions)
6. [Code Examples](#code-examples)
7. [Anti-Patterns (What NOT To Do)](#anti-patterns-what-not-to-do)
8. [Testing Strategy](#testing-strategy)
9. [Migration Phases](#migration-phases)

---

## ARCHITECTURE OVERVIEW

### Core Principle
**Clear separation of concerns** across 4 independent layers:

```
┌─────────────────────────────────────────────────────────┐
│           PRESENTATION LAYER (UI)                       │
│        PyQt6 - Display, Events, User Interaction         │
│   IMPORTS FROM: Application Layer ONLY                  │
│   RESPONSIBILITIES: Render UI, handle clicks, display   │
└────────────────────────┬────────────────────────────────┘
                         │ (uses)
┌────────────────────────▼────────────────────────────────┐
│          APPLICATION LAYER (Services)                   │
│      Orchestration, Workflow, Business Rules            │
│   IMPORTS FROM: Domain + Persistence layers             │
│   RESPONSIBILITIES: Compose logic, handle use cases     │
└────────────────────────┬────────────────────────────────┘
                         │ (uses)
       ┌─────────────────┴─────────────────┐
       │                                   │
┌──────▼──────────────┐          ┌────────▼──────────────┐
│   DOMAIN LAYER      │          │ PERSISTENCE LAYER    │
│  (Pure Logic)       │          │   (Data Access)      │
│                     │          │                      │
│ IMPORTS FROM:       │          │ IMPORTS FROM:        │
│ NONE (pure Python)  │          │ Domain only          │
│                     │          │                      │
│ RESPONSIBILITIES:   │          │ RESPONSIBILITIES:    │
│ - Calculations      │          │ - DB queries         │
│ - Rules             │          │ - CRUD operations    │
│ - Algorithms        │          │ - Repository pattern │
└─────────────────────┘          └────────────────────────┘
```

**CRITICAL RULE:**
```
UI  ────X────→  Domain  (UI CANNOT import Domain)
 ↓                ↑
App  ←────→  Persistence
 │                │
 └────────┬───────┘
          │
      Both import Domain & Persistence
```

---

## FOLDER STRUCTURE

```
apeiron_cost_estimation_pro/
│
├── app/
│   ├── __init__.py                      # Version, metadata
│   │
│   ├── domain/                          # ⭐ PURE BUSINESS LOGIC
│   │   ├── __init__.py
│   │   ├── cost_calculator.py           # Cost math: module_cost, labor_cost, etc.
│   │   ├── estimation_calculator.py     # Full estimation: cost + risk + stages
│   │   ├── variance_calculator.py       # Variance & analytics
│   │   ├── maintenance_calculator.py    # Maintenance forecasting
│   │   ├── constants.py                 # Constants, defaults, thresholds
│   │   └── models.py                    # Domain value objects (NOT ORM)
│   │
│   ├── persistence/                     # ⭐ DATA ACCESS LAYER
│   │   ├── __init__.py
│   │   ├── database.py                  # SQLite engine, session factory
│   │   ├── models.py                    # SQLAlchemy ORM models (EXISTING)
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base_repository.py       # Abstract base + common CRUD
│   │       ├── employee_repository.py   # Employee queries
│   │       ├── project_repository.py    # Project queries
│   │       ├── estimate_repository.py   # Estimate queries
│   │       ├── multiplier_repository.py # Complexity, AppType multipliers
│   │       ├── preset_repository.py     # Industry presets
│   │       └── audit_repository.py      # Audit logs
│   │
│   ├── application/                     # ⭐ ORCHESTRATION LAYER
│   │   ├── __init__.py
│   │   ├── estimation_service.py        # Use case: Run full estimation
│   │   ├── employee_service.py          # Use case: CRUD employees
│   │   ├── project_service.py           # Use case: CRUD projects
│   │   ├── export_service.py            # Use case: Generate PDF proposal
│   │   ├── analytics_service.py         # Use case: Calculate analytics
│   │   ├── pricing_service.py           # Use case: Apply pricing strategies
│   │   └── base_service.py              # Common service patterns
│   │
│   ├── ui/                              # ⭐ PRESENTATION LAYER
│   │   ├── __init__.py
│   │   ├── main_window.py               # Main window (ONLY setup & wiring)
│   │   ├── tabs/
│   │   │   ├── __init__.py
│   │   │   ├── base_tab.py              # Common tab patterns
│   │   │   ├── master_data_tab.py       # Master data management
│   │   │   ├── estimation_tab.py        # Run estimations
│   │   │   ├── analysis_tab.py          # View analytics
│   │   │   └── proposal_tab.py          # Export proposals
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── forms/
│   │   │   │   ├── employee_form.py     # Employee CRUD widget
│   │   │   │   ├── project_form.py      # Project CRUD widget
│   │   │   │   └── module_form.py       # Module CRUD widget
│   │   │   ├── tables/
│   │   │   │   ├── employee_table.py
│   │   │   │   ├── project_table.py
│   │   │   │   └── estimate_table.py
│   │   │   ├── cards.py                 # Card widgets (stats display)
│   │   │   ├── dialogs.py               # Common dialogs
│   │   │   └── charts.py                # Chart widgets (matplotlib)
│   │   └── style/
│   │       ├── __init__.py
│   │       ├── theme.py                 # Theme definitions (colors, fonts)
│   │       └── stylesheet.py            # Stylesheet generation
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatting.py                # format_inr(), format_percentage()
│       ├── validators.py                # Input validation
│       └── exceptions.py                # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures (fake DB, services)
│   ├── domain/
│   │   ├── test_cost_calculator.py
│   │   ├── test_estimation_calculator.py
│   │   ├── test_variance_calculator.py
│   │   └── test_maintenance_calculator.py
│   ├── application/
│   │   ├── test_estimation_service.py
│   │   ├── test_employee_service.py
│   │   ├── test_project_service.py
│   │   ├── test_export_service.py
│   │   └── test_analytics_service.py
│   ├── persistence/
│   │   ├── test_employee_repository.py
│   │   ├── test_project_repository.py
│   │   └── test_multiplier_repository.py
│   └── ui/
│       ├── test_main_window.py          # Minimal UI tests
│       └── test_components.py           # Component tests
│
├── run.py                               # Entry point
├── requirements.txt                     # Dependencies
├── .copilot-instructions.md             # THIS FILE
└── README.md                            # Project overview

```

---

## LAYER RESPONSIBILITIES

### 1️⃣ DOMAIN LAYER (`app/domain/`)

**PURPOSE:** Pure business logic with ZERO external dependencies

**Characteristics:**
- ✅ Pure Python functions & classes
- ✅ No imports from other app layers
- ✅ No database access
- ✅ No UI imports
- ✅ 100% testable in isolation
- ✅ Easily reusable (CLI, Web, API later)

**Examples of code that belongs here:**
```python
# ✅ GOOD - Pure math
def calculate_module_cost(hourly_rate: float, hours: float, region_mult: float) -> float:
    return hourly_rate * hours * region_mult

# ✅ GOOD - Pure logic
def apply_risk_buffer(cost: float, risk_pct: float) -> float:
    return cost * (1 + risk_pct / 100)

# ✅ GOOD - Pure formula
def convert_hours_to_person_months(hours: float) -> float:
    return hours / 176  # 22 days * 8 hours
```

**Examples that DO NOT belong here:**
```python
# ❌ BAD - Database dependency
from app.persistence.models import Employee

# ❌ BAD - UI dependency
from PyQt6.QtWidgets import QMainWindow

# ❌ BAD - Session dependency
def calculate_cost(session):  # ← Takes DB session
    employee = session.query(Employee)...
```

**Interface Pattern:**
```python
# Always accept parameters, NEVER fetch from outside
class CostCalculator:
    def calculate_total_labor(
        self,
        module_costs: list,          # ← Parameters (not from DB)
        complexity_multiplier: float, # ← Parameters (not from DB)
        app_type_adjustment: float    # ← Parameters (not from DB)
    ) -> float:
        """Calculate cost from inputs"""
        return sum(module_costs) * complexity_multiplier * app_type_adjustment
```

---

### 2️⃣ PERSISTENCE LAYER (`app/persistence/`)

**PURPOSE:** All database operations encapsulated behind repositories

**Characteristics:**
- ✅ DB access ONLY here
- ✅ SQLAlchemy ORM models (existing `models.py`)
- ✅ Repository pattern for each entity
- ✅ CRUD methods (Create, Read, Update, Delete)
- ✅ Can import Domain layer
- ❌ CANNOT import Application or UI

**Repository Example:**
```python
# app/persistence/repositories/employee_repository.py

from app.persistence.models import Employee

class EmployeeRepository:
    def __init__(self, session):
        self.session = session
    
    # CREATE
    def create(self, name: str, role: str, base_salary: float) -> Employee:
        emp = Employee(name=name, role=role, base_salary=base_salary)
        self.session.add(emp)
        self.session.commit()
        return emp
    
    # READ
    def get_by_id(self, emp_id: int) -> Employee:
        return self.session.query(Employee).filter_by(id=emp_id).first()
    
    def get_all(self) -> list[Employee]:
        return self.session.query(Employee).all()
    
    # UPDATE
    def update(self, emp_id: int, **kwargs) -> Employee:
        emp = self.get_by_id(emp_id)
        for key, val in kwargs.items():
            setattr(emp, key, val)
        self.session.commit()
        return emp
    
    # DELETE
    def delete(self, emp_id: int) -> bool:
        emp = self.get_by_id(emp_id)
        self.session.delete(emp)
        self.session.commit()
        return True
```

**Key Principle:**
```
Repository = The ONLY place where you write SQL/ORM queries
All session.query() calls should be INSIDE repositories
```

---

### 3️⃣ APPLICATION LAYER (`app/application/`)

**PURPOSE:** Orchestrate domain logic + persistence to fulfill use cases

**Characteristics:**
- ✅ Imports Domain + Persistence
- ✅ No UI logic
- ✅ Stateless (pure functions preferred)
- ✅ Accepts plain Python data (dicts, lists, floats)
- ✅ Returns plain Python data
- ❌ CANNOT import UI

**Service Example:**
```python
# app/application/estimation_service.py

from app.domain.cost_calculator import CostCalculator
from app.domain.estimation_calculator import EstimationCalculator
from app.persistence.repositories.multiplier_repository import MultiplierRepository
from app.persistence.repositories.project_repository import ProjectRepository

class EstimationService:
    """Use case: Run a full cost estimation"""
    
    def __init__(
        self,
        cost_calc: CostCalculator,
        estimation_calc: EstimationCalculator,
        multiplier_repo: MultiplierRepository,
        project_repo: ProjectRepository
    ):
        self.cost_calc = cost_calc
        self.estimation_calc = estimation_calc
        self.multiplier_repo = multiplier_repo
        self.project_repo = project_repo
    
    def estimate_project(self, project_id: int) -> dict:
        """
        Workflow:
        1. Load project from DB (via repo)
        2. Load multipliers from DB (via repo)
        3. Calculate using domain logic
        4. Return result
        """
        # Step 1: Get data from persistence
        project = self.project_repo.get_with_modules(project_id)
        cx_mult = self.multiplier_repo.get_complexity_multiplier(project.complexity)
        app_adj = self.multiplier_repo.get_app_type_adjustment(project.app_type)
        
        # Step 2: Transform to domain inputs
        module_costs = [self.cost_calc.calculate_module_cost(m) for m in project.modules]
        
        # Step 3: Use domain calculators
        adjusted_labor = self.cost_calc.calculate_total_labor(
            module_costs, cx_mult, app_adj
        )
        
        total_cost = self.estimation_calc.calculate_total_cost(
            labor=adjusted_labor,
            infra=project.infra_cost,
            stack=project.stack_cost
        )
        
        # Step 4: Return (NOT ORM objects, just dicts)
        return {
            "project_id": project.id,
            "modules": [{"name": m.name, "cost": m.cost} for m in project.modules],
            "complexity_multiplier": cx_mult,
            "adjusted_labor": adjusted_labor,
            "total_cost": total_cost
        }
```

**Key Principle:**
```
Service = Bridge between UI needs and backend capabilities
- ✅ Accepts UI-friendly inputs (plain dicts)
- ✅ Returns UI-friendly outputs (plain dicts)
- ✅ All heavy lifting from Domain
- ✅ All data fetching from Persistence
```

---

### 4️⃣ PRESENTATION LAYER (`app/ui/`)

**PURPOSE:** Display data + handle user interaction

**Characteristics:**
- ✅ PyQt6 widgets ONLY
- ✅ Imports Application layer ONLY
- ✅ No business logic
- ✅ No database queries
- ✅ Event handlers are thin (read UI → call service → display result)
- ❌ CANNOT import Domain or Persistence

**UI Example:**
```python
# app/ui/tabs/estimation_tab.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel
from app.application.estimation_service import EstimationService

class EstimationTab(QWidget):
    """UI for running estimations"""
    
    def __init__(self, service: EstimationService):  # ← Dependency Injection!
        super().__init__()
        self.service = service  # ← Store service
        self._setup_ui()
    
    def _setup_ui(self):
        """Build UI - NO LOGIC HERE"""
        layout = QVBoxLayout(self)
        
        self.project_input = QLineEdit()
        self.result_label = QLabel()
        
        btn = QPushButton("Calculate Estimate")
        btn.clicked.connect(self._on_calculate)  # ← Event handler
        
        layout.addWidget(self.project_input)
        layout.addWidget(btn)
        layout.addWidget(self.result_label)
    
    def _on_calculate(self):
        """Handle button click - THIN event handler"""
        # Step 1: Read from UI
        project_id = int(self.project_input.text())
        
        # Step 2: Call service (ALL LOGIC HAPPENS HERE)
        try:
            result = self.service.estimate_project(project_id)
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            return
        
        # Step 3: Display result (UI ONLY)
        self.result_label.setText(f"Total: ₹{result['total_cost']}")
    
    # ❌ NEVER DO THIS:
    # def _on_calculate(self):
    #     project = self.session.query(Project)...  # ❌ DB access
    #     cost = my_calculation_function()...       # ❌ Business logic
    #     self._refresh_ui()                        # ❌ Manual refresh
```

**Key Principle:**
```
UI = Dumb display layer
- Event handler reads UI → calls service → displays result
- Service does ALL the work (logic + data access)
- Never touch databases, never do calculations
```

---

## DEPENDENCIES & IMPORTS

### Import Rules (CRITICAL ⚠️)

```python
# ✅ ALLOWED IMPORTS

# From Domain → NOWHERE
from app.domain.cost_calculator import CostCalculator

# From Persistence → Application, Persistence
from app.persistence.repositories.employee_repository import EmployeeRepository

# From Application → UI, Application
from app.application.estimation_service import EstimationService

# From UI → UI, Application (ONLY)
from app.ui.components.cards import StatCard
from app.application.estimation_service import EstimationService


# ❌ FORBIDDEN IMPORTS

# Domain should never import (except stdlib + maybe numpy/math)
from app.persistence import ...  # ❌ Domain CANNOT depend on DB
from app.ui import ...           # ❌ Domain CANNOT depend on UI

# UI should never import Domain or Persistence
from app.domain import ...       # ❌ UI CANNOT depend on Domain
from app.persistence import ...  # ❌ UI CANNOT depend on Persistence
```

### Dependency Injection Pattern

**DO NOT create dependencies inside classes:**

```python
# ❌ BAD - Hard-coded dependency
class EstimationTab(QWidget):
    def __init__(self):
        session = get_session()                          # ❌ Creating inside
        repository = EmployeeRepository(session)         # ❌ Creating inside
        self.service = EstimationService(repository)     # ❌ Creating inside
```

**DO inject dependencies from outside:**

```python
# ✅ GOOD - Dependency injection
class EstimationTab(QWidget):
    def __init__(self, service: EstimationService):  # ← Passed in!
        self.service = service                        # ← Just use it
```

**Wire everything in main_window.py:**

```python
# app/ui/main_window.py

from PyQt6.QtWidgets import QMainWindow
from app.persistence.database import get_session
from app.persistence.repositories.multiplier_repository import MultiplierRepository
from app.domain.cost_calculator import CostCalculator
from app.application.estimation_service import EstimationService
from app.ui.tabs.estimation_tab import EstimationTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup dependencies (Dependency Injection)
        session = get_session()
        multiplier_repo = MultiplierRepository(session)
        cost_calc = CostCalculator()
        estimation_service = EstimationService(cost_calc, multiplier_repo)
        
        # Inject into UI
        estimation_tab = EstimationTab(estimation_service)
        
        # ... rest of UI setup
```

---

## NAMING CONVENTIONS

### File Names
```
DO:
- cost_calculator.py       # Descriptive, lowercase, underscores
- employee_repository.py   # Entity name + pattern name
- estimation_tab.py        # What + where

DON'T:
- costCalc.py              # ❌ Camelcase in Python
- emp_repo.py              # ❌ Abbreviations
- tab1.py                  # ❌ Generic names
```

### Class Names
```
DO:
class CostCalculator:              # PascalCase
class EmployeeRepository:          # Entity + Pattern
class EstimationService:           # UseCaseName + "Service"
class EstimationType(BaseTab):     # Type or Purpose + "Tab"

DON'T:
class costCalculator:              # ❌ camelCase
class Calc:                        # ❌ Abbreviations
class EmployeeStuff:               # ❌ Vague names
```

### Function Names
```
DO:
def calculate_module_cost(...):    # verb_object_specifier
def get_by_id(emp_id):             # get_by_X
def save(...):                     # save, create, update, delete
def format_inr(value):             # format_X

DON'T:
def calc_mod_cost(...):            # ❌ Abbreviations
def GetEmployeeData():             # ❌ PascalCase
def do_stuff():                    # ❌ Vague
def format_currency():             # ❌ Too generic (for which currency?)
```

### Variable Names
```
DO:
project_id = 42
employee_data = {name: "John", ...}
total_labor_cost = 50000
region_multiplier = 1.2

DON'T:
pid = 42                    # ❌ Abbreviations
e_data = {...}              # ❌ Cryptic
tlc = 50000                 # ❌ All caps for non-constants
rm = 1.2                    # ❌ Single letters
```

---

## CODE EXAMPLES

### Example 1: Complete Flow (Small Feature)

**Story:** Calculate employee hourly cost from base salary

#### Domain Layer (Pure logic)
```python
# app/domain/cost_calculator.py

class CostCalculator:
    """Pure math - no DB, no UI"""
    
    def calculate_hourly_cost(
        self,
        base_salary: float,
        pf_pct: float = 12.0,
        bonus_pct: float = 8.33,
        leave_pct: float = 4.0,
        infra_pct: float = 5.0,
        admin_pct: float = 3.0
    ) -> dict:
        """
        Real Monthly = Base × (1 + total_pct/100)
        Hourly = Real Monthly / 22 / 8
        """
        total_pct = pf_pct + bonus_pct + leave_pct + infra_pct + admin_pct
        real_monthly = base_salary * (1 + total_pct / 100)
        hourly = real_monthly / 22 / 8
        
        return {
            "total_add_on_pct": total_pct,
            "real_monthly_cost": round(real_monthly, 2),
            "hourly_cost": round(hourly, 2)
        }
```

#### Persistence Layer (Data access)
```python
# app/persistence/repositories/employee_repository.py

from app.persistence.models import Employee

class EmployeeRepository:
    def __init__(self, session):
        self.session = session
    
    def get_by_id(self, emp_id: int) -> Employee:
        return self.session.query(Employee).filter_by(id=emp_id).first()
    
    def create(self, name: str, role: str, base_salary: float) -> Employee:
        emp = Employee(name=name, role=role, base_salary=base_salary)
        self.session.add(emp)
        self.session.commit()
        return emp
    
    def update_salary(self, emp_id: int, base_salary: float) -> Employee:
        emp = self.get_by_id(emp_id)
        emp.base_salary = base_salary
        self.session.commit()
        return emp
```

#### Application Layer (Orchestration)
```python
# app/application/employee_service.py

from app.domain.cost_calculator import CostCalculator
from app.persistence.repositories.employee_repository import EmployeeRepository

class EmployeeService:
    def __init__(self, calc: CostCalculator, repo: EmployeeRepository):
        self.calc = calc
        self.repo = repo
    
    def get_employee_with_costs(self, emp_id: int) -> dict:
        """Get employee and calculate their hourly cost"""
        # Fetch from DB
        emp = self.repo.get_by_id(emp_id)
        if not emp:
            raise ValueError(f"Employee {emp_id} not found")
        
        # Calculate using domain
        cost_breakdown = self.calc.calculate_hourly_cost(
            base_salary=emp.base_salary,
            pf_pct=emp.pf_pct,
            bonus_pct=emp.bonus_pct,
            leave_pct=emp.leave_pct,
            infra_pct=emp.infra_pct,
            admin_pct=emp.admin_pct
        )
        
        # Return as plain dict (not ORM object)
        return {
            "emp_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "base_salary": emp.base_salary,
            "real_monthly_cost": cost_breakdown["real_monthly_cost"],
            "hourly_cost": cost_breakdown["hourly_cost"]
        }
    
    def create_employee(self, name: str, role: str, base_salary: float) -> dict:
        """Create employee and calculate costs"""
        emp = self.repo.create(name, role, base_salary)
        return self.get_employee_with_costs(emp.id)
```

#### Presentation Layer (UI)
```python
# app/ui/components/forms/employee_form.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QDoubleSpinBox, QPushButton, QLabel
)
from app.application.employee_service import EmployeeService

class EmployeeForm(QWidget):
    def __init__(self, service: EmployeeService):  # ← Injected
        super().__init__()
        self.service = service
        self._setup_ui()
    
    def _setup_ui(self):
        """Build form"""
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.role_input = QLineEdit()
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setPrefix("₹ ")
        
        form.addRow("Name:", self.name_input)
        form.addRow("Role:", self.role_input)
        form.addRow("Base Salary:", self.salary_input)
        
        self.result_label = QLabel()
        
        btn = QPushButton("Create & Calculate")
        btn.clicked.connect(self._on_create)
        
        layout.addLayout(form)
        layout.addWidget(btn)
        layout.addWidget(self.result_label)
    
    def _on_create(self):
        """Handle button click"""
        try:
            # Read UI
            name = self.name_input.text()
            role = self.role_input.text()
            salary = float(self.salary_input.value())
            
            # Call service (all logic happens here)
            result = self.service.create_employee(name, role, salary)
            
            # Display result
            msg = f"Created {result['name']}\n"
            msg += f"Hourly: ₹{result['hourly_cost']}"
            self.result_label.setText(msg)
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
```

#### Test
```python
# tests/application/test_employee_service.py

import pytest
from app.domain.cost_calculator import CostCalculator
from app.application.employee_service import EmployeeService

# Fake repository (no real DB!)
class FakeEmployeeRepository:
    def __init__(self):
        self.employees = {}
    
    def get_by_id(self, emp_id):
        class FakeEmp:
            id = emp_id
            name = "John"
            role = "Dev"
            base_salary = 100000
            pf_pct = 12
            bonus_pct = 8.33
            leave_pct = 4
            infra_pct = 5
            admin_pct = 3
        return FakeEmp()
    
    def create(self, name, role, salary):
        emp = self.get_by_id(1)
        return emp

def test_employee_costs():
    """Test WITHOUT DB, WITHOUT UI"""
    calc = CostCalculator()
    repo = FakeEmployeeRepository()
    service = EmployeeService(calc, repo)
    
    result = service.get_employee_with_costs(1)
    
    # Base 100000, total_pct = 32.33%
    # Real monthly = 100000 * 1.3233 = 132330
    # Hourly = 132330 / 22 / 8 = 752.78
    assert result["hourly_cost"] == 752.78
```

---

## ANTI-PATTERNS (What NOT To Do)

### ❌ NEVER: Mix layers

```python
# ❌ BAD - UI doing business logic
class EstimationTab(QWidget):
    def _on_calculate(self):
        # Business logic in UI method!
        modules = self.get_modules_from_table()
        complexity_mult = get_complexity_multiplier(...)  # ← Domain logic
        adjusted_cost = sum(...) * complexity_mult        # ← Domain logic
        self.result_label.setText(adjusted_cost)

# ✅ GOOD - UI delegates to service
class EstimationTab(QWidget):
    def _on_calculate(self):
        result = self.service.estimate(...)  # Service does the work
        self.result_label.setText(result['cost'])
```

### ❌ NEVER: Import from higher layers in lower layers

```python
# ❌ BAD - Domain importing UI/Persistence
from app.ui.main_window import MainWindow
from app.persistence.models import Employee

def calculate_cost():  # Domain logic importing UI!
    ...

# ✅ GOOD - Clean dependencies
def calculate_cost(hourly_rate, hours):  # No imports needed
    return hourly_rate * hours
```

### ❌ NEVER: Create dependencies inside constructors

```python
# ❌ BAD - Hard-coded dependencies
class EmployeeService:
    def __init__(self):
        self.session = get_session()              # Created inside
        self.repo = EmployeeRepository(...)       # Created inside
        self.calculator = CostCalculator(...)     # Created inside

# ✅ GOOD - Dependencies injected
class EmployeeService:
    def __init__(self, calc, repo):  # Passed in
        self.calc = calc
        self.repo = repo
```

### ❌ NEVER: Store ORM objects in UI

```python
# ❌ BAD - returning ORM object to UI
def get_employee(emp_id):
    emp = session.query(Employee).get(emp_id)
    return emp  # ← ORM object leaks to UI

# ✅ GOOD - Transform to plain dict
def get_employee(emp_id):
    emp = session.query(Employee).get(emp_id)
    return {
        "id": emp.id,
        "name": emp.name,
        "salary": emp.base_salary
    }  # ← Plain data to UI
```

### ❌ NEVER: Session management scattered everywhere

```python
# ❌ BAD - Each method creates its own session
def method1():
    session = get_session()
    ...

def method2():
    session = get_session()  # Another session!
    ...

# ✅ GOOD - Repositories manage sessions
class EmployeeRepository:
    def __init__(self, session):  # Injected once
        self.session = session
    
    def get_all(self):
        return self.session.query(Employee)...
    
    def get_one(self):
        return self.session.query(Employee)...  # Reuses session
```

### ❌ NEVER: Vague error handling

```python
# ❌ BAD
try:
    result = service.calculate(data)
except:
    self.label.setText("Error")  # What error? No clue!

# ✅ GOOD
try:
    result = service.calculate(data)
except ValueError as e:
    self.label.setText(f"Invalid input: {e}")
except Exception as e:
    self.label.setText(f"Unexpected error: {e}")
```

---

## TESTING STRATEGY

### Layer-By-Layer Testing

#### Domain Tests (100% coverage)
```python
# tests/domain/test_cost_calculator.py

def test_calculate_hourly_cost():
    calc = CostCalculator()
    result = calc.calculate_hourly_cost(
        base_salary=100000,
        pf_pct=12,
        bonus_pct=8.33,
        leave_pct=4,
        infra_pct=5,
        admin_pct=3
    )
    assert result['hourly_cost'] == 752.78
```

**Why easy?** No DB, no UI, just math. Pure functions.

#### Application Tests (With fakes)
```python
# tests/application/test_employee_service.py

class FakeRepo:
    def get_by_id(self, emp_id):
        return MockEmployee(id=emp_id, base_salary=100000)

def test_service():
    service = EmployeeService(CostCalculator(), FakeRepo())
    result = service.get_employee_with_costs(1)
    assert result['hourly_cost'] == 752.78
```

**Why easy?** Fake repo instead of real DB.

#### Persistence Tests (Real SQLite)
```python
# tests/persistence/test_employee_repository.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_create_employee(db_session):
    repo = EmployeeRepository(db_session)
    emp = repo.create("John", "Dev", 100000)
    assert emp.id is not None
```

**Why okay?** In-memory SQLite, fast and isolated.

#### UI Tests (Minimal)
```python
# tests/ui/test_components.py

def test_employee_form_renders():
    service = FakeEmployeeService()
    form = EmployeeForm(service)
    assert form is not None
```

**Why minimal?** PyQt6 is hard to test. Keep UI dumb = less to test.

---

## MIGRATION PHASES

### Phase 1: Setup Architecture (Week 1)
- [ ] Create folder structure (`domain/`, `persistence/`, `application/`)
- [ ] Create base classes (BaseRepository, BaseService)
- [ ] Create constants file (`domain/constants.py`)
- [ ] Set up `.copilot-instructions.md` (this file) ✅ DONE

### Phase 2: Extract Domain (Week 2)
- [ ] Move all pure logic functions from `logic.py` → `domain/cost_calculator.py`
- [ ] Move constants from `logic.py` → `domain/constants.py`
- [ ] Create `domain/estimation_calculator.py` (full estimation logic)
- [ ] Create `domain/variance_calculator.py` (variance & analytics)
- [ ] Unit test domain (100% coverage)

### Phase 3: Build Repositories (Week 3)
- [ ] Create `base_repository.py` with common CRUD
- [ ] Create repository for each entity (Employee, Project, Estimate, etc.)
- [ ] Move all `session.query()` calls into repositories
- [ ] Create tests for each repository

### Phase 4: Create Services (Week 4)
- [ ] Create `estimation_service.py` (use case: estimate project)
- [ ] Create `employee_service.py` (use case: CRUD employees)
- [ ] Create `project_service.py` (use case: CRUD projects)
- [ ] Create `export_service.py` (use case: generate PDF)
- [ ] Create `analytics_service.py` (use case: calculate analytics)
- [ ] Unit test services (with fake repos)

### Phase 5: Refactor UI (Week 5)
- [ ] Break `main_ui.py` → `ui/tabs/` (one file per tab)
- [ ] Create reusable components in `ui/components/`
- [ ] Remove all DB access from UI
- [ ] Remove all business logic from UI
- [ ] Implement dependency injection in `main_window.py`

### Phase 6: Wire It Up (Week 6)
- [ ] Update `run.py` to instantiate all services
- [ ] Update `main_window.py` to inject services
- [ ] Test entire flow (all tabs working)
- [ ] Update tests

### Phase 7: Polish & Docs (Week 7)
- [ ] Add docstrings
- [ ] Add type hints
- [ ] Refactor tests
- [ ] Update README.md
- [ ] Code review

---

## QUICK REFERENCE

### When adding a feature:

**Question:** Where does this code belong?

```
Is it pure math/logic with no DB or UI?
    → DOMAIN layer

Does it access the database?
    → PERSISTENCE layer (repository)

Does it orchestrate logic + DB?
    → APPLICATION layer (service)

Does it display or handle user interaction?
    → PRESENTATION layer (UI)
```

### When writing code:

```
1. Is it testable without UI? If no → refactor
2. Does it have one responsibility? If no → split
3. Can it be reused outside PyQt6? If no → refactor
4. Why does it import that? Ask yourself → refactor if wrong
```

### When reviewing code:

```
❌ Check for:
- UI importing Domain/Persistence
- Domain importing anything except stdlib
- Service creating its own dependencies
- Database access outside repositories
- Business logic outside domain

✅ Look for:
- Clean layer boundaries
- Dependency injection
- Plain Python data (not ORM objects) in UI
- Pure functions in domain
```

---

## SUMMARY

**Remember:**
```
┌─────────────────────────────────────────┐
│    EACH LAYER HAS ONE RESPONSIBILITY     │
├─────────────────────────────────────────┤
│ Domain:  Pure logic (math, rules)        │
│ Persist: Data access (CRUD)              │
│ App:     Orchestration (workflow)        │
│ UI:      Display + events (dumb)         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│     FOLLOW THE DEPENDENCY FLOW           │
├─────────────────────────────────────────┤
│ UI  → App → {Domain, Persist}           │
│     NO BACKFLOW (Persist ≠→ UI)          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         USE DEPENDENCY INJECTION         │
├─────────────────────────────────────────┤
│ Pass in; don't create inside             │
│ Makes testing easy (use fakes)           │
│ Makes code reusable                      │
└─────────────────────────────────────────┘
```

---

**Questions?** When in doubt, ask: *"Does this create a dependency on UI/DB?"* If yes → refactor to a lower layer.

