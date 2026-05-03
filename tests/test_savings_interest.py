"""Tests for savings account interest rate calculation."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
def minimal_savings_assumptions():
    """Minimal assumptions dict for a savings-only scenario with no retirement accounts."""
    return {
        "birthdate": date(1990, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0,
        "base_savings": 10000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 2.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }

# Todo: Delete this as it's not helpful
def test_yearly_rf_interest_computed_from_assumption(minimal_savings_assumptions):
    """yearly_rf_interest is base_rf_interest_per_yr converted to a decimal."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    rate_pct = minimal_savings_assumptions["base_rf_interest_per_yr"]
    expected = round(rate_pct / 100, 6)
    assert scenario.yearly_rf_interest == expected


def test_monthly_rf_interest_derived_from_yearly(minimal_savings_assumptions):
    """monthly_rf_interest is the monthly equivalent of yearly_rf_interest."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    expected = round((1 + scenario.yearly_rf_interest) ** (1 / 12) - 1, 6)
    assert scenario.monthly_rf_interest == expected


def test_savings_initial_balance(minimal_savings_assumptions):
    """The first entry in the savings list equals the initial base_savings."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    assert savings_list[0] == minimal_savings_assumptions["base_savings"]


def test_savings_grows_with_interest(minimal_savings_assumptions):
    """With no contributions and no bills, savings grows by monthly_rf_interest each month."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    base_savings = minimal_savings_assumptions["base_savings"]
    monthly_rate = scenario.monthly_rf_interest

    expected_month_1 = round(base_savings * (1 + monthly_rate), 6)
    assert savings_list[1] == pytest.approx(expected_month_1, rel=1e-4)


def test_savings_compounds_over_multiple_months(minimal_savings_assumptions):
    """Savings compounds correctly over several months."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    base_savings = minimal_savings_assumptions["base_savings"]
    monthly_rate = scenario.monthly_rf_interest

    for month in range(1, 13):
        expected = round(base_savings * (1 + monthly_rate) ** month, 6)
        assert savings_list[month] == pytest.approx(expected, rel=1e-4)


def test_savings_compounds_correctly_at_age_ninety_zero_months(
    minimal_savings_assumptions,
):
    """Savings at age 90y 0m matches pure compounding from the start month."""
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    base_savings = minimal_savings_assumptions["base_savings"]
    monthly_rate = scenario.monthly_rf_interest

    target_month_index = next(
        i
        for i, (age_yrs, age_mos) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if age_yrs == 90 and age_mos == 0
    )

    expected = round(base_savings * (1 + monthly_rate) ** target_month_index, 6)
    assert savings_list[target_month_index] == pytest.approx(expected, rel=1e-6)


def test_higher_interest_rate_produces_more_savings(minimal_savings_assumptions):
    """A higher base_rf_interest_per_yr results in a larger savings balance."""
    low_rate_assumptions = {**minimal_savings_assumptions, "base_rf_interest_per_yr": 1.0}
    high_rate_assumptions = {**minimal_savings_assumptions, "base_rf_interest_per_yr": 5.0}

    low_scenario = BaseScenario(assumptions=low_rate_assumptions)
    high_scenario = BaseScenario(assumptions=high_rate_assumptions)

    low_savings = low_scenario.savings_retirement_account_list[0]
    high_savings = high_scenario.savings_retirement_account_list[0]

    assert high_savings[12] > low_savings[12]
