---
name: generator
description: Fast code implementation for daily coding, boilerplate, and pattern-based development
---

# Generator Skill

## Purpose
**Write code quickly** following an established plan. Prioritize speed and efficiency for implementation tasks.

## When To Use
- Daily coding tasks and boilerplate
- CRUD operations and repetitive patterns
- Scaffolding tests and test files
- Writing type definitions and interfaces
- Implementing code that follows existing patterns
- After a concrete plan exists (from Advisor phase)

## Core Behaviors

### DO
- Follow existing project patterns and conventions
- Generate code efficiently without over-engineering
- Create consistent, readable code structure
- Scaffold boilerplate quickly
- Match the existing code style of the project
- Iterate on suggestions when first attempt isn't perfect

### DON'T
- Make architectural decisions (use Advisor skill first)
- Assume code is secure without review
- Skip validation of business logic
- Trust generated code blindly for security-critical sections
- Overcomplicate simple implementations

## Output Format
When activated, provide:
1. **Implementation**: Clean, working code
2. **File Changes**: Clear indication of what files are created/modified
3. **Usage Notes**: Brief explanation of how to use the generated code

## Limitations (Be Aware)
- May not catch security vulnerabilities
- Does not validate business logic correctness
- May miss edge cases
- Requires Reviewer skill for quality assurance

## Example Prompts
- "Generate the CRUD endpoints for the User model"
- "Create a Bloc for managing pickup requests"
- "Scaffold unit tests for the AuthService"
- "Write the Widget for displaying order items"

## Integration with Workflow
This skill aligns with the **EXECUTION** mode in task boundaries:
- Follow the `implementation_plan.md` from Advisor phase
- Update `task.md` as items are completed
- Prepare code for Reviewer phase validation
