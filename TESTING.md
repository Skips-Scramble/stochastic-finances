# Testing Guide for `stochastic-finances`

## How Does Testing Currently Work in This App?

This project uses **Django's built-in test runner** (based on Python's `unittest` framework). All the tests live in one file:

```
pages/tests.py
```

There are also two **standalone manual scripts** in the root of the project (`test_interest_fields.py` and `test_override.py`) — these are *not* part of the automated test suite. They're one-off debugging scripts that you run by hand when you want to poke at a specific thing.

### What Does the Test Suite Actually Test?

The tests in `pages/tests.py` cover the core financial calculation logic:

| Test Class | What It Checks |
|---|---|
| `ConservativeRetirementRateTests` | Market interest rate "glide path" — rate should step down toward 5% as you approach age 90 |
| `PerAccountConservativeRateToggleTests` | Per-account toggle for conservative rates on/off |
| `PerAccountInterestRateCsvTests` | Per-account interest rate overrides show up correctly in CSV export |
| `VarPerAccountInterestRateCsvTests` | Same as above but for the stochastic (random) scenario |
| `RetirementPensionTests` | Pension account payments start/stop at the right time, grow with inflation |
| `MedicalBillsBaseScenarioTests` | Medical bills toggle, inflation adjustment, effect on savings |
| `MedicalBillsRandomScenarioTests` | Medical bills in random scenarios, never negative, included in output DataFrame |

All test classes extend Django's `SimpleTestCase` — this variant does **not** hit a real database, which keeps tests fast and self-contained.

---

## How Does Testing Normally Work in a Django Project?

Django projects typically use one of two approaches:

### 1. Django's Own Test Runner (what this project uses)

- Write test classes that extend `django.test.TestCase`, `SimpleTestCase`, or `TransactionTestCase`.
- Run with: `python manage.py test`
- Django automatically finds any file named `tests.py` (or a `tests/` package) inside your apps.
- It spins up a temporary test database, runs your tests, then tears everything down.

### 2. pytest-django (popular alternative)

- Install `pytest` and `pytest-django`.
- Add a `pytest.ini` (or `[tool.pytest.ini_options]` block in `pyproject.toml`) pointing at your Django settings.
- Run with: `pytest`
- This project has `pytest` listed as a dev dependency in `pyproject.toml` but has **not configured pytest-django**, so plain `pytest` will **not** work for the Django tests right now (see below).

---

## Can You Invoke pytest Directly?

**Not for the Django tests — at least not without extra setup.**

`pytest` is installed (it's in `pyproject.toml` under `[tool.poetry.group.dev.dependencies]`) but `pytest-django` is not installed and there is no `[tool.pytest.ini_options]` block setting `DJANGO_SETTINGS_MODULE`. If you run `pytest` by itself it will either find nothing or fail to boot Django.

The two root-level scripts (`test_interest_fields.py` and `test_override.py`) *do* manually call `django.setup()` at the top, so you can run those directly with Python — but they're not real test suites (no assertions, just `print` statements).

**Bottom line:** Use `python manage.py test` — it's the supported, working way.

---

## Step-by-Step: How to Run the Tests

### Prerequisites — install dependencies

If you're using Poetry (recommended):

```bash
poetry install          # installs everything in pyproject.toml
poetry shell            # activates the virtual environment
```

If you're using pip instead:

```bash
pip install -r requirements.txt
pip install crispy-bootstrap4 "django-allauth>=0.60" "django-debug-toolbar==4.*"
```

### Run database migrations (first time only)

```bash
python manage.py migrate
```

### Run all tests

```bash
python manage.py test pages.tests
```

You should see output like:

```
..............................
----------------------------------------------------------------------
Ran 30 tests in 4.123s

OK
```

If you see `OK` — everything passed. If you see `FAIL` or `ERROR`, the output will tell you exactly which test failed and why.

### Run a single test class

```bash
python manage.py test pages.tests.RetirementPensionTests
```

### Run a single test method

```bash
python manage.py test pages.tests.RetirementPensionTests.test_pension_is_in_retirement_list
```

### Run with more verbose output (see each test name as it runs)

```bash
python manage.py test pages.tests --verbosity=2
```

---

## Run the Linter

This project uses **Ruff** for linting and formatting.

```bash
# Check for lint issues
ruff check

# Check a specific file
ruff check pages/base_scenario.py

# Auto-fix fixable lint issues
ruff check --fix

# Format code
ruff format
```

Ruff also runs automatically on every commit via the pre-commit hooks defined in `.pre-commit-config.yaml`. If you commit and it fails, fix the issues and commit again.

---

## Run the Manual Debug Scripts (optional)

These scripts in the project root are *not* part of the test suite — they're quick sanity checks a developer wrote to inspect model fields:

```bash
# Test that model fields were renamed correctly
python test_interest_fields.py

# Test that interest rate override logic works in isolation
python test_override.py
```

These just print output — you read it with your eyes to confirm things look right.

---

## Running the App Locally

To start the dev server and use the app in a browser:

```bash
python manage.py migrate          # set up the database
python manage.py createsuperuser  # create an admin user
python manage.py runserver        # start the server
# Open http://127.0.0.1:8000 in your browser
```

---

## Quick Reference Cheat Sheet

| Task | Command |
|---|---|
| Run all tests | `python manage.py test pages.tests` |
| Run one test class | `python manage.py test pages.tests.ClassName` |
| Run one test method | `python manage.py test pages.tests.ClassName.test_method_name` |
| Verbose test output | `python manage.py test pages.tests --verbosity=2` |
| Lint code | `ruff check` |
| Auto-fix lint issues | `ruff check --fix` |
| Format code | `ruff format` |
| Start dev server | `python manage.py runserver` |
