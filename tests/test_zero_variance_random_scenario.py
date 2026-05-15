"""Tests that RandomScenario with zero variance reproduces BaseScenario rate values.

Patching strategy
-----------------
- ``np.random.normal``  → always returns its first argument (the mean), eliminating
  all normal-distribution noise from bills, savings contributions, and market rates.
- ``random.randint``    → always returns 0, preventing the RF interest rate from
  drifting up or down between adjustment windows.

With those two patches the random scenario is fully deterministic.

Savings account
  var_monthly_rf_interest is derived from var_yearly_rf_interest using the same
  formula and precision (6 decimal places) as BaseScenario.monthly_rf_interest.
  Given zero bills and zero contributions, the savings growth loop reduces to
  identical arithmetic on both sides, so the two savings lists must be exactly equal.

Retirement accounts
  RandomScenario and BaseScenario now both round sampled yearly market rates to
  **6** decimal places, so the computed monthly rates are identical.  Given zero
  bills, zero contributions, and zero inflation, retirement account balances must
  also be exactly equal when variance is zero.
"""

import random
from datetime import date

import numpy as np
import pytest

from pages.base_scenario import BaseScenario
from pages.random_scenario import RandomScenario


# ── shared fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
# Assumptions with a traditional 401k for rate and per-account tests.
# Bills, contributions, and inflation are zero to isolate interest behaviour.
def zero_variance_assumptions_with_401k():
    return {
        "birthdate": date(1990, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 50000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
                "use_conservative_rates": False,
            }
        ],
        "ss_incl": False,
        "base_rf_interest_per_yr": 3.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }


