# Task: Fix Employee Form Fields Height Compress Issue

## Original Request
"can you see here, employee form's field's are too small in height when application size is small. this is wrong. they should be properly visible regardless of what app's view size is. please follow @[.agent/workflows/new-task.md] and @[.agent/rules.md] 100% and create a proper prompt file with a plan to fix this bug."

## Task Analysis

The issue is a UI layout squishing bug. In `app/ui/tabs/master_data_tab.py`, the `Add Employee` form (`QGroupBox` with `QFormLayout`) competes for vertical space with the `QTableWidget` below it. When the application window height shrinks, PyQt6 compresses the form fields instead of maintaining their readable minimum height and letting the table absorb the resize or scrolling. 

To fix this, we need to apply proper `MinimumHeight` constraints to the input fields or the `QGroupBox` itself, and/or adjust the stretch factors on the main `QVBoxLayout` so that the table takes the flexible space (`stretch=1`) and the form takes only its required space (`stretch=0`).

### Layer Mapping
- [ ] **Domain Layer** (Pure logic)
  - [ ] Affected files/functions: None
  - [ ] Input: N/A
  - [ ] Output: N/A

- [ ] **Persistence Layer** (Data access)
  - [ ] Affected repositories: None
  - [ ] New tables/fields?: No
  - [ ] Query changes?: No

- [ ] **Application Layer** (Orchestration)
  - [ ] Service changes: None
  - [ ] New use cases?: No

- [x] **UI Layer** (Display)
  - [x] UI/component changes: Apply minimum height to form fields/groupbox and fix stretch factors in `app/ui/tabs/master_data_tab.py`. Also apply similar fixes to the Stack Costs and Infra Costs tabs if they suffer from the same issue.
  - [ ] Event handlers needed?: No

### Dependencies
- [ ] Will this affect other layers? No.
- [ ] Any circular dependency risk? No.
- [x] Does it violate `.github/copilot-instructions.md` import rules? No, it's pure presentation layer changes.

### Assumptions
- [x] The fix should simply enforce minimum heights and proper layout stretching so the fields remain legible at minimum window sizes.
- [x] We should proactively apply this same layout fix to the "Stack Costs" and "Infrastructure" sub-tabs in the same file since they share identical layout patterns and likely have the same bug.

---

## Implementation Checklist (Standard Flow)

### Layer 1: Domain (Pure Logic)
*No changes required.*

### Layer 2: Persistence (Data Access)
*No changes required.*

### Layer 3: Application (Orchestration)
*No changes required.*

### Layer 4: UI (Display & Events)
- [ ] Component file: `app/ui/tabs/master_data_tab.py`
  - Modify `_build_employee_subtab()`: Add minimum heights to inputs or groupbox, adjust layout stretches.
  - Modify `_build_stack_subtab()`: Replicate layout fix.
  - Modify `_build_infra_subtab()`: Replicate layout fix.
- [ ] Tests: `tests/ui/test_components.py`
  - Verify if existing UI tests still pass. Add a basic rendering assertion if needed.

### Layer 5: Integration
- [ ] Manual smoke test to resize the window and verify forms do not compress excessively.
