---
name: tester
description: Run automated tests and static analysis to verify application stability.
---

# Tester Skill

## Purpose
**Verify code correctness** by running automated tests and static analysis tools.

## When To Use
- After making changes to the codebase.
- When the user asks to "test" or "verify" the app.
- To detect regressions, bugs, or type errors.

## Core Behaviors
- **Run Tests**: Execute `pytest` for server-side tests.
- **Run Static Analysis**: Execute `mypy` for type checking.
- **Report Results**: Summarize pass/fail status and list any errors found.

## Tools
- `pytest`: For running unit and integration tests.
- `mypy`: For static type checking.

## Usage

### 1. Static Analysis (Mypy)
To check for type errors in the entire `app` directory:
```bash
python -m mypy app
```

To check a specific file:
```bash
python -m mypy path/to/file.py
```

### 2. Automated Tests (Pytest)
To run all tests:
```bash
python -m pytest
```

To run a specific test file:
```bash
python -m pytest path/to/test_file.py
```

## Output Format
When activated, provide:
1. **Understanding**: Summarize what you understand about the problem (e.g., "Found X critical type errors in Y files").
2. **Analysis**: Break down the issues found (e.g., "The errors fall into 3 categories: ...").
3. **Recommendation**: Suggest the best path forward with reasoning (e.g., "Fix critical bugs first, ignore strictness issues...").
4. **Plan**: Break down the chosen approach into actionable steps.
