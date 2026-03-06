# Apeiron CostEstimation Pro - AI Agent Rules

**VERSION 2.0 (Common Edition)**  
This is the **Modular Source of Truth** for agents working in this repository.

---

## 1. Modular Rules Registry

Rules are split into specialized modules. Every agent MUST read and adhere to all of them:

| Module | File | Covers |
|--------|------|--------|
| **Common** | [common.md](rules/common.md) | Project identity, scope, folder structure, security, refactoring rules, Definition of Done. |
| **Architecture** | [architecture.md](rules/architecture.md) | 4-layer standard, dependency flow, injection, anti-patterns, quick reference. |
| **Coding & Style** | [standards.md](rules/standards.md) | Naming conventions, type hinting, error handling, readability. |
| **Testing** | [testing.md](rules/testing.md) | Pytest strategy, AAA pattern, layer-aware tests, fixtures, anti-patterns. |

---

## 2. Primary Architecture Reference

For deep technical examples, code walkthroughs, and original design rationale, see:
[.github/copilot-instructions.md](../.github/copilot-instructions.md)

---

## 3. Implementation Workflow

Agents must follow the structured pipeline defined in [orchestrator.md](orchestrator.md):

1. **Discovery**: Research requirements, remove ambiguity.
2. **Architecture/Planning**: Map the task to the 4 layers, produce `implementation_plan.md`.
3. **Execution**: Implement ONLY what is in the approved plan.
4. **Verification**: Validate against architecture rules and security basics.
5. **Testing**: Write/update tests covering success + failure paths.

---

## 4. Conflict Resolution

If any instruction across documents conflicts, the priority order is:
1. **User request** (always highest).
2. This `rules.md` and its sub-modules.
3. `.github/copilot-instructions.md`.

---

**Keep architecture clean, code standardized, and logic verified.**
