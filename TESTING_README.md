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

## What a Fully Functioning Website Should Test

For a production-ready Django app, you usually want a **test pyramid**:

1. **Unit tests** (many): Fast checks of isolated business logic.
2. **Integration tests** (some): Verify views/forms/models/auth/database work together.
3. **End-to-end (E2E) tests** (few): Simulate real user flows in a browser.
4. **Regression tests** (targeted): Lock in bug fixes so they never come back.
5. **Smoke tests** (small set): Quick "is the app alive" checks on core pages and actions.

### 1) Unit Tests (isolated logic)

What they are:
- Tests that avoid database/network and focus on deterministic logic.
- In this codebase, your scenario math in `pages/base_scenario.py` and `pages/random_scenario.py` is perfect for unit tests.

Examples you can implement (or expand, since you already have similar tests):
- Verify conservative market-rate glide path reaches 5% by age 90.
- Verify monthly interest conversion from a yearly override is mathematically correct.

Example (add to `pages/tests.py`):

```python
from django.test import SimpleTestCase

from pages.base_scenario import BaseScenario


class RateMathUnitTests(SimpleTestCase):
	def test_monthly_rate_matches_yearly_override(self):
		assumptions = {
			"birthdate": __import__("datetime").date(2000, 1, 1),
			"retirement_age_yrs": 65,
			"retirement_age_mos": 0,
			"add_healthcare": False,
			"medicare_coverage_type": "standard",
			"private_insurance_per_mo": None,
			"retirement_extra_expenses": 0,
			"base_savings": 50000,
			"base_saved_per_mo": 500,
			"base_savings_per_yr_increase": 0,
			"savings_lower_limit": 10000,
			"base_monthly_bills": 2000,
			"payment_items": [],
			"retirement_accounts": [
				{
					"retirement_type": "roth_ira",
					"base_retirement": 10000,
					"base_retirement_per_mo": 200,
					"base_retirement_per_yr_increase": 0,
					"interest_rate_per_yr": 6.0,
					"use_conservative_rates": True,
				}
			],
			"ss_incl": False,
			"base_rf_interest_per_yr": 1.0,
			"base_mkt_interest_per_yr": 8.0,
			"base_inflation_per_yr": 3.0,
			"add_medical_bills": False,
			"monthly_medical_bills": 0,
		}

		df = BaseScenario(assumptions=assumptions).create_base_df()
		yearly = df["roth_ira_yearly_mkt_interest"].iloc[0]
		monthly = df["roth_ira_monthly_mkt_interest"].iloc[0]

		expected_monthly = round((1 + yearly) ** (1 / 12) - 1, 6)
		self.assertAlmostEqual(monthly, expected_monthly, places=6)
```

### 2) Integration Tests (database + views + auth)

What they are:
- Tests that verify multiple layers working together (routing, login, model filtering, templates, etc.).
- Use `django.test.TestCase` so you get a real temporary test database.

Examples you can implement:
- Unauthenticated users are redirected to login for protected dashboards.
- Authenticated users only see their own input records (`created_by` scoping).

Example (new file: `pages/tests_integration.py`):

```python
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pages.models import GeneralInputsModel


class GeneralDashboardIntegrationTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user_a = user_model.objects.create_user(
			username="alice",
			email="alice@example.com",
			password="testpass123",
		)
		self.user_b = user_model.objects.create_user(
			username="bob",
			email="bob@example.com",
			password="testpass123",
		)

	def test_general_dashboard_requires_login(self):
		response = self.client.get(reverse("general_inputs_dashboard"))
		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response.url)

	def test_general_dashboard_only_shows_current_users_records(self):
		GeneralInputsModel.objects.create(
			birthdate=date(1990, 1, 1),
			retirement_age_yrs=65,
			retirement_age_mos=0,
			created_by=self.user_a,
		)
		GeneralInputsModel.objects.create(
			birthdate=date(1992, 1, 1),
			retirement_age_yrs=67,
			retirement_age_mos=0,
			created_by=self.user_b,
		)

		self.client.login(username="alice", password="testpass123")
		response = self.client.get(reverse("general_inputs_dashboard"))

		self.assertEqual(response.status_code, 200)
		rows = list(response.context["general_inputs"])
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0].created_by, self.user_a)
```

### 3) End-to-End (E2E) Tests (real user journey)

What they are:
- Browser-driven tests (Playwright/Selenium) that click through pages like a real user.
- Best for critical workflows, not every edge case.

Examples you can implement:
- Sign in -> create one active scenario per section -> run calculations -> confirm results page renders expected cards/graphs.
- Attempt to run calculations with missing active inputs -> confirm `non_active` page appears with the expected missing/multiple warnings.

Tip for this repo:
- Keep E2E scope small and focused on your "happy path" and one major failure path.
- Run E2E in CI only on pull requests or nightly to keep feedback fast.

### 4) Regression Tests (bug-fix locks)

What they are:
- A test written specifically because something previously broke.
- The goal is to ensure that exact bug never reappears.

Examples from this codebase area:
- Per-account `use_conservative_rates` missing from older records should default to `True`.
- Per-account override columns should appear in output DataFrames when an override is set.

Pattern to follow:
1. Recreate the bug input.
2. Assert the correct behavior.
3. Keep test name tied to the historical bug symptom.

### 5) Smoke Tests (fast confidence checks)

What they are:
- A tiny set of very fast tests that answer: "Is the app fundamentally up?"
- Usually run first in CI before slower test suites.

Examples you can implement:
- Home page (`/`) returns 200.
- Login page (`/accounts/login/`) returns 200.
- One authenticated dashboard route returns 200 for a logged-in user.

Example (new file: `pages/tests_smoke.py`):

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SmokeTests(TestCase):
	def test_home_page_loads(self):
		response = self.client.get(reverse("home"))
		self.assertEqual(response.status_code, 200)

	def test_login_page_loads(self):
		response = self.client.get(reverse("account_login"))
		self.assertEqual(response.status_code, 200)

	def test_general_dashboard_loads_for_authenticated_user(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username="smokeuser",
			email="smoke@example.com",
			password="testpass123",
		)
		self.client.login(username="smokeuser", password="testpass123")

		response = self.client.get(reverse("general_inputs_dashboard"))
		self.assertEqual(response.status_code, 200)
```

### Recommended Coverage Plan for This Repo

If you want a practical rollout plan:

1. Keep your existing financial-logic unit tests in `pages/tests.py`.
2. Add 5-10 integration tests around login protection, user data isolation, and calculations preconditions.
3. Add 3 smoke tests for homepage/auth/dashboard.
4. Add 1-2 E2E tests for the full scenario workflow.
5. Every time you fix a bug, add one regression test in the closest relevant test module.

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
