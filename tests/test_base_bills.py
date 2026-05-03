"""Tests for base bills calculations."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
# Minimal assumptions dict for testing base bills
def base_assumptions():
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
        "base_monthly_bills": 2000.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 2.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 3.0,
    }


# The first month's base bills should equal the base_monthly_bills assumption
def test_base_bills_list_first_entry_equals_monthly_bills(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.base_bills_list[0] == base_assumptions["base_monthly_bills"]


# With zero inflation, every month's base bills should remain constant
def test_base_bills_list_constant_with_zero_inflation(base_assumptions):
    assumptions = {**base_assumptions, "base_inflation_per_yr": 0.0}
    scenario = BaseScenario(assumptions=assumptions)
    expected = base_assumptions["base_monthly_bills"]
    for bill in scenario.base_bills_list:
        assert bill == pytest.approx(expected, rel=1e-5)


# With positive inflation, base bills should grow by the monthly inflation factor each month
def test_base_bills_list_grows_with_inflation(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    monthly_inflation = round(
        ((1 + base_assumptions["base_inflation_per_yr"] / 100) ** (1 / 12)) - 1, 6
    )
    for i in range(1, 13):
        expected = round(
            base_assumptions["base_monthly_bills"] * (1 + monthly_inflation) ** i, 6
        )
        assert scenario.base_bills_list[i] == pytest.approx(expected, rel=1e-5)


# The length of base_bills_list should equal the scenario's total_months
def test_base_bills_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.base_bills_list) == scenario.total_months


# When base_monthly_bills is zero, all entries in base_bills_list should be zero
def test_base_bills_list_zero_when_no_bills(base_assumptions):
    assumptions = {**base_assumptions, "base_monthly_bills": 0.0}
    scenario = BaseScenario(assumptions=assumptions)
    assert all(bill == 0.0 for bill in scenario.base_bills_list)


# A higher inflation rate should produce larger base bills over time
def test_base_bills_list_higher_inflation_produces_larger_bills(base_assumptions):
    low_inflation = {**base_assumptions, "base_inflation_per_yr": 1.0}
    high_inflation = {**base_assumptions, "base_inflation_per_yr": 5.0}

    low_scenario = BaseScenario(assumptions=low_inflation)
    high_scenario = BaseScenario(assumptions=high_inflation)

    assert high_scenario.base_bills_list[12] > low_scenario.base_bills_list[12]
