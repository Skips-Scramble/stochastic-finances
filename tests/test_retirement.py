"""Tests for retirement account and birthday/retirement date calculations."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
# Minimal assumptions dict for testing retirement accounts and birthday combinations
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
    early_retire = {
        **base_assumptions,
        "retirement_age_yrs": 50,
        "retirement_age_mos": 0,
    }
    standard_retire = {
        **base_assumptions,
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
    }

    early_scenario = BaseScenario(assumptions=early_retire)
    standard_scenario = BaseScenario(assumptions=standard_retire)

    early_pre_retire = sum(
        1 for v in early_scenario.pre_retire_month_count_list if v != 0
    )
    standard_pre_retire = sum(
        1 for v in standard_scenario.pre_retire_month_count_list if v != 0
    )

    assert early_pre_retire < standard_pre_retire


# A late retiree (age 70) should have more pre-retirement months than a standard retiree (age 65)
def test_late_retiree_has_more_pre_retirement_months(base_assumptions):
    late_retire = {
        **base_assumptions,
        "retirement_age_yrs": 70,
        "retirement_age_mos": 0,
    }
    standard_retire = {
        **base_assumptions,
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
    }

    late_scenario = BaseScenario(assumptions=late_retire)
    standard_scenario = BaseScenario(assumptions=standard_retire)

    late_pre_retire = sum(
        1 for v in late_scenario.pre_retire_month_count_list if v != 0
    )
    standard_pre_retire = sum(
        1 for v in standard_scenario.pre_retire_month_count_list if v != 0
    )

    assert late_pre_retire > standard_pre_retire


# Retirement age in months should shift the retirement date by the correct number of months
def test_retirement_age_months_shifts_retirement_date(base_assumptions):
    no_months = {**base_assumptions, "retirement_age_yrs": 65, "retirement_age_mos": 0}
    with_months = {
        **base_assumptions,
        "retirement_age_yrs": 65,
        "retirement_age_mos": 6,
    }

    no_months_scenario = BaseScenario(assumptions=no_months)
    with_months_scenario = BaseScenario(assumptions=with_months)

    # The retirement date should be 6 months later
    diff_months = (
        with_months_scenario.retirement_date.year
        - no_months_scenario.retirement_date.year
    ) * 12 + (
        with_months_scenario.retirement_date.month
        - no_months_scenario.retirement_date.month
    )
    assert diff_months == 6


# A person born later (younger) who retires at the same age should retire at a later date
def test_younger_person_retires_later(base_assumptions):
    older_person = {**base_assumptions, "birthdate": date(1970, 1, 1)}
    younger_person = {**base_assumptions, "birthdate": date(1990, 1, 1)}

    older_scenario = BaseScenario(assumptions=older_person)
    younger_scenario = BaseScenario(assumptions=younger_person)

    assert younger_scenario.retirement_date > older_scenario.retirement_date


# --- Roth 401k account tests ---


# The initial balance of a Roth 401k should equal its base_retirement value
def test_roth_401k_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_401k",
                "base_retirement": 30000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    roth_401k = scenario.retirement_list[0]
    assert roth_401k.retirement_account_list[0] == pytest.approx(30000.0, rel=1e-4)


# A Roth 401k with no contributions should grow with market interest before retirement
def test_roth_401k_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_401k",
                "base_retirement": 30000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[1] > account_list[0]


# Roth 401k contributions should increase the balance relative to an account with no contributions
def test_roth_401k_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_401k",
                "base_retirement": 30000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_401k",
                "base_retirement": 30000.0,
                "base_retirement_per_mo": 400.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    no_list = (
        BaseScenario(assumptions=no_contrib).retirement_list[0].retirement_account_list
    )
    with_list = (
        BaseScenario(assumptions=with_contrib)
        .retirement_list[0]
        .retirement_account_list
    )
    assert with_list[12] > no_list[12]


# --- Traditional IRA account tests ---


# The initial balance of a Traditional IRA should equal its base_retirement value
def test_trad_ira_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_ira",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_ira = scenario.retirement_list[0]
    assert trad_ira.retirement_account_list[0] == pytest.approx(20000.0, rel=1e-4)


# A Traditional IRA with no contributions should grow with market interest before retirement
def test_trad_ira_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_ira",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[1] > account_list[0]


# Traditional IRA contributions should increase the balance relative to no contributions
def test_trad_ira_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_ira",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_ira",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 300.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    no_list = (
        BaseScenario(assumptions=no_contrib).retirement_list[0].retirement_account_list
    )
    with_list = (
        BaseScenario(assumptions=with_contrib)
        .retirement_list[0]
        .retirement_account_list
    )
    assert with_list[12] > no_list[12]


# --- Roth IRA account tests ---


# The initial balance of a Roth IRA should equal its base_retirement value
def test_roth_ira_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    roth_ira = scenario.retirement_list[0]
    assert roth_ira.retirement_account_list[0] == pytest.approx(15000.0, rel=1e-4)


# A Roth IRA with no contributions should grow with market interest before retirement
def test_roth_ira_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[1] > account_list[0]


# Roth IRA contributions should increase the balance relative to no contributions
def test_roth_ira_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 250.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    no_list = (
        BaseScenario(assumptions=no_contrib).retirement_list[0].retirement_account_list
    )
    with_list = (
        BaseScenario(assumptions=with_contrib)
        .retirement_list[0]
        .retirement_account_list
    )
    assert with_list[12] > no_list[12]


# --- HSA account tests ---


# The initial balance of an HSA should equal its base_retirement value
def test_hsa_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "hsa",
                "base_retirement": 8000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    hsa = scenario.retirement_list[0]
    assert hsa.retirement_account_list[0] == pytest.approx(8000.0, rel=1e-4)


# An HSA with no contributions should grow with market interest before retirement
def test_hsa_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "hsa",
                "base_retirement": 8000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[1] > account_list[0]


# HSA contributions should increase the balance relative to no contributions
def test_hsa_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "hsa",
                "base_retirement": 8000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "hsa",
                "base_retirement": 8000.0,
                "base_retirement_per_mo": 200.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    no_list = (
        BaseScenario(assumptions=no_contrib).retirement_list[0].retirement_account_list
    )
    with_list = (
        BaseScenario(assumptions=with_contrib)
        .retirement_list[0]
        .retirement_account_list
    )
    assert with_list[12] > no_list[12]


# --- Brokerage account tests ---


# The initial balance of a brokerage account should equal its base_retirement value
def test_brokerage_initial_balance_equals_base_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "brokerage",
                "base_retirement": 25000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    brokerage = scenario.retirement_list[0]
    assert brokerage.retirement_account_list[0] == pytest.approx(25000.0, rel=1e-4)


# A brokerage account with no contributions should grow with market interest before retirement
def test_brokerage_grows_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "brokerage",
                "base_retirement": 25000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[1] > account_list[0]


# Brokerage contributions should increase the balance relative to no contributions
def test_brokerage_contributions_increase_balance(base_assumptions):
    no_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "brokerage",
                "base_retirement": 25000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    with_contrib = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "brokerage",
                "base_retirement": 25000.0,
                "base_retirement_per_mo": 350.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    no_list = (
        BaseScenario(assumptions=no_contrib).retirement_list[0].retirement_account_list
    )
    with_list = (
        BaseScenario(assumptions=with_contrib)
        .retirement_list[0]
        .retirement_account_list
    )
    assert with_list[12] > no_list[12]


# --- Multiple accounts and list-level tests ---


# The retirement_list should contain one entry per account specified in assumptions
def test_retirement_list_length_matches_number_of_accounts(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert len(scenario.retirement_list) == 2


# Each retirement account should be tracked independently when multiple accounts exist
def test_multiple_retirement_accounts_each_tracked_independently(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
            {
                "retirement_type": "roth_ira",
                "base_retirement": 15000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_401k_list = scenario.retirement_list[0].retirement_account_list
    roth_ira_list = scenario.retirement_list[1].retirement_account_list
    # Initial balances should reflect each account's own base_retirement
    assert trad_401k_list[0] == pytest.approx(50000.0, rel=1e-4)
    assert roth_ira_list[0] == pytest.approx(15000.0, rel=1e-4)


# A retirement account starting with zero balance should remain near zero with no contributions
def test_zero_balance_retirement_account_grows_to_zero_with_no_contributions(
    base_assumptions,
):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 0.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account_list = scenario.retirement_list[0].retirement_account_list
    assert account_list[0] == pytest.approx(0.0, abs=1e-6)
    assert account_list[12] == pytest.approx(0.0, abs=1e-6)


# The retirement_account_list length should equal the scenario's total_months
def test_retirement_account_list_length_equals_total_months(base_assumptions):
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
    assert len(trad_401k.retirement_account_list) == scenario.total_months


# An account with an annual increase should have higher contributions in year 2 than year 1
def test_trad_401k_annual_increase_raises_contributions_each_year(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 500.0,
                "base_retirement_per_yr_increase": 100.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_401k = scenario.retirement_list[0]
    # Year 1 contributions should be lower than year 2
    year_1_avg = sum(trad_401k.retirement_increase_list[0:12]) / 12
    year_2_avg = sum(trad_401k.retirement_increase_list[12:24]) / 12
    assert year_2_avg > year_1_avg


# The retirement_date should exactly match the expected date based on birthdate and retirement age
def test_retirement_date_matches_expected_from_birthdate_and_age(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    # birthdate = 1990-01-01, retirement_age_yrs = 65 → retirement_date = 2055-01-01
    from dateutil.relativedelta import relativedelta

    expected_date = (date(1990, 1, 1) + relativedelta(years=65)).replace(day=1)
    assert scenario.retirement_date == expected_date


# With no retirement accounts, the retirement_list should be empty
def test_empty_retirement_accounts_produces_empty_retirement_list(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.retirement_list == []
