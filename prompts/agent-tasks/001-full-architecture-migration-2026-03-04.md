# Task: Full Clean Architecture Migration

**Task ID:** 001  
**Date:** 2026-03-04  
**Phase:** Migration Phases 1–7 (all)  
**Architecture Reference:** `.github/copilot-instructions.md`  
**Rules Reference:** `.agent/rules.md`  
**Workflow Reference:** `.agent/workflows/new-task.md`

---

## Original Request

Migrate the entire Apeiron CostEstimation Pro application from its current flat
single-folder structure to a clean 4-layer architecture (Domain / Persistence /
Application / UI) as defined in `.github/copilot-instructions.md`.

---

## Current State

### Source Files

| File | Lines | Problem |
|------|-------|---------|
| `app/logic.py` | 454 | Mixes domain math + DB session calls + audit writes |
| `app/models.py` | 376 | ORM models (keep in Persistence layer – mostly fine) |
| `app/database.py` | 261 | DB engine + session factory + seed data |
| `app/main_ui.py` | 799 | Monolithic UI with inline business logic & DB access |
| `app/proposal_generator.py` | 284 | PDF export with mixed concerns |
| `app/ui_charts.py` | 109 | Chart helpers (UI) |
| `app/ui_sop.py` | 123 | SOP tab (UI) |
| `app/ui_sysconfig.py` | 282 | System config tab (UI) |
| `app/ui_theme.py` | 113 | Theme/style (UI) |

### Entities (from `models.py`)

- **Employee** — costs: base salary, PF%, bonus%, leave%, infra%, admin%
- **RegionMultiplier** — geography-based rate multipliers
- **StackCost** — technology stack/license costs
- **InfraCost** — hosting/infrastructure costs
- **Project** — top-level project with modules, settings, status
- **ProjectModule** — individual work item: employee + hours + cost
- **Estimate** — computed snapshot: labor/infra/stack/risk/final price
- **Actual** — real post-project cost for variance tracking
- **MaintenanceRecord** — multi-year maintenance forecast
- **SystemLookup** — dynamic dropdown values
- **AppTypeMultiplier** — per app-type effort multiplier
- **ComplexityMultiplier** — per complexity multiplier
- **PricingStrategy** — profit/risk preset profiles
- **IndustryPreset + IndustryPresetModule** — template module groups
- **AuditLog** — field-level change history

### Domain Functions Already Identified (in `logic.py`)

- `compute_hourly_from_salary()` → pure function ✅ → move to Domain
- `calculate_module_cost()` → takes ORM object ⚠️ → partial refactor
- `calculate_total_labor_cost()` → takes `session` ❌ → split
- `calculate_total_hours()` → pure ✅
- `hours_to_person_months()` → pure ✅
- `calculate_stage_distribution()` → pure ✅
- `calculate_infra_stack_total()` → takes ORM list ⚠️
- `calculate_risk_buffer()` → pure ✅
- `calculate_final_price()` → pure ✅
- `calculate_maintenance_forecast()` → pure ✅
- `calculate_variance()` → pure ✅
- `cost_per_function_point()` → pure ✅
- `burn_rate_monthly()` → pure ✅
- `revenue_margin()` → pure ✅
- `contribution_margin()` → pure ✅
- `run_full_estimation()` → full orchestrator ❌ → move to Application
- `format_inr()` → formatting helper → move to `utils/formatting.py`
- `create_audit_entry()` → DB write ❌ → move to `AuditRepository`
- `get_complexity_multiplier()` → DB query ❌ → move to `MultiplierRepository`
- `get_app_type_adjustment()` → DB query ❌ → move to `MultiplierRepository`

---

## Task Analysis

### Layer Mapping

