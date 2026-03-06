# Common Standards

Core project identity, scope boundaries, and guiding principles.

## 1. Project Profile
- **Product**: Apeiron CostEstimation Pro (proprietary to Koinonia Technologies).
- **Stack**: Python 3.11+, PyQt6, SQLAlchemy (SQLite), ReportLab, Matplotlib.
- **Form Factor**: Fully offline Desktop Application.
- **UI Themes**: Professional "Deep Blue" and "True Light".
- **Database Location**: `~/.apeiron_costpro/costpro.db` (auto-created on first run).
- **Entry Point**: `run.py`.

## 2. In Scope
- PyQt6 UI structure, tabs, components, and theming.
- Domain calculations (cost, effort, variance, maintenance).
- SQLAlchemy persistence with SQLite (repository pattern).
- Application service orchestration and dependency injection.
- PDF proposal generation (ReportLab) and analytics charts (Matplotlib).
- Pytest test suites for all layers.

## 3. Out of Scope (Unless User Explicitly Requests)
- API routes/endpoints (no FastAPI, Flask, etc.).
- JWT/OAuth authentication stacks.
- Async web server patterns.
- Cloud deployment or containerization.

## 4. Folder Structure

```
app/
├── domain/              # Pure business logic (no DB, no UI)
│   ├── cost_calculator.py
│   ├── estimation_calculator.py
│   ├── variance_calculator.py
│   ├── maintenance_calculator.py
│   └── constants.py
├── persistence/         # Data access (ORM models + repositories)
│   ├── database.py
│   ├── models.py
│   └── repositories/
├── application/         # Service orchestration (domain + persistence)
│   ├── estimation_service.py
│   ├── employee_service.py
│   ├── project_service.py
│   ├── analytics_service.py
│   ├── pricing_service.py
│   └── export_service.py
├── ui/                  # PyQt6 presentation layer
│   ├── main_window.py
│   ├── tabs/
│   ├── components/
│   └── style/
└── utils/               # Shared helpers (formatting, validation, exceptions)
    ├── formatting.py
    ├── validators.py
    ├── exceptions.py
    └── proposal_generator.py
```

## 5. Coding Principles
- **DRY (Don't Repeat Yourself)**: Abstract common logic into Services or Repositories.
- **Single Responsibility (SRP)**: Each class/module must have one clear purpose.
- **YAGNI (You Ain't Gonna Need It)**: Do not add functionality until explicitly requested.
- **KISS (Keep It Simple, Stupid)**: Prefer readable logic over clever, complex code.

## 6. Security & Safety
- No hardcoded secrets or credentials in code.
- Validate and sanitize user-controlled inputs.
- Avoid dangerous execution patterns (`eval`, `exec`, shell injection).
- Keep PDF/export file paths controlled and predictable.

## 7. Refactoring Rules
When moving, renaming, or removing fields or behaviors, agents MUST update **all** impacted layers:
1. SQLAlchemy model definitions (`persistence/models.py`).
2. Repository methods.
3. Service outputs and DTOs.
4. UI bindings, forms, and tables.
5. Tests and fixtures.

**Never leave stale field references.**

## 8. Definition of Done
A task is considered complete only when:
1. All functional requirements are met.
2. Architecture rules (4-layer) are strictly followed.
3. Code naming and style adhere to `standards.md`.
4. Tests (Pytest) cover the new/changed logic and pass successfully.
5. No regressions are introduced.
6. Changes are minimal, focused, and documented in commit-ready state.
