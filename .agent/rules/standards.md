# Coding & Style Standards

Standardized naming, formatting, and error handling for consistency across the codebase.

## 1. Naming Conventions

### 1.1 Files
- Use `snake_case.py` (e.g., `cost_calculator.py`, `employee_repository.py`).
- Avoid abbreviations (e.g., `employee_repository.py` not `emp_repo.py`).
- Names should reflect entity + pattern (e.g., `estimation_service.py`, `estimation_tab.py`).

### 1.2 Classes
- Use `PascalCase` (e.g., `EmployeeService`, `MainWindow`).
- Suffix must denote the architectural pattern:
  - Domain: `XxxCalculator`
  - Persistence: `XxxRepository`
  - Application: `XxxService`
  - UI: `XxxTab`, `XxxForm`, `XxxWidget`

### 1.3 Functions & Methods
- Use `snake_case` with a **verb prefix** for clarity:
  - Domain: `calculate_xxx()`, `compute_xxx()`, `validate_xxx()`
  - Repository: `get_by_id()`, `get_all()`, `create()`, `update()`, `delete()`
  - Service: `estimate_project()`, `get_employee_with_costs()`
  - UI handlers: `_on_xxx_clicked()`, `_on_xxx_changed()`
  - UI setup: `_setup_ui()`, `_create_xxx_widget()`
- Avoid: `calc_mod_cost()` (abbreviations), `do_stuff()` (vague), `GetEmployeeData()` (PascalCase).

### 1.4 Variables
- Use descriptive `snake_case` (e.g., `total_labor_cost`, `region_multiplier`).
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PF_PCT`, `WORKING_DAYS_PER_MONTH`).
- Avoid: single-letter names (`x`, `e`), cryptic abbreviations (`tlc`, `rm`).

## 2. Type Hinting
- MANDATORY for all new/modified public functions and methods.
- Prefer explicit return types (e.g., `-> dict`, `-> float`, `-> list[Employee]`).
- Use `Optional[]` for nullable parameters.

## 3. Error Handling
- Always catch **specific** exceptions — never use bare `except:`.
- Provide meaningful error messages to the user.

```python
# ❌ BAD — bare except, vague message
try:
    result = service.calculate(data)
except:
    self.label.setText("Error")

# ✅ GOOD — specific exception, clear message
try:
    result = service.calculate(data)
except ValueError as e:
    self.label.setText(f"Invalid input: {e}")
except Exception as e:
    self.label.setText(f"Unexpected error: {e}")
```

## 4. General Style
- Maximize readability over cleverness.
- Keep methods focused: aim for < 25 lines per method.
- No unrelated refactors in the same task — keep changes minimal and focused.
- Docstrings required for complex logic in the Domain and Application layers.
- Private/internal methods should be prefixed with `_` (e.g., `_setup_ui()`).