| What | Where Now | Target Layer | Target File |
|------|-----------|--------------|-------------|
| Hourly cost math | `logic.py` | Domain | `app/domain/cost_calculator.py` |
| Stage distribution | `logic.py` | Domain | `app/domain/estimation_calculator.py` |
| Risk & buffer | `logic.py` | Domain | `app/domain/estimation_calculator.py` |
| Variance calc | `logic.py` | Domain | `app/domain/variance_calculator.py` |
| Maintenance forecast | `logic.py` | Domain | `app/domain/maintenance_calculator.py` |
| Analytics helpers | `logic.py` | Domain | `app/domain/estimation_calculator.py` |
| INR formatting | `logic.py` | Utils | `app/utils/formatting.py` |
| Constants/defaults | `logic.py` | Domain | `app/domain/constants.py` |
| ORM Models | `models.py` | Persistence | `app/persistence/models.py` |
| Session factory | `database.py` | Persistence | `app/persistence/database.py` |
| Employee CRUD | `main_ui.py` | Persistence | `app/persistence/repositories/employee_repository.py` |
| Project CRUD | `main_ui.py` | Persistence | `app/persistence/repositories/project_repository.py` |
| Estimate CRUD | `main_ui.py` | Persistence | `app/persistence/repositories/estimate_repository.py` |
| Multiplier lookup | `logic.py` | Persistence | `app/persistence/repositories/multiplier_repository.py` |
| Industry presets | `database.py` | Persistence | `app/persistence/repositories/preset_repository.py` |
| Audit log writes | `logic.py` | Persistence | `app/persistence/repositories/audit_repository.py` |
| StackCost/InfraCost | `main_ui.py` | Persistence | `app/persistence/repositories/pricing_repository.py` |
| Full estimation flow | `logic.py` | Application | `app/application/estimation_service.py` |
| Employee use-cases | `main_ui.py` | Application | `app/application/employee_service.py` |
| Project use-cases | `main_ui.py` | Application | `app/application/project_service.py` |
| PDF/proposal export | `proposal_generator.py` | Application | `app/application/export_service.py` |
| Analytics | `main_ui.py` | Application | `app/application/analytics_service.py` |
| Pricing strategies | `main_ui.py` | Application | `app/application/pricing_service.py` |
| Main window | `main_ui.py` | UI | `app/ui/main_window.py` |
| Estimation tab | `main_ui.py` | UI | `app/ui/tabs/estimation_tab.py` |
| Master data tab | `main_ui.py` | UI | `app/ui/tabs/master_data_tab.py` |
| Analysis tab | `main_ui.py` | UI | `app/ui/tabs/analysis_tab.py` |
| Proposal tab | `main_ui.py` | UI | `app/ui/tabs/proposal_tab.py` |
| System config | `ui_sysconfig.py` | UI | `app/ui/tabs/sysconfig_tab.py` |
| SOP/Help | `ui_sop.py` | UI | `app/ui/tabs/sop_tab.py` |
| Charts | `ui_charts.py` | UI | `app/ui/components/charts.py` |
| Theme/style | `ui_theme.py` | UI | `app/ui/style/theme.py` |

### Dependency Flow Confirmation

```
app/ui/ → app/application/ → app/domain/
                           → app/persistence/ → app/domain/
                                              → app/persistence/models.py
app/utils/ (standalone – imported by any layer where needed)
```

### Import Violations to Fix in `logic.py`

```python
# CURRENT (logic.py line 9-13) — Domain importing DB models
from app.models import Employee, Project, ProjectModule, Estimate, MaintenanceRecord, AuditLog

# FIX: domain functions work with plain values; ORM objects only enter at Persistence
```

---

## Implementation Checklist

### PHASE 1: Folder Scaffolding (Week 1)

#### Step 1.1 — Create target folder structure
- [ ] `app/domain/__init__.py`
- [ ] `app/persistence/__init__.py`
- [ ] `app/persistence/repositories/__init__.py`
- [ ] `app/application/__init__.py`
- [ ] `app/ui/__init__.py`
- [ ] `app/ui/tabs/__init__.py`
- [ ] `app/ui/components/__init__.py`
- [ ] `app/ui/components/forms/__init__.py`
- [ ] `app/ui/components/tables/__init__.py`
- [ ] `app/ui/style/__init__.py`
- [ ] `app/utils/__init__.py`
- [ ] `tests/domain/__init__.py`
- [ ] `tests/persistence/__init__.py`
- [ ] `tests/application/__init__.py`
- [ ] `tests/ui/__init__.py`

#### Step 1.2 — Create base/skeleton files
- [ ] `app/domain/constants.py` — move DEFAULT_STAGES, VARIANCE_THRESHOLDS
- [ ] `app/persistence/repositories/base_repository.py` — abstract CRUD base
- [ ] `app/application/base_service.py` — common service patterns
- [ ] `app/utils/formatting.py` — move `format_inr()` here
- [ ] `app/utils/exceptions.py` — custom exception classes
- [ ] `app/utils/validators.py` — input validation helpers
- [ ] `tests/conftest.py` — shared pytest fixtures (in-memory DB session)

