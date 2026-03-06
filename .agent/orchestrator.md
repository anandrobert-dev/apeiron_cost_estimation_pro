# AI Orchestrator

This file defines the execution pipeline and authority rules for all AI agents.

---

## System States

1. DISCOVERY
   - Active Agent: requirements_analyst
   - Purpose: Remove all ambiguity.
   - Exit Condition: All clarifications answered.

2. ARCHITECTURE
   - Active Agent: advisor
   - Purpose: Produce implementation_plan.md.
   - Exit Condition: Plan approved.

3. EXECUTION
   - Active Agent: generator
   - Purpose: Implement ONLY what is in implementation_plan.md.
   - Restriction: Cannot modify architecture or deviate from plan.
   - Exit Condition: All checklist items complete.

4. VERIFICATION
   - Active Agent: reviewer
   - Purpose: Validate security, performance, pattern adherence.
   - Exit Condition: No critical issues.

5. TESTING
   - Active Agent: test_generator
   - Purpose: Write AAA tests and validate edge cases.
   - Exit Condition: Tests cover success + failure paths.

---

## Hard Transition Rules

- Cannot enter ARCHITECTURE without DISCOVERY approval.
- Cannot enter EXECUTION without ARCHITECTURE plan.
- Cannot skip VERIFICATION.
- Cannot skip TESTING.
- Reviewer has veto over Generator.
- Advisor has veto over architectural change.

---

## Forbidden Actions

- Generator cannot create new architecture patterns.
- Reviewer cannot rewrite code.
- Advisor cannot implement code.
- Test Generator cannot change business logic.
