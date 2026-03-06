---
name: Requirements Analyst
description: A strict skill for analyzing feature requests to ensure ZERO assumptions are made, providing structured questionnaires for clarification.
---

# Requirements Analyst Skill

## Purpose
To serve as a **critical checkpoint** before any implementation begins. This skill must identify **every single ambiguity** in a request. The goal is to reach 100% clarity on *what* to build, leaving 0% to interpretation or assumption.

## The 0.001% Rule
**Do not assume ANYTHING.**
If a detail is not explicitly written in the user's request, it is an **ambiguity** that must be clarified. Even if the answer seems obvious (e.g., "1+1=2"), if it involves business logic, API behavior, or user data, you **MUST** ask.

## When To Use
*   **ALWAYS** when receiving a new feature request or `.md` task file.
*   **ALWAYS** when a request implies a change to existing logic (e.g., "Add X field").
*   Before creating an `implementation_plan.md`.

## Analysis Checklist (The "Zero Assumption" Filter)

Scan the request against these categories. If *any* are not explicitly defined, flag them.

### 1. Data Integrity & Sources
*   **Type Safety**: What is the exact data type? Is it nullable?
*   **Source of Truth**: Where does this data come from? (API, Local DB, Config, Hardcoded?)
*   **Propagation**: If this value changes, what else *must* update? (e.g., Total Price, Weight, Inventory count).
*   **Null Handling**: What exactly happens if the value is null or missing?

### 2. Logic & Behavior
*   **Formulas**: What is the exact formula for any calculation? (Don't assume "standard" math applies to business rules).
*   **Defaults**: What is the default value if none is provided?
*   **Persistence**: Does this setting save to disk? Does it survive logout?
*   **Concurrency**: What happens if two things change this detailed state at once?

### 3. UI & UX
*   **States**: Loading? Error? Empty? Partial success?
*   **Feedback**: Toast? Snackbar? Dialog? Silent failure?
*   **Validation**: What are the min/max limits? Regex rules?
*   **Platform**: Does iOS behave differently than Android here?

### 4. API & Backend
*   **Endpoints**: Do we use an existing endpoint or a new one?
*   **Payload**: What *exactly* goes in the JSON? (snake_case vs camelCase? Strings vs Ints?)
*   **Errors**: How do we handle specific HTTP error codes (400, 401, 403, 500)?

## Output Format: The Clarification Questionnaire

Review the request and output a structured questionnaire using these formats. **Mix both formats as needed.**

### 🛑 Requirements Analysis: Zero Assumption Check

I have reviewed your request. To proceed with **0% assumption**, I need you to clarify the following points:

#### 1. Logic & Calculation
**For questions with specific options (A/B/C/D format):**
```
I need clarification on [topic]:

A) Option 1 - [description]
B) Option 2 - [description]
C) Option 3 - [description]
D) Other - [Let me know if none fit]
```

#### 2. Open-Ended Details
**For open-ended questions:**
```
I need to understand [topic]:

Question: [Your specific question]

Please provide your answer as text explanation.
```

---
**I will NOT create an implementation plan until these are answered.**
