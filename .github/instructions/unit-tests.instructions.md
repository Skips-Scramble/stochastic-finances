---
description: "Use when creating or modifying unit tests in this Django repository. Enforces consistent test structure, naming, fixtures, and assertion quality."
name: "Unit Test Guardrails"
applyTo:
  - "**/tests/**/*.py"
  - "**/test_*.py"
  - "**/*tests.py"
---
# Unit Test Guardrails

## Objective
Write focused, deterministic unit tests that validate business behavior and fail for clear reasons.

## Required Standards
- Prefer small, behavior-focused tests with one clear assertion objective.
- Keep arrange, act, assert phases explicit and readable.
- Use descriptive test names that explain expected behavior and condition.
- Add a simple comment directly above each test function definition explaining what the test validates.
- Validate meaningful outcomes, not only type checks or trivial truthiness.
- Keep tests independent and order-agnostic.

## Project Conventions
- Use pytest only. Do not create Django `SimpleTestCase` or `TestCase` classes for new unit tests.
- Prefer plain pytest test functions and pytest fixtures.
- Follow existing filename patterns: `test_*.py` or app-level `tests.py`.
- Prefer deterministic inputs over randomness; if randomness is unavoidable, set a seed and assert stable invariants.

## Do Not
- Do not make network calls, external API calls, or real file system side effects.
- Do not rely on wall-clock timing, sleeping, or non-deterministic ordering.
- Do not add broad integration flow checks to unit test files.
- Do not silently swallow exceptions in tests.

## Assertions and Coverage Quality
- Assert behavior at boundaries and edge cases, not only happy paths.
- Prefer exact equality comparisons (`==`) for expected outcomes when deterministic values are available.
- Avoid less-than and greater-than assertions unless the requirement is explicitly range-based.
- Include at least one negative or edge condition for each new behavior introduced.
- If a bug is being fixed, add a regression test that fails before the fix and passes after.

## Implementation Checklist
1. Identify unit under test and expected behavior contract.
2. Add tests near the closest existing test module.
3. Keep fixtures minimal and local to the test scope.
4. Ensure test names describe scenario plus expected outcome.
5. Run the smallest relevant test subset first, then broader suite as needed.

## Validation Commands
- Targeted pytest run: `pytest -q <test_file_or_nodeid>`
- Pytest subset: `pytest -q tests`