---

### PHASE 2: Extract Domain Layer (Week 2)

All files in this phase: **ZERO imports from app.models, app.persistence, app.ui**

#### Step 2.1 — `app/domain/constants.py`
```
Move from logic.py:
- DEFAULT_STAGES dict
- VARIANCE_THRESHOLDS dict

Add:
- WORKING_DAYS_PER_MONTH = 22
- WORKING_HOURS_PER_DAY = 8
- HOURS_PER_PERSON_MONTH = 176
- DEFAULT_MAINTENANCE_PCT = 15.0
- DEFAULT_RISK_PCT = 10.0
- DEFAULT_PROFIT_PCT = 20.0
```

#### Step 2.2 — `app/domain/cost_calculator.py`
```
Extract from logic.py (make pure — remove ORM object params):
+ compute_hourly_from_salary(base_salary, pf_pct, ...) → dict (pure ✅)
+ calculate_module_cost(hourly_rate, hours, region_mult) → float (NOW pure: no ORM)
+ calculate_total_labor(module_costs, complexity_mult, app_type_adj) → dict
+ calculate_total_hours(hours_list) → float (param: list[float] not ORM objects)
+ hours_to_person_months(hours) → float
```

#### Step 2.3 — `app/domain/estimation_calculator.py`
```
Extract from logic.py (all pure):
+ calculate_stage_distribution(total_cost, stage_pcts) → dict
+ calculate_infra_stack_total(infra_costs, stack_costs) → dict (param: list[float] not ORM)
+ calculate_risk_buffer(gross_cost, maintenance_pct, risk_pct) → dict
+ calculate_final_price(safe_cost, profit_pct) → dict
+ calculate_gross_cost(labor, infra_stack) → float
+ cost_per_function_point(total_cost, fps) → float
+ burn_rate_monthly(total_cost, duration_months) → float
+ revenue_margin(final_price, safe_cost) → float
+ contribution_margin(final_price, variable_cost) → float
```

#### Step 2.4 — `app/domain/variance_calculator.py`
```
Extract from logic.py:
+ calculate_variance(estimated, actual) → dict (pure ✅)
+ classify_variance(variance_pct) → str
```

#### Step 2.5 — `app/domain/maintenance_calculator.py`
```
Extract from logic.py:
+ calculate_maintenance_forecast(dev_cost, annual_pct, years) → list[dict] (pure ✅)
+ calculate_cumulative_maintenance(forecast) → float
```

#### Step 2.6 — Tests
- [ ] `tests/domain/test_cost_calculator.py` — 100% coverage
- [ ] `tests/domain/test_estimation_calculator.py` — 100% coverage
- [ ] `tests/domain/test_variance_calculator.py` — 100% coverage
- [ ] `tests/domain/test_maintenance_calculator.py` — 100% coverage

**Key test patterns for domain:**
```python
# pure: no DB fixture needed
def test_compute_hourly_from_salary():
    calc = CostCalculator()
    result = calc.compute_hourly_from_salary(base_salary=100000)
    assert result["hourly_cost"] == 752.78

def test_calculate_variance_perfect():
    vc = VarianceCalculator()
    result = vc.calculate_variance(estimated=100000, actual=103000)
    assert result["is_perfect"] is True  # 3% < 5%
```

---

### PHASE 3: Build Persistence Layer (Week 3)

#### Step 3.1 — Move models and database
- [ ] Copy `app/models.py` → `app/persistence/models.py` (unchanged content)
- [ ] Copy `app/database.py` → `app/persistence/database.py`
  - Keep: `get_engine()`, `get_session()`, `Base`, `create_all_tables()`
  - Move seed data → separate `app/persistence/seed_data.py`
- [ ] Keep backward-compat re-exports in `app/models.py` and `app/database.py`  
  during transition period (import from new location, re-export)

#### Step 3.2 — `app/persistence/repositories/base_repository.py`
```python
class BaseRepository:
    def __init__(self, session): self.session = session
    def commit(self): self.session.commit()
    def rollback(self): self.session.rollback()
    def flush(self): self.session.flush()
```