@pytest.fixture
# Assumptions with no retirement accounts so that savings balance grows only
# through RF interest, with no retirement transfers feeding back into savings.
def zero_variance_assumptions_savings_only():
    return {
        "birthdate": date(1990, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 50000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 3.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }


@pytest.fixture
# Patch randomness to zero and return (RandomScenario, BaseScenario) for rate tests.
def zero_variance_scenario(zero_variance_assumptions_with_401k, monkeypatch):
    monkeypatch.setattr(np.random, "normal", lambda mean, std_dev: mean)
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    base = BaseScenario(assumptions=zero_variance_assumptions_with_401k)
    rand = RandomScenario(base_scenario=base)
    return rand, base


@pytest.fixture
# Patch randomness to zero and return (RandomScenario, BaseScenario) for savings
# balance tests; no retirement accounts so no cross-account transfers can occur.
def zero_variance_scenario_savings_only(
    zero_variance_assumptions_savings_only, monkeypatch
):
    monkeypatch.setattr(np.random, "normal", lambda mean, std_dev: mean)
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    base = BaseScenario(assumptions=zero_variance_assumptions_savings_only)
    rand = RandomScenario(base_scenario=base)
    return rand, base


# ── RF interest rate tests ─────────────────────────────────────────────────────


# With randint always returning 0 the adjustment factor is always 0, so no
# change is ever applied; every element must equal the scalar base RF rate.
def test_var_yearly_rf_interest_is_constant_at_base_rate_when_no_drift(
    zero_variance_scenario,
):
    rand, base = zero_variance_scenario
    assert all(r == base.yearly_rf_interest for r in rand.var_yearly_rf_interest)


# var_monthly_rf_interest is derived from var_yearly_rf_interest using the same
# formula and precision as BaseScenario.monthly_rf_interest; they must be equal.
def test_var_monthly_rf_interest_equals_base_monthly_rf_interest_when_no_drift(
    zero_variance_scenario,
):
    rand, base = zero_variance_scenario
    assert all(r == base.monthly_rf_interest for r in rand.var_monthly_rf_interest)


# ── market interest rate tests ─────────────────────────────────────────────────


# With np.random.normal returning its mean, the sampled yearly market rate for
# each month equals the conservative base rate exactly (both rounded to 6 decimal
# places), so the two lists must be identical.
def test_var_yearly_mkt_interest_equals_conservative_base_rates_when_zero_variance(
    zero_variance_scenario,
):
    rand, base = zero_variance_scenario
    assert rand.var_yearly_mkt_interest == base.conservative_yearly_mkt_interest


# With zero variance and use_conservative_rates=False every sampled yearly rate
# equals the flat base market rate rounded to 6 decimal places, matching the
# base scenario's _account_yearly_rate_list exactly.
def test_account_var_yearly_rate_equals_flat_base_rate_when_zero_variance(
    zero_variance_scenario,
):
    rand, base = zero_variance_scenario
    trad_401k = base.retirement_list[0]
    expected_rate = round(base.assumptions["base_mkt_interest_per_yr"] / 100, 6)
    account_rates = rand._account_var_yearly_rate_list(trad_401k)
    for month_index, rate in enumerate(account_rates):
        assert (
            rate == expected_rate
        ), f"Month {month_index}: expected {expected_rate}, got {rate}"


# With zero variance, zero bills, zero contributions, and shared 6-decimal rate
# precision, the 401k balance grows by identical arithmetic on both sides;
# the two balance lists must be identical element-for-element.
def test_var_trad_401k_balance_matches_base_exactly_when_zero_variance_no_bills(
    zero_variance_scenario,
):
    rand, base = zero_variance_scenario
    rand_trad_401k = rand.var_savings_retirement_account_list[3]
    base_trad_401k = base.savings_retirement_account_list[3]
    assert len(rand_trad_401k) == len(base_trad_401k)
    for month_index, (rand_value, base_value) in enumerate(
        zip(rand_trad_401k, base_trad_401k)
    ):
        assert (
            rand_value == base_value
        ), f"Month {month_index}: expected {base_value}, got {rand_value}"


# ── savings account balance test ───────────────────────────────────────────────


# With zero variance, zero bills, and no retirement accounts the savings loop
# on both sides reduces to: balance *= (1 + monthly_rf_interest).  Because
# var_monthly_rf_interest[i] equals monthly_rf_interest exactly (same precision,
# same value) and there are no retirement transfers that could diverge due to
# rate-rounding, the two savings lists must be identical element-for-element.
def test_var_savings_account_matches_base_savings_exactly_when_zero_variance_no_bills(
    zero_variance_scenario_savings_only,
):
    rand, base = zero_variance_scenario_savings_only
    rand_savings = rand.var_savings_retirement_account_list[0]
    base_savings = base.savings_retirement_account_list[0]
    assert len(rand_savings) == len(base_savings)
    for month_index, (rand_value, base_value) in enumerate(
        zip(rand_savings, base_savings)
    ):
        assert (
            rand_value == base_value
        ), f"Month {month_index}: expected {base_value}, got {rand_value}"


# Variable Medicare Part B and Part D premiums should only re-sample at January boundaries.
def test_var_medicare_premiums_resample_only_in_january(monkeypatch):
    """Validate stochastic Medicare premiums are re-sampled only at yearly step points."""
    assumptions = {
        "birthdate": date(1950, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": True,
        "retirement_extra_expenses": 0.0,
        "base_savings": 50000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 3.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }

    call_count = {"value": 0}

    def fake_normal(mean, std_dev):
        call_count["value"] += 1
        return mean + call_count["value"]

    monkeypatch.setattr(np.random, "normal", fake_normal)

    base = BaseScenario(assumptions=assumptions)
    rand = RandomScenario(base_scenario=base)

    for premium_list in (
        rand.var_medicare_part_b_premium_costs_list,
        rand.var_medicare_part_d_premium_costs_list,
    ):
        for i in range(1, len(premium_list)):
            if (
                premium_list[i] > 0.0
                and premium_list[i - 1] > 0.0
                and base.month_list[i].month != 1
            ):
                assert premium_list[i] == premium_list[i - 1]

    def _count_expected_resamples(base_premium_list):
        expected = 0
        for i, (month, cost) in enumerate(zip(base.month_list, base_premium_list)):
            if cost <= 0.0:
                continue
            if i == 0 or month.month == 1 or base_premium_list[i - 1] <= 0.0:
                expected += 1
        return expected

    expected_call_count = _count_expected_resamples(
        base.medicare_part_b_premium_costs
    ) + _count_expected_resamples(base.medicare_part_d_premium_costs)
    assert call_count["value"] == expected_call_count
