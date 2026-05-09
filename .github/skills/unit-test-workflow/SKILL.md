---
name: unit-test-workflow
description: "Design and write high-quality Python unit tests with consistent structure and guardrails. Use for test generation, test refactoring, regression tests, and edge-case coverage in this Django project."
argument-hint: "Target module or behavior to test"
user-invocable: true
---

# Unit Test Workflow

## When To Use
- You need to create new unit tests for a module, function, class, or bug fix.
- You want test additions to follow the same style and rigor every time.
- You need a repeatable checklist for deterministic and high-signal tests.

## Inputs Expected
- Module or symbol under test.
- Behavior contract and key edge cases.
- Whether database access is required.

## Procedure
1. Determine scope:
   - Unit-only behavior, no database: use `SimpleTestCase`.
   - Unit behavior with model/database logic: use `TestCase`.
2. Build a minimal scenario matrix:
   - Happy path.
   - Boundary condition.
   - Negative or failure condition.
3. Implement tests with clear names:
   - `test_<behavior>_when_<condition>`
4. Keep setup local and minimal:
   - Avoid over-shared fixtures unless they reduce duplication without hiding intent.
5. Validate quickly:
   - Run targeted tests first.
   - Expand to broader suite if changed behavior has wider impact.

## Output Contract
- New or updated test file in existing project structure.
- Deterministic assertions that verify behavior, not internals.
- Brief note of what behavior is now protected from regression.

## Quality Bar
- Each newly tested behavior has at least one edge or negative test.
- No real external calls or unstable timing dependencies.
- Tests are isolated and can run independently in any order.