#### Step 3.3 — `app/persistence/repositories/employee_repository.py`
```
Methods:
+ create(name, role, base_salary, **overrides) → Employee
+ get_by_id(emp_id) → Employee | None
+ get_all(active_only=True) → list[Employee]
+ update(emp_id, **kwargs) → Employee
+ delete(emp_id) → bool
+ get_roles() → list[str]  (distinct roles)
```

#### Step 3.4 — `app/persistence/repositories/project_repository.py`
```
Methods:
+ create(**kwargs) → Project
+ get_by_id(project_id) → Project | None
+ get_with_modules(project_id) → Project  (eager loads modules)
+ get_all(status=None) → list[Project]
+ update(project_id, **kwargs) → Project
+ delete(project_id) → bool
+ get_region_multiplier(project_id) → float
```

#### Step 3.5 — `app/persistence/repositories/estimate_repository.py`
```
Methods:
+ save_estimate(project_id, estimate_data: dict) → Estimate
+ get_by_project(project_id) → Estimate | None
+ save_maintenance_records(project_id, forecast: list[dict]) → list[MaintenanceRecord]
+ save_actual(project_id, actual_cost, ...) → Actual
+ get_actual(project_id) → Actual | None
```

#### Step 3.6 — `app/persistence/repositories/multiplier_repository.py`
```
Methods:
+ get_complexity_multiplier(name) → float
+ get_app_type_multiplier(name) → float
+ get_region_multiplier(region_id) → float
+ get_all_complexity() → list[ComplexityMultiplier]
+ get_all_app_types() → list[AppTypeMultiplier]
+ upsert_complexity(name, multiplier) → ComplexityMultiplier
+ upsert_app_type(name, multiplier) → AppTypeMultiplier
```

#### Step 3.7 — `app/persistence/repositories/pricing_repository.py`
```
Handles: StackCost, InfraCost, PricingStrategy

Methods:
+ get_all_stack_costs() → list[StackCost]
+ get_all_infra_costs() → list[InfraCost]
+ create_stack_cost(**kwargs) → StackCost
+ create_infra_cost(**kwargs) → InfraCost
+ update_stack_cost(id, **kwargs) → StackCost
+ update_infra_cost(id, **kwargs) → InfraCost
+ delete_stack_cost(id) → bool
+ delete_infra_cost(id) → bool
+ get_all_pricing_strategies() → list[PricingStrategy]
+ get_pricing_strategy(name) → PricingStrategy | None
```

#### Step 3.8 — `app/persistence/repositories/preset_repository.py`
```
Methods:
+ get_all_presets() → list[IndustryPreset]
+ get_preset_with_modules(preset_id) → IndustryPreset
+ create_preset(name, modules: list[dict]) → IndustryPreset
+ delete_preset(preset_id) → bool
+ get_lookup_values(category) → list[str]  (from SystemLookup)
+ add_lookup_value(category, value) → SystemLookup
+ delete_lookup_value(id) → bool
```

#### Step 3.9 — `app/persistence/repositories/audit_repository.py`
```
Methods:
+ log(table_name, record_id, action, field_name, old_value, new_value) → AuditLog
+ get_for_record(table_name, record_id) → list[AuditLog]
+ get_recent(limit=50) → list[AuditLog]
```

#### Step 3.10 — Tests
- [ ] `tests/persistence/test_employee_repository.py` — CRUD + edge cases  
- [ ] `tests/persistence/test_project_repository.py` — CRUD + eager load
- [ ] `tests/persistence/test_estimate_repository.py` — save/retrieve
- [ ] `tests/persistence/test_multiplier_repository.py` — lookup correctness

**conftest.py pattern:**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.persistence.models import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
```

---

### PHASE 4: Create Application Layer (Week 4)

All services: **accept plain Python dicts/primitives; return plain Python dicts**  
No ORM objects should leak to UI.

#### Step 4.1 — `app/application/employee_service.py`
```
Orchestrates: EmployeeRepository + CostCalculator

