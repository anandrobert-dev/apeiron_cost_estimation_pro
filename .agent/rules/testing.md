# Testing Standards

Verification strategy for application stability and correctness.

## 1. Testing Framework
- Use **Pytest** for all test suites.
- Baseline command: `python -m pytest tests/ -v`.

## 2. Layer-Aware Strategy
Tests MUST be organized by the layer they verify:

| Layer           | Directory               | Dependencies    | Notes                                     |
|-----------------|-------------------------|-----------------|-----------------------------------------  |
| **Domain**      | `tests/domain/`         | None            | Pure logic, zero mocks. Aim for 100%.     |
| **Persistence** | `tests/persistence/`    | In-memory SQLite | Repository CRUD behavior.                |
| **Application** | `tests/application/`    | Fakes/Mocks     | Services with injected fake repositories. |
| **UI**          | `tests/ui/`             | Fake Services   | Minimal: widget creation, signal/slot.    |
| **Backward-compat** | `tests/test_logic.py` | Varies        | Legacy shim tests (keep passing).        |

## 3. Test File Naming
- Mirror the source file path: `app/domain/cost_calculator.py` → `tests/domain/test_cost_calculator.py`.
- Prefix all test files with `test_`.

## 4. Fixtures & Conftest
- Shared fixtures (e.g., `db_session`, `in_memory_engine`) live in `tests/conftest.py`.
- Layer-specific fixtures can live in their sub-directory's `conftest.py`.

## 5. AAA Pattern
All tests should follow the **Arrange-Act-Assert** pattern:

```python
def test_hourly_cost_calculation():
    # Arrange
    base_salary = 100_000
    pf_pct = 12.0

    # Act
    result = compute_hourly_from_salary(base_salary, pf_pct=pf_pct)

    # Assert
    assert result["hourly_cost"] > 0
    assert isinstance(result["real_monthly_cost"], float)
```

## 6. Testing Anti-Patterns

```python
# ❌ BAD — No assertions
def test_something():
    service.do_something()  # What are we verifying?

# ❌ BAD — Testing implementation, not behavior
def test_service():
    service.repo.session.query.assert_called_once()  # Brittle!

# ✅ GOOD — Test behavior and outputs
def test_service_returns_valid_cost():
    result = service.estimate_project(project_id=1)
    assert result["total_cost"] > 0
```

## 7. Minimum Expectations
- Every new feature MUST have corresponding tests.
- Every bug fix MUST have a regression test.
- Coverage should not decrease after a task.
- All existing tests MUST remain passing.
