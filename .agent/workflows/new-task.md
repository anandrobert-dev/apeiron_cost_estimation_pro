---
description: Step-by-step workflow for handling new task requests (Desktop Edition - PyQt6 + Clean Architecture)
---

# AI Task Management Workflow - Apeiron CostEstimation Pro

Use this workflow when starting ANY new feature, bug fix, or refactoring. Trigger with `/new-task`.

**Architecture Reference:** `.github/copilot-instructions.md`

---

## When to Use This Workflow

### ✅ USE for:
- New features (estimations, reports, etc.)
- Database schema changes (Models in Persistence)
- Business logic changes (Domain, Application layers)
- Refactoring across layers (moving logic up/down)
- Adding new UI tabs or components
- Any task with 2+ files or 3+ functions

### ❌ SKIP for (do directly):
- Quick typo fixes
- Comment updates
- Single-file, single-function fixes
- Documentation only

---

## Task File Naming

**Location:** `prompts/agent-tasks/[XXX]-[name]-[YYYY-MM-DD].md`

**Numbering:** 3-digit, zero-padded (001, 002, 099)

**How to number:**
1. Check `prompts/agent-tasks/` folder
2. Find highest number
3. Increment by 1
4. Use format: `001-file-upload-2026-03-04.md`

---

## WORKFLOW STEPS (DO NOT SKIP ANY)

### Phase 1: Understanding & Clarifications

1.  **Receive user request**
2.  **READ `.github/copilot-instructions.md` sections relevant to task:**
    - General features → Read "Layer Responsibilities" section
    - Domain logic changes → Focus "Domain Layer" rules
    - Database changes → Focus "Persistence Layer" rules  
    - UI changes → Focus "Presentation Layer" rules
    - Service/orchestration → Focus "Application Layer" rules
    - Testing → Focus "Testing Strategy"
3.  **Create agent-task file** with structure below
4.  **Self-review** against architecture rules
5.  **Ask clarifications** if needed (using questions below)

---

### Phase 2: Clarifications Format

**For multiple choice questions:**
```
I need to clarify [topic]:

A) Option 1 - [detailed description]
B) Option 2 - [detailed description]  
C) Option 3 - [detailed description]
D) Other - [let me know if none fit]

Which approach should we take?
```

**For open-ended questions:**
```
I need to understand [specific topic]:

Question: [Your concrete question]

Based on the task, [explain why this matters].
```

**Common clarifications:**
- Which layer should this logic belong to?
- Should this be cached or computed on-demand?
- Does this change affect multiple services?
- Is this user-facing or internal logic?

---

### Phase 3: Create Agent Task File

**File structure:**

```markdown
# Task: [Clear task title]

## Original Request
[Copy user's exact request]

## Task Analysis

### Layer Mapping
- [ ] **Domain Layer** (Pure logic)
  - [ ] Affected files/functions
  - [ ] Input: [what data?]
  - [ ] Output: [what result?]

- [ ] **Persistence Layer** (Data access)
  - [ ] Affected repositories
  - [ ] New tables/fields?
  - [ ] Query changes?

- [ ] **Application Layer** (Orchestration)
  - [ ] Service changes
  - [ ] New use cases?

- [ ] **UI Layer** (Display)
  - [ ] UI/component changes
  - [ ] Event handlers needed?

### Dependencies
- [ ] Will this affect other layers?
- [ ] Any circular dependency risk?
- [ ] Does it violate `.github/copilot-instructions.md` import rules?

### Assumptions
- [ ] [List your assumptions]
- [ ] [Will clarify these with user]

---

## Implementation Checklist (Standard Flow)

### Layer 1: Domain (Pure Logic)
- [ ] File: `app/domain/xxx.py`
- [ ] Functions/Classes: [list them]
- [ ] Tests: `tests/domain/test_xxx.py`
  - [ ] Happy path
  - [ ] Edge cases
  - [ ] Error conditions

### Layer 2: Persistence (Data Access)
- [ ] Repository file: `app/persistence/repositories/xxx_repository.py`
- [ ] Methods: [CREATE, READ, UPDATE, DELETE operations]
- [ ] Tests: `tests/persistence/test_xxx_repository.py`
  - [ ] CRUD operations
  - [ ] Error handling (404, unique constraint, etc.)

### Layer 3: Application (Orchestration)
- [ ] Service file: `app/application/xxx_service.py`
- [ ] Methods: [use cases this service provides]
- [ ] Tests: `tests/application/test_xxx_service.py`
  - [ ] Use fakes, not real repos
  - [ ] All workflows

### Layer 4: UI (Display & Events)
- [ ] Component file: `app/ui/[tabs|components]/xxx.py`
- [ ] Event handlers: [list them]
- [ ] Tests: `tests/ui/test_xxx.py` (minimal, component level)

### Layer 5: Integration
- [ ] Dependency injection wiring (main_window.py)
- [ ] All imports verified (no violations)
- [ ] Type hints added (`mypy` clean)
- [ ] Manual smoke test

---

## Agent Prompts (Use These Exactly)

### For Advisor (Planning Phase)
```
/plan [task-title]

Original request: [user request]

Layer analysis:
- Domain changes: [Y/N] → [what]
- Persist changes: [Y/N] → [what]
- App changes: [Y/N] → [what]
- UI changes: [Y/N] → [what]