Methods:
+ create_employee(name, role, base_salary, **overrides) → dict
+ update_employee(emp_id, **kwargs) → dict
+ delete_employee(emp_id) → bool
+ get_employee(emp_id) → dict  (includes computed hourly_cost)
+ get_all_employees() → list[dict]
+ recalculate_all_costs() → int  (count updated)
```

#### Step 4.2 — `app/application/project_service.py`
```
Orchestrates: ProjectRepository + MultiplierRepository + CostCalculator

Methods:
+ create_project(**kwargs) → dict
+ update_project(project_id, **kwargs) → dict
+ delete_project(project_id) → bool
+ get_project(project_id) → dict
+ get_all_projects(status=None) → list[dict]
+ add_module(project_id, module_data: dict) → dict
+ update_module(module_id, **kwargs) → dict
+ delete_module(module_id) → bool
+ apply_industry_preset(project_id, preset_id) → dict
```

#### Step 4.3 — `app/application/estimation_service.py`
```
Orchestrates: All repositories + All domain calculators

Main method:
+ estimate_project(project_id, pricing_strategy=None) → dict  (full result)

Returns dict containing:
  - labor breakdown (module costs, multipliers, totals)
  - infra/stack totals
  - risk/buffer breakdown
  - final pricing
  - stage distribution
  - maintenance forecast (5 years)
  - analytics (FP cost, burn rate, etc.)

Other methods:
+ save_estimate(project_id, result: dict) → dict
+ get_saved_estimate(project_id) → dict | None
+ record_actual(project_id, actual_cost, duration_months) → dict
```

#### Step 4.4 — `app/application/analytics_service.py`
```
Orchestrates: EstimateRepository + ActualRepository + VarianceCalculator

Methods:
+ get_variance_report(project_id) → dict
+ get_portfolio_summary() → dict  (all projects: estimate vs actual)
+ get_maintenance_forecast(project_id) → list[dict]
+ compare_estimates(project_ids: list[int]) → list[dict]
```

#### Step 4.5 — `app/application/pricing_service.py`
```
Orchestrates: PricingRepository + EstimationService

Methods:
+ get_all_stack_costs() → list[dict]
+ get_all_infra_costs() → list[dict]
+ create_stack_cost(**kwargs) → dict
+ create_infra_cost(**kwargs) → dict
+ update_stack_cost(id, **kwargs) → dict
+ update_infra_cost(id, **kwargs) → dict
+ delete_stack_cost(id) → bool
+ delete_infra_cost(id) → bool
+ apply_pricing_strategy(project_id, strategy_name) → dict
+ get_pricing_strategies() → list[dict]
```

#### Step 4.6 — `app/application/export_service.py`
```
Orchestrates: EstimationService + ProposalGenerator (move from proposal_generator.py)

Methods:
+ generate_proposal(project_id, output_path: str) → str  (returns file path)
+ get_proposal_data(project_id) → dict  (data needed for PDF)
```

#### Step 4.7 — Tests
- [ ] `tests/application/test_estimation_service.py` — fake repos, verify orchestration
- [ ] `tests/application/test_employee_service.py` — CRUD + cost calc
- [ ] `tests/application/test_project_service.py` — project + module management
- [ ] `tests/application/test_analytics_service.py` — variance + portfolio reports

**Fake repository pattern:**
```python
class FakeEmployeeRepository:
    def __init__(self): self.store = {}
    def get_by_id(self, emp_id):
        return self.store.get(emp_id)
    def create(self, name, role, base_salary, **kw):
        from types import SimpleNamespace
        emp = SimpleNamespace(id=len(self.store)+1, name=name,
                              role=role, base_salary=base_salary,
                              pf_pct=12, bonus_pct=8.33, leave_pct=4,
                              infra_pct=5, admin_pct=3)
        self.store[emp.id] = emp
        return emp
