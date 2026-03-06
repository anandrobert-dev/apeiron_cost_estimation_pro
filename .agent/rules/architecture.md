# Architecture Rules

Strict layer separation defines the Clean 4-Layer Architecture of Apeiron CostEstimation Pro.

## 1. Dependency Flow

```
UI → Application → {Domain, Persistence}
                    Persistence → Domain
                    Domain → NOTHING
```

**The Laws:**
- **UI** → imports Application ONLY.
- **Application** → imports Domain + Persistence ONLY.
- **Persistence** → imports Domain ONLY (for shared constants/types).
- **Domain** → imports NOTHING from internal app layers (Pure Python + stdlib only).
- **Utils** → can be imported by any layer. Must NOT import from Domain, Persistence, Application, or UI.

## 2. Forbidden Imports

| From Layer    | Cannot Import                                        |
|---------------|------------------------------------------------------|
| **UI**        | `app.domain`, `app.persistence`                      |
| **Domain**    | `app.ui`, `app.persistence`, `app.application`       |
| **Persistence** | `app.ui`, `app.application`                        |
| **Application** | `app.ui`                                           |

## 3. Layer Responsibilities

### 3.1 Domain (`app/domain/`)
- Pure business logic, math, and formulas.
- No database access (`session.query`, commits), no UI frameworks.
- Accepts plain Python parameters (floats, dicts, lists) — never ORM objects.
- 100% testable in isolation.
- Can be reused in CLI, Web, or API contexts later.

### 3.2 Persistence (`app/persistence/`)
- Encapsulated database operations (SQLAlchemy ORM models + Repositories).
- All `session.query()` calls MUST live inside repositories.
- CRUD methods: `create()`, `get_by_id()`, `get_all()`, `update()`, `delete()`.
- Session management is centralized — never scatter `get_session()` calls.

### 3.3 Application (`app/application/`)
- Use-case orchestration: combine Domain calculators with Persistence repositories.
- Accepts plain Python inputs from UI (NOT widget references).
- Returns plain Python outputs (dicts/lists) to UI — **never ORM objects**.
- Stateless where possible.

### 3.4 UI (`app/ui/`)
- Presentation and user interaction (PyQt6 widgets).
- Thin event handlers: **Read UI → Call Service → Display Result**.
- No business logic, no database queries.
- Dependencies (services) must be injected via constructor.

### 3.5 Utils (`app/utils/`)
- Shared helpers: formatting, validation, exceptions.
- Must remain layer-agnostic (no domain logic, no DB access, no UI imports).

## 4. Dependency Injection
Dependencies must be injected via constructors. Never hard-code instantiations inside classes.

```python
# ✅ GOOD — Dependencies injected
class EstimationService:
    def __init__(self, repository: ProjectRepository, calculator: CostCalculator):
        self.repository = repository
        self.calculator = calculator

# ❌ BAD — Hard-coded dependencies
class EstimationService:
    def __init__(self):
        self.repository = ProjectRepository(get_session())  # Created inside
```

All wiring happens in `main_window.py` (the composition root).

## 5. Anti-Patterns (NEVER Do These)

### 5.1 Business logic in UI
```python
# ❌ BAD
def _on_calculate(self):
    modules = self.get_modules_from_table()
    adjusted_cost = sum(modules) * get_complexity_multiplier()  # Domain logic in UI!

# ✅ GOOD
def _on_calculate(self):
    result = self.service.estimate(...)  # Service does all the work
    self.result_label.setText(result['cost'])
```

### 5.2 ORM objects leaking to UI
```python
# ❌ BAD — returning ORM object
def get_employee(self, emp_id):
    return self.session.query(Employee).get(emp_id)  # ORM leaks to UI

# ✅ GOOD — transform to dict
def get_employee(self, emp_id):
    emp = self.repo.get_by_id(emp_id)
    return {"id": emp.id, "name": emp.name, "salary": emp.base_salary}
```

### 5.3 Session management scattered across files
```python
# ❌ BAD — each method creates its own session
def method1():
    session = get_session()  # Session A

def method2():
    session = get_session()  # Session B — inconsistent!

# ✅ GOOD — injected once via repository constructor
class EmployeeRepository:
    def __init__(self, session):
        self.session = session  # Shared, predictable
```

## 6. Quick Reference: "Where does this code go?"

```
Is it pure math/logic with no DB or UI?
    → DOMAIN layer

Does it access the database?
    → PERSISTENCE layer (repository)

Does it orchestrate logic + DB?
    → APPLICATION layer (service)

Does it display or handle user interaction?
    → UI layer (PyQt6 widget)

Is it a shared helper (formatting, validation)?
    → UTILS
```