Create an implementation_plan.md that:
1. Shows exactly which files to create/modify
2. Lists all functions/methods per layer
3. Confirms NO import rule violations from `.github/copilot-instructions.md`
```

### For Generator (Implementation Phase)
```
/implement [task-number]

File: [implementation_plan.md location]

Execute the plan EXACTLY as written.
- Create files in correct folders per layer
- Use provided code examples from `.github/copilot-instructions.md`
- Follow naming conventions (file, class, function, variable)
- Do not skip a layer
- Do not deviate from the plan
```

### For Reviewer (Verification Phase)
```
/review [task-number]

Check the implementation for:

Layer Isolation:
- [ ] No UI imports in Domain/Persistence/Application
- [ ] No Persistence imports in UI
- [ ] No circular dependencies
- [ ] Correct import flow: UI→App→{Domain, Persist}

Code Quality:
- [ ] Run mypy: type hints correct
- [ ] All public functions have docstrings
- [ ] Naming follows conventions
- [ ] Error handling present

Architecture Adherence:
- [ ] Services take dependencies (injected)
- [ ] Domain functions pure (no side effects)
- [ ] Repositories only in Persistence layer
- [ ] UI returns plain dicts (not ORM objects)

Security:
- [ ] Input validation present
- [ ] SQL injection prevented (via ORM)
- [ ] No sensitive data in logs

Report findings as Critical/Warning/Info
```

### For Test Generator (Testing Phase)
```
/test [task-number]

Write pytest tests following AAA pattern:

1. Domain layer (100% coverage)
   - Test all pure functions
   - Use fakes for external dependencies
   - File: tests/domain/test_xxx.py

2. Persistence layer (80%+ coverage)
   - Test CRUD operations
   - Use in-memory SQLite (conftest fixture)
   - File: tests/persistence/test_xxx_repository.py

3. Application layer (80%+ coverage)
   - Test services with fake repos
   - File: tests/application/test_xxx_service.py

4. UI layer (50%+ - minimal)
   - Component integration only
   - File: tests/ui/test_xxx.py

All tests must pass. Coverage targets:
- Domain: 100%
- Persistence: 80%+
- Application: 80%+
- UI: 50%+
```

---

## Example Task Files

### Example 1: New Estimation Feature

```markdown
# Task: Add SaaS Complexity Estimator

## Original Request
Add a tool to estimate complexity for SaaS products based on features

## Task Analysis

### Layer Mapping

- **Domain Layer** (Pure logic)
  - [ ] `app/domain/saas_estimator.py` - Calculate SaaS complexity score
  - [ ] Input: feature list (strings)
  - [ ] Output: complexity level (string) + confidence (float)

- **Persistence Layer** (Data access)
  - [ ] `app/persistence/repositories/saas_preset_repository.py` - Store SaaS templates
  - [ ] New table: `saas_templates` (name, features, complexity)

- **Application Layer** (Orchestration)
  - [ ] `app/application/saas_service.py` - Run full estimation with presets
  - [ ] Methods: `estimate_saas_project()`, `get_saas_templates()`

- **UI Layer** (Display)
  - [ ] `app/ui/components/saas_form.py` - UI form to input features
  - [ ] `app/ui/tabs/estimation_tab.py` - Add SaaS section

### Dependencies
- [x] No circular dependencies
- [x] Follows import rules (UI→App→{Domain,Persist})

## Implementation Checklist

### Domain
- [ ] `app/domain/saas_estimator.py` - CostEstimator class
- [ ] test: `tests/domain/test_saas_estimator.py`

### Persistence
- [ ] DB migration (alembic) - add saas_templates table
- [ ] `app/persistence/repositories/saas_repository.py`
- [ ] test: `tests/persistence/test_saas_repository.py`

... [continue with all layers]
```

---

## Execution Checklist

Before marking phase complete:

- [ ] **DISCOVERY:** All clarifications answered, user approved layer mapping
- [ ] **ARCHITECTURE:** Plan created, no violations detected, user approved
- [ ] **EXECUTION:** All checklist items complete, code compiles, no import errors
- [ ] **VERIFICATION:** mypy clean, security checks passed, patterns verified
- [ ] **TESTING:** All tests pass, coverage targets met

---

## When to Loop Back

If during any phase you find:

| Find | Action | Loop To |
|------|--------|---------|
| Unclear scope | Ask more questions | DISCOVERY |
| Layer violation in plan | Replan approach | ARCHITECTURE |
| Plan needs change mid-code | Stop and replan | ARCHITECTURE |
| Test shows logic bug | Fix code then re-test | TESTING |
| Security issue found | Fix and re-verify | VERIFICATION |

**KEY:** Never try to "patch" architectural issues. Always loop back to root cause.

---

## Quick Reference Checklist

Use before you start:

```
□ Task file created (prompts/agent-tasks/XXX-*.md)
□ `.github/copilot-instructions.md` read (relevant sections)
□ Layer mapping clear (Domain/Persist/App/UI assignments)
□ Clarifications asked (if ambiguous)
□ User approved before ARCHITECTURE phase
□ Plan shows no violations (imports, dependencies)
□ User approved plan before EXECUTION phase
□ All phases completed (D→A→E→V→T)
□ All tests passing
```

