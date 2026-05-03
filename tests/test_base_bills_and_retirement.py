"""Tests for base bills and retirement account calculations."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
# Minimal assumptions dict for testing base bills and retirement accounts
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


# --- Base bills tests ---


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


# --- Retirement account tests ---


# The initial balance of a traditional 401k account should equal its base_retirement value
def test_trad_401k_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_401k = scenario.retirement_list[0]
    assert trad_401k.retirement_account_list[0] == pytest.approx(50000.0, rel=1e-4)


# Before retirement, a 401k balance with no contributions should grow with market interest
def test_trad_401k_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_401k = scenario.retirement_list[0]
    account_list = trad_401k.retirement_account_list
    assert account_list[1] > account_list[0]


# Monthly contributions should be added to the 401k balance each pre-retirement month
def test_trad_401k_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 500.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario_no = BaseScenario(assumptions=no_contrib)
    scenario_with = BaseScenario(assumptions=with_contrib)

    no_list = scenario_no.retirement_list[0].retirement_account_list
    with_list = scenario_with.retirement_list[0].retirement_account_list

    # After one year, the account with contributions should have a higher balance
    assert with_list[12] > no_list[12]


# A higher market interest rate should produce a larger 401k balance over time
def test_trad_401k_higher_interest_rate_produces_larger_balance(base_assumptions):
    low_rate = {
        **base_assumptions,
        "base_mkt_interest_per_yr": 3.0,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    high_rate = {
        **base_assumptions,
        "base_mkt_interest_per_yr": 10.0,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    low_scenario = BaseScenario(assumptions=low_rate)
    high_scenario = BaseScenario(assumptions=high_rate)

    low_list = low_scenario.retirement_list[0].retirement_account_list
    high_list = high_scenario.retirement_list[0].retirement_account_list

    assert high_list[12] > low_list[12]


# --- Birthday and retirement date combination tests ---


# An early retiree (age 50) should have fewer pre-retirement months than a standard retiree (age 65)
def test_early_retiree_has_fewer_pre_retirement_months(base_assumptions):
    early_retire = {**base_assumptions, "retirement_age_yrs": 50, "retirement_age_mos": 0}
    standard_retire = {**base_assumptions, "retirement_age_yrs": 65, "retirement_age_mos": 0}

    early_scenario = BaseScenario(assumptions=early_retire)
    standard_scenario = BaseScenario(assumptions=standard_retire)

    early_pre_retire = sum(1 for v in early_scenario.pre_retire_month_count_list if v != 0)
    standard_pre_retire = sum(1 for v in standard_scenario.pre_retire_month_count_list if v != 0)

    assert early_pre_retire < standard_pre_retire


# A late retiree (age 70) should have more pre-retirement months than a standard retiree (age 65)
def test_late_retiree_has_more_pre_retirement_months(base_assumptions):
    late_retire = {**base_assumptions, "retirement_age_yrs": 70, "retirement_age_mos": 0}
    standard_retire = {**base_assumptions, "retirement_age_yrs": 65, "retirement_age_mos": 0}

    late_scenario = BaseScenario(assumptions=late_retire)
    standard_scenario = BaseScenario(assumptions=standard_retire)

    late_pre_retire = sum(1 for v in late_scenario.pre_retire_month_count_list if v != 0)
    standard_pre_retire = sum(1 for v in standard_scenario.pre_retire_month_count_list if v != 0)

    assert late_pre_retire > standard_pre_retire


# Retirement age in months should shift the retirement date by the correct number of months
def test_retirement_age_months_shifts_retirement_date(base_assumptions):
    no_months = {**base_assumptions, "retirement_age_yrs": 65, "retirement_age_mos": 0}
    with_months = {**base_assumptions, "retirement_age_yrs": 65, "retirement_age_mos": 6}

    no_months_scenario = BaseScenario(assumptions=no_months)
    with_months_scenario = BaseScenario(assumptions=with_months)

    # The retirement date should be 6 months later
    diff_months = (
        (with_months_scenario.retirement_date.year - no_months_scenario.retirement_date.year)
        * 12
        + (with_months_scenario.retirement_date.month - no_months_scenario.retirement_date.month)
    )
    assert diff_months == 6


# A person born later (younger) who retires at the same age should retire at a later date
def test_younger_person_retires_later(base_assumptions):
    older_person = {**base_assumptions, "birthdate": date(1970, 1, 1)}
    younger_person = {**base_assumptions, "birthdate": date(1990, 1, 1)}

    older_scenario = BaseScenario(assumptions=older_person)
    younger_scenario = BaseScenario(assumptions=younger_person)

    assert younger_scenario.retirement_date > older_scenario.retirement_date
