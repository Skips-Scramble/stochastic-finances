"""Tests for healthcare costs and extra retirement expenses in BaseScenario."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
def retired_assumptions():
    # Minimal assumptions for a person already retired (born 1950, retired at 65 in Jan 2015).
    # Uses zero interest and zero inflation so savings changes are exact and easy to verify.
    return {
        "birthdate": date(1950, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0,
        "base_savings": 10_000_000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 0.0,
        "base_mkt_interest_per_yr": 0.0,
        "base_inflation_per_yr": 0.0,
    }


# --- Healthcare costs tests ---


def test_healthcare_costs_are_all_zeros_when_disabled(retired_assumptions):
    # healthcare_costs should be all zeros when add_healthcare is False
    scenario = BaseScenario(assumptions=retired_assumptions)
    assert all(v == 0.0 for v in scenario.healthcare_costs)


def test_healthcare_costs_are_nonzero_when_enabled(retired_assumptions):
    # healthcare_costs should have non-zero values for a person in the 65-84 age band when enabled
    assumptions = {**retired_assumptions, "add_healthcare": True}
    scenario = BaseScenario(assumptions=assumptions)
    assert sum(scenario.healthcare_costs) > 0


def test_healthcare_costs_length_equals_total_months(retired_assumptions):
    # healthcare_costs list length should equal total_months whether enabled or disabled
    disabled = BaseScenario(assumptions=retired_assumptions)
    enabled = BaseScenario(assumptions={**retired_assumptions, "add_healthcare": True})
    assert len(disabled.healthcare_costs) == disabled.total_months
    assert len(enabled.healthcare_costs) == enabled.total_months


def test_enabling_healthcare_reduces_savings_balance(retired_assumptions):
    # Enabling healthcare should reduce the final savings balance compared to no healthcare
    no_hc = BaseScenario(assumptions=retired_assumptions)
    with_hc = BaseScenario(
        assumptions={**retired_assumptions, "add_healthcare": True}
    )
    savings_no_hc = no_hc.savings_retirement_account_list[0]
    savings_with_hc = with_hc.savings_retirement_account_list[0]
    assert savings_with_hc[-1] < savings_no_hc[-1]


def test_disabling_healthcare_leaves_savings_unchanged(retired_assumptions):
    # With zero bills, zero interest, and healthcare disabled, savings stay at base_savings
    scenario = BaseScenario(assumptions=retired_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    assert all(v == retired_assumptions["base_savings"] for v in savings_list)


# --- Extra retirement expenses tests ---


def test_post_retire_extra_bills_are_all_zeros_when_no_extra_expenses(
    retired_assumptions,
):
    # post_retire_extra_bills_list should be all zeros when retirement_extra_expenses is zero
    scenario = BaseScenario(assumptions=retired_assumptions)
    assert all(v == 0.0 for v in scenario.post_retire_extra_bills_list)


def test_post_retire_extra_bills_length_equals_total_months(retired_assumptions):
    # post_retire_extra_bills_list length should equal total_months
    assumptions = {**retired_assumptions, "retirement_extra_expenses": 1200}
    scenario = BaseScenario(assumptions=assumptions)
    assert len(scenario.post_retire_extra_bills_list) == scenario.total_months


def test_post_retire_extra_bills_equal_monthly_rate_at_zero_inflation(
    retired_assumptions,
):
    # At zero inflation each monthly extra bill should equal retirement_extra_expenses / 12
    annual_extra = 1200.0
    assumptions = {**retired_assumptions, "retirement_extra_expenses": annual_extra}
    scenario = BaseScenario(assumptions=assumptions)
    expected_monthly = annual_extra / 12
    for v in scenario.post_retire_extra_bills_list:
        assert v == pytest.approx(expected_monthly, rel=1e-5)


def test_adding_extra_retirement_expenses_reduces_savings_balance(retired_assumptions):
    # Adding extra retirement expenses should reduce the final savings balance
    no_extra = BaseScenario(assumptions=retired_assumptions)
    with_extra = BaseScenario(
        assumptions={**retired_assumptions, "retirement_extra_expenses": 1200}
    )
    savings_no_extra = no_extra.savings_retirement_account_list[0]
    savings_with_extra = with_extra.savings_retirement_account_list[0]
    assert savings_with_extra[-1] < savings_no_extra[-1]


def test_extra_retirement_expenses_savings_difference_is_exact_at_zero_rates(
    retired_assumptions,
):
    # At zero interest and zero inflation the savings difference equals (total_months - 1) * monthly_extra
    annual_extra = 1200.0
    monthly_extra = annual_extra / 12

    no_extra = BaseScenario(assumptions=retired_assumptions)
    with_extra = BaseScenario(
        assumptions={**retired_assumptions, "retirement_extra_expenses": annual_extra}
    )

    savings_no_extra = no_extra.savings_retirement_account_list[0]
    savings_with_extra = with_extra.savings_retirement_account_list[0]

    # Month 0 is initialisation (no deduction). Months 1..total_months-1 each deduct monthly_extra.
    expected_diff = (no_extra.total_months - 1) * monthly_extra
    actual_diff = savings_no_extra[-1] - savings_with_extra[-1]
    assert actual_diff == pytest.approx(expected_diff, rel=1e-5)