```

---

### PHASE 5: Refactor UI Layer (Week 5)

**Rule:** UI event handlers must be ≤ 10 lines — read input → call service → display result.

#### Step 5.1 — `app/ui/style/theme.py`
```
Move from ui_theme.py:
- Color palette constants (DARK_BG, ACCENT, etc.)
- Font definitions
```

#### Step 5.2 — `app/ui/style/stylesheet.py`
```
Move from ui_theme.py:
- generate_stylesheet() → str
- apply_theme(app: QApplication)
```

#### Step 5.3 — `app/ui/components/charts.py`
```
Move from ui_charts.py:
- All matplotlib chart widgets
- EstimationChartWidget, VarianceChartWidget, etc.
```

#### Step 5.4 — `app/ui/tabs/master_data_tab.py`
```
Extract from main_ui.py (master data section):
- Employee CRUD form + table
- StackCost / InfraCost CRUD form + table
- RegionMultiplier management
Inject: EmployeeService, PricingService
```

#### Step 5.5 — `app/ui/tabs/estimation_tab.py`
```
Extract from main_ui.py (estimation section):
- Project selector
- Module list with add/remove
- Run estimation button → shows result panel
- Stage distribution display
Inject: EstimationService, ProjectService
```

#### Step 5.6 — `app/ui/tabs/analysis_tab.py`
```
Extract from main_ui.py (analysis/variance section):
- Project picker for variance
- Variance report display
- Maintenance forecast table
- Chart integration (from charts.py)
Inject: AnalyticsService
```

#### Step 5.7 — `app/ui/tabs/proposal_tab.py`
```
Extract from main_ui.py (export/proposal section):
- Project picker
- PDF export button
- Preview panel (if any)
Inject: ExportService
```

#### Step 5.8 — `app/ui/tabs/sysconfig_tab.py`
```
Refactor ui_sysconfig.py:
- Complexity multiplier editor
- AppType multiplier editor
- Pricing strategy editor
- Industry preset manager
- SystemLookup (dynamic dropdowns) editor
Inject: PricingService (for multipliers too)
```

#### Step 5.9 — `app/ui/tabs/sop_tab.py`
```
Refactor ui_sop.py:
- SOP/help content display  
- No services needed (static content)
```

#### Step 5.10 — `app/ui/components/forms/`
```
employee_form.py  — EmployeeForm widget (used inside master_data_tab)
project_form.py   — ProjectForm widget
module_form.py    — ModuleForm widget
```

#### Step 5.11 — `app/ui/components/tables/`
```
employee_table.py  — QTableWidget wrapper for employees
project_table.py   — QTableWidget wrapper for projects
estimate_table.py  — QTableWidget wrapper for estimate breakdown
```

#### Step 5.12 — Tests  
- [ ] `tests/ui/test_main_window.py` — window creates without error
- [ ] `tests/ui/test_components.py` — components render, basic interaction

---

### PHASE 6: Wire Everything + Run.py Update (Week 6)

#### Step 6.1 — `app/ui/main_window.py`
```
Responsibilities:
- Create session
- Instantiate all repositories
- Instantiate all domain calculators
- Instantiate all services (inject repos + calcs)
- Instantiate all tabs (inject services)
- Wire tabs into QTabWidget
```

**Dependency injection wiring order:**
```python
# 1. Infrastructure
session = get_session()

# 2. Domain calculators
cost_calc = CostCalculator()
estimation_calc = EstimationCalculator()
variance_calc = VarianceCalculator()
maintenance_calc = MaintenanceCalculator()

# 3. Repositories
employee_repo = EmployeeRepository(session)
project_repo  = ProjectRepository(session)
estimate_repo = EstimateRepository(session)
multiplier_repo = MultiplierRepository(session)
pricing_repo  = PricingRepository(session)
preset_repo   = PresetRepository(session)
audit_repo    = AuditRepository(session)

# 4. Services
employee_service   = EmployeeService(cost_calc, employee_repo, audit_repo)
project_service    = ProjectService(project_repo, preset_repo, audit_repo)
estimation_service = EstimationService(cost_calc, estimation_calc, maintenance_calc,
                                       project_repo, estimate_repo, multiplier_repo,
                                       pricing_repo, audit_repo)
analytics_service  = AnalyticsService(variance_calc, estimate_repo, project_repo)
pricing_service    = PricingService(pricing_repo, multiplier_repo, preset_repo)
export_service     = ExportService(estimation_service)

