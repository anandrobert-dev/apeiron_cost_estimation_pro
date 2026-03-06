---
name: reviewer
description: Quality gatekeeper - architecture validation, security checks, and code consistency enforcement
---

# Reviewer Skill - Architecture & Quality Guardian

## Purpose

**STOP architectural violations before they become problems.** Validate that code follows clean architecture rules BEFORE Generator finishes.

**This is the ACCESS POINT between EXECUTION and VERIFICATION phases.**

---

## When To Use

### ✅ USE for:
- After Generator completes (before tests)
- Validating architecture integrity
- Checking security vulnerabilities  
- Verifying code patterns match examples
- Detecting circular dependencies
- Type checking with `mypy`
- Code consistency & naming

### ❌ DON'T use for:
- Rewriting code (report issues, don't fix)
- Validating business logic correctness (that's domain logic's job)
- Bug hunting in algorithms (report, don't fix)
- Approving architectural changes (that's Advisor's domain)

---

## CRITICAL: Layer Violation Checklist

**RED FLAGS - VET

O GENERATOR IMMEDIATELY:**

### ❌ Import Violations

```python
# ❌ VETO if found in UI layer:
from app.domain.cost_calculator import CostCalculator
from app.persistence.repositories import EmployeeRepository

# ❌ VETO if found in Domain:
from app.persistence.models import Employee
from app.ui.main_window import MainWindow

# ❌ VETO if found in Persistence:
from app.ui.components import SomeWidget
from app.application.services import SomeService

# ✅ ALLOWED:
# In UI: from app.application.xxx_service import XxxService
# In App: from app.domain.xxx import Xxx; from app.persistence.repos import XxxRepo
# In Domain: No app-layer imports at all
```

**Action:** If any FORBIDDEN import found:
1. **VETO the code**
2. **Report** which files violate (don't fix)
3. **Ask Generator to fix** before proceeding

### ❌ Circular Dependencies

```
# ❌ VETO:
Domain → Persistence → Application → UI → Domain (cycle!)

# ✅ ALLOWED:
Domain ← Persistence ← Application ← UI (one-way flow only)
```

**Action:** Use `mypy` and visual inspection:
```bash
mypy app/  # Check for circular imports
```

### ❌ Database Access Outside Persistence

```python
# ❌ VETO - DB in Application:
class EstimationService:
    def estimate(self):
        emp = self.session.query(Employee)...  # ❌ Direct DB query

# ✅ GOOD - Only in Repository:
class EmployeeRepository:
    def get_by_id(self, emp_id):
        return self.session.query(Employee)...  # ✅ Correct
```

**Action:** Search for `session.query()`, `self.session`, `.commit()` outside `persistence/repositories/`

### ❌ CrossLayer Type Leakage

```python
# ❌ VETO - UI receives ORM object:
class EstimationService:
    def estimate(self):
        project = self.repo.get(1)
        return project  # ← ORM object to UI!

# ✅ GOOD - Transform to plain dict:
class EstimationService:
    def estimate(self):
        project = self.repo.get(1)
        return {
            "id": project.id,
            "name": project.name
            # ← Plain dict to UI
        }
```

**Action:** Check all service return values - should be plain dicts/lists, never ORM objects

---

## Review Checklist (RUN IN ORDER)

### Phase 1: Architecture Integrity (GATE)

```
□ Layer Isolation Check
  □ Run: grep -r "from app.domain" app/ui/ → Must be ZERO
  □ Run: grep -r "from app.persistence" app/ui/ → Must be ZERO
  □ Run: grep -r "from app.ui" app/domain/ → Must be ZERO
  □ Run: grep -r "from app.ui" app/persistence/ → Must be ZERO

□ Import Flow Diagram
  □ UI imports Application? ✅
  □ Application imports Domain/Persistence? ✅
  □ Domain imports anything app-related? ❌ VETO if yes
  □ Persistence imports Application? ❌ VETO if yes

□ Database Access
  □ session.query() only in app/persistence/repositories/? ✅
  □ Any DB access in app/application/? ❌ VETO if yes
  □ Any DB access in app/ui/? ❌ VETO if yes

□ Type Leakage
  □ All service returns are plain dicts/lists (not ORM)? ✅
  □ ORM models stay in persistence layer? ✅
```

**Decision:** 
- ✅ All passing → Continue to Phase 2
- ❌ Any failing → VETO code, report issues (don't fix)

---

### Phase 2: Type Safety (GATE)

```bash
# Run mypy
mypy app/ --strict

# Expected:
# 0 errors (or document why exceptions exist)
```

**Report:**
```
Type Check Results:
□ All type hints present
□ No "Any" types (except where documented)
□ All function signatures typed
□ All return types specified
```

**Decision:**
- ✅ Clean mypy → Continue to Phase 3  
- ⚠️ Warnings → Document, can continue
- ❌ Errors → VETO, must fix

---

### Phase 3: Security (GATE)

```
□ Input Validation
  □ All user inputs validated?
  □ Type hints enforced (mypy)?
  □ No eval() or exec()?

□ SQL Safety
  □ Using SQLAlchemy ORM (not string concatenation)? ✅
  □ Any SQL strings? ❌ VETO if yes

□ Sensitive Data
  □ No passwords in logs?
  □ No tokens in docstrings?
  □ No credentials in error messages?
```

---

### Phase 4: Code Consistency (GATE)

```
□ Naming Conventions (per `.github/copilot-instructions.md`)
  □ Files: snake_case (cost_calculator.py) ✅
  □ Classes: PascalCase (CostCalculator) ✅
  □ Functions: snake_case (calculate_cost) ✅
  □ Repositories: XXXRepository pattern ✅
  □ Services: XXXService pattern ✅

□ Docstrings
  □ All public functions/classes have docstrings?
  □ Format: """Description. Arguments: x (type). Returns: type."""

□ Error Handling
  □ All try/except blocks justified?
  □ Specific exceptions (not bare except)?
  □ Error messages clear?

□ Code Style
  □ Lines under 100 chars?
  □ Proper spacing/indentation?
  □ No unused imports?
```

---

### Phase 5: Pattern Adherence (INFO)

```
□ Domain Layer
  □ Functions pure (no side effects)?
  □ No instance state (or documented)?
  □ Math/logic self-contained?

□ Persistence Layer
  □ All queries in repositories?
  □ CRUD pattern applied?
  □ Base repository inherited?

□ Application Layer
  □ Services compose logic + persistence?
  □ Dependencies injected?
  □ Returns plain dicts?

□ UI Layer
  □ Event handlers thin (delegate to service)?
  □ No business logic in widgets?
  □ Dependency injected?
```

---

## Output Format

### Critical Issues (MUST FIX)
```
❌ CRITICAL: [Issue Name]
File: [path]
Line: [number]
Violation: [rule from `.github/copilot-instructions.md`]
Example: [show the problematic code]
Action Required: [what needs to change]

Example:
❌ CRITICAL: Layer Violation - UI importing Domain
File: app/ui/tabs/estimation_tab.py:34
Violation: "UI can only import Application layer"
Code: from app.domain.cost_calculator import CostCalculator
Action: Remove this import. Use EstimationService instead.
```

### Warnings (SHOULD FIX)
```
⚠️ WARNING: [Issue Name]
File: [path]
Line: [number]
Suggestion: [what's suboptimal]
Recommendation: [how to improve]

Example:
⚠️ WARNING: Missing Type Hint
File: app/domain/cost_calculator.py:15
Code: def calculate(total):  # No type hint
Recommendation: def calculate(total: float) -> float:
```

### Info (NICE TO HAVE)
```
ℹ️ INFO: [Note]
Example: "Consider adding docstring to clarify intent"
```

---

## Example Review Report

```markdown
# Code Review: estimation_service.py

## Summary
**Status:** ❌ BLOCKED - Layer violation found  
**Files Reviewed:** 2  
**Critical Issues:** 1  
**Warnings:** 2  
**Info:** 1  

## Critical Issues

❌ CRITICAL: Cross-Layer Import Violation
**File:** `app/application/estimation_service.py:5`
**Rule Violated:** Application can import Domain + Persistence, NOT UI
**Code:**
```python
from app.ui.components.cards import StatCard
```
**Fix:** Remove UI import. StatCard is UI's responsibility, not Service's.

---

## Warnings

⚠️ Missing Type Hints
**File:** `app/application/estimation_service.py:20`
**Code:**
```python
def estimate_project(self, modules):  # modules type?
```
**Fix:**
```python
def estimate_project(self, modules: list[dict]) -> dict:
```

⚠️ ORM Object Leak
**File:** `app/application/estimation_service.py:45`
**Code:**
```python
return project  # ← Returning ORM object!
```
**Fix:**
```python
return {
    "id": project.id,
    "name": project.name
}
```

---

## Info

ℹ️ Docstring Details
Consider adding parameter descriptions to `estimate_project()` method.

---

## Verdict

**BLOCK** until critical issue fixed. Resubmit for review.
```

---

## Common Issues & Fixes

| Issue | Detection | Fix |
|-------|-----------|-----|
| Domain importing DB | grep "from app.persistence" app/domain/ | Remove import, use function params |
| UI calling repository | grep "Repository" app/ui/ | Use Service instead |
| Missing type hints | mypy app/ | Add type: hints |
| ORM leak to UI | Search returns | Transform to dict |
| Circular import | mypy app/ | Move to lower layer |
| Business logic in UI | Review event handlers | Move to Domain/Service |

---

## Integration with Workflow

This skill aligns with **VERIFICATION phase** in orchestrator.md:

1. Generator completes implementation
2. Reviewer runs checklist
3. **If critical issues:** VETO → Generator fixes
4. **If warnings:** Report → Can continue with caveats
5. **If clean:** Approve → Test Generator starts
6. User can request changes throughout

**Success Criteria:**
- ✅ No architectural violations
- ✅ Type safe (mypy clean)
- ✅ Secure (validated)
- ✅ Pattern adherent
- ✅ Documented