# 5. UI tabs
master_data_tab  = MasterDataTab(employee_service, pricing_service)
estimation_tab   = EstimationTab(estimation_service, project_service)
analysis_tab     = AnalysisTab(analytics_service)
proposal_tab     = ProposalTab(export_service)
sysconfig_tab    = SysconfigTab(pricing_service)
sop_tab          = SopTab()
```

#### Step 6.2 — `run.py` update
```
Keep minimal:
- Import MainWindow
- Create QApplication
- Show window
- Execute
```

#### Step 6.3 — Backward-compat cleanup
```
After all UI wired and tested:
- Remove re-export shims from app/models.py (or keep for tests)
- Remove re-export shims from app/database.py (or keep for tests)
- Update any remaining imports in tests/
```

#### Step 6.4 — Full integration smoke test
- [ ] App launches without error
- [ ] All tabs render
- [ ] Employee CRUD works end-to-end
- [ ] Full estimation runs and displays results
- [ ] PDF export works
- [ ] System config saves and loads

---

### PHASE 7: Polish & Documentation (Week 7)

#### Step 7.1 — Type hints
- [ ] Add return types to all public functions
- [ ] Verify with `mypy app/` (target: 0 errors)

#### Step 7.2 — Docstrings
- [ ] Domain functions: formula description + param/return docs
- [ ] Service methods: use-case description
- [ ] Repository methods: brief description of query behavior

#### Step 7.3 — Test coverage report
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```
Targets:
- `app/domain/`: 100%
- `app/persistence/`: 80%+
- `app/application/`: 80%+
- `app/ui/`: 50%+

#### Step 7.4 — Update `README.md`
- [ ] New folder structure
- [ ] How to run
- [ ] How to run tests
- [ ] Architecture diagram

---

## Agent Prompts (Use These for Each Sub-Task)

### Advisor — before starting each phase
```
/plan phase-[N]-[description]

Context file: prompts/agent-tasks/001-full-architecture-migration-2026-03-04.md
Reference: .github/copilot-instructions.md

Phase N scope: [paste relevant phase section above]

Create implementation plan that:
1. Lists exact files to create (with paths)
2. Lists functions/classes per file
3. Confirms NO import rule violations
4. Identifies any risk to existing working behavior
```

### Generator — for implementation
```
/implement phase-[N]-[description]

Follow the layer rules from .github/copilot-instructions.md exactly:
- Domain: pure functions, zero imports from app layers
- Persistence: ORM + session only, import Domain if needed
- Application: orchestration, import Domain + Persistence
- UI: PyQt6 only, import Application only

Do not deviate from the plan. Create each file with full content.
```

### Reviewer — after each phase
```
/review phase-[N]

Validate per .github/copilot-instructions.md rules:

Import violations:
□ grep for "from app.persistence" in app/domain/ → must be 0 results
□ grep for "from app.ui" in app/domain/ → must be 0 results
□ grep for "from app.domain" in app/ui/ → must be 0 results
□ grep for "from app.persistence" in app/ui/ → must be 0 results
□ grep for "session.query" outside app/persistence/ → must be 0 results

Code quality:
□ All public functions have type hints
□ Repository methods return ORM objects internally, never return to UI
□ Services return plain dicts (no ORM objects)
□ UI event handlers ≤ 10 lines (read UI → call service → display)

Report: Critical | Warning | Info
```

### Test Generator — after each phase
```
/test phase-[N]

Generate pytest tests:

Domain (100% coverage): pure functions, no fixtures needed
Persistence (80%+): use conftest db_session fixture (in-memory SQLite)
Application (80%+): use Fake repositories (no real DB)
UI (50%): QApplication fixture, component-level only

All tests must pass with: python -m pytest tests/ -v
```

---

## Execution Order (Do NOT skip)

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
  ↑            ↑          ↑          ↑          ↑         ↑
Scaffold   Domain    Persist    Services    UI      Wire    Polish
(safe)     (pure)   (repos)    (orch.)  (refactor) (DI)  (quality)
```

**After each phase:**
1. Run `python -m pytest tests/ -v` → all green before continuing
2. Run app manually (`python run.py`) → no crashes before continuing

---

## Definition of Done

This task is complete when:

- [ ] All source code is in the correct layer (verified by import grep)
- [ ] No business logic in UI (`app/ui/`)
- [ ] No session/DB calls outside `app/persistence/`
- [ ] No PyQt6 imports outside `app/ui/`
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Coverage: `python -m pytest tests/ --cov=app --cov-report=term-missing`
  - domain: 100%
  - persistence: 80%+
  - application: 80%+
- [ ] App launches and all features work: `python run.py`
- [ ] `mypy app/` reports 0 errors
- [ ] README updated with new structure
