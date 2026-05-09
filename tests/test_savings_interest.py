"""Tests for savings account interest rate calculation."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
# Minimal assumptions dict for a savings-only scenario with no retirement accounts
def minimal_savings_assumptions():
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
# yearly_rf_interest should be base_rf_interest_per_yr converted to a decimal
def test_yearly_rf_interest_computed_from_assumption(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    rate_pct = minimal_savings_assumptions["base_rf_interest_per_yr"]
    expected = round(rate_pct / 100, 6)
    assert scenario.yearly_rf_interest == expected


# monthly_rf_interest should be the monthly compounding equivalent of yearly_rf_interest
def test_monthly_rf_interest_derived_from_yearly(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    expected = round((1 + scenario.yearly_rf_interest) ** (1 / 12) - 1, 6)
    assert scenario.monthly_rf_interest == expected


# The first entry in the savings list should equal the initial base_savings amount
def test_savings_initial_balance(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    assert savings_list[0] == minimal_savings_assumptions["base_savings"]


# With no contributions and no bills, savings should grow by monthly_rf_interest each month
def test_savings_grows_with_interest(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    base_savings = minimal_savings_assumptions["base_savings"]
    monthly_rate = scenario.monthly_rf_interest

    expected_month_1 = round(base_savings * (1 + monthly_rate), 6)
    assert savings_list[1] == pytest.approx(expected_month_1, rel=1e-4)


# Savings should compound correctly over the first year of months
def test_savings_compounds_over_multiple_months(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    base_savings = minimal_savings_assumptions["base_savings"]
    monthly_rate = scenario.monthly_rf_interest

    for month in range(1, 13):
        expected = round(base_savings * (1 + monthly_rate) ** month, 6)
        assert savings_list[month] == pytest.approx(expected, rel=1e-4)


# Savings at age 90y 0m should match pure compounding from the start month
def test_savings_compounds_correctly_at_age_ninety_zero_months(
    minimal_savings_assumptions,
):
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


# A higher base_rf_interest_per_yr should produce a larger savings balance
def test_higher_interest_rate_produces_more_savings(minimal_savings_assumptions):
    low_rate_assumptions = {
        **minimal_savings_assumptions,
        "base_rf_interest_per_yr": 1.0,
    }
    high_rate_assumptions = {
        **minimal_savings_assumptions,
        "base_rf_interest_per_yr": 5.0,
    }

    low_scenario = BaseScenario(assumptions=low_rate_assumptions)
    high_scenario = BaseScenario(assumptions=high_rate_assumptions)

    low_savings = low_scenario.savings_retirement_account_list[0]
    high_savings = high_scenario.savings_retirement_account_list[0]

    assert high_savings[12] > low_savings[12]


# savings_retirement_account_list should return a tuple of 17 elements
def test_savings_retirement_account_list_has_17_elements(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    result = scenario.savings_retirement_account_list
    assert len(result) == 17


# Each element of savings_retirement_account_list should be a list of length total_months
def test_savings_retirement_account_list_all_sublists_have_total_months_length(
    minimal_savings_assumptions,
):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    result = scenario.savings_retirement_account_list
    for sublist in result:
        assert len(sublist) == scenario.total_months


# With no retirement accounts, all retirement balance lists should be all zeros
def test_savings_retirement_account_list_retirement_balances_all_zero_with_no_accounts(
    minimal_savings_assumptions,
):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    result = scenario.savings_retirement_account_list
    # Indices 1-3, 8-12 are retirement account balances
    for idx in [1, 2, 3, 8, 9, 11]:
        assert all(v == 0.0 for v in result[idx])


# With no retirement accounts, all transfer lists should be all zeros
def test_savings_retirement_account_list_transfer_lists_all_zero_with_no_accounts(
    minimal_savings_assumptions,
):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    result = scenario.savings_retirement_account_list
    # Indices 5, 6, 7, 10, 12 are transfer lists
    for idx in [5, 6, 7, 10, 12]:
        assert all(v == 0.0 for v in result[idx])


# With no retirement accounts, the RMD list should be all zeros
def test_savings_retirement_account_list_rmd_list_all_zero_with_no_accounts(
    minimal_savings_assumptions,
):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    rmd_list = scenario.savings_retirement_account_list[4]
    assert all(v == 0.0 for v in rmd_list)


# Adding a monthly savings contribution should increase the savings balance relative to no contribution
def test_savings_with_monthly_contribution_grows_faster(minimal_savings_assumptions):
    no_contrib = minimal_savings_assumptions
    with_contrib = {**minimal_savings_assumptions, "base_saved_per_mo": 500.0}

    no_scenario = BaseScenario(assumptions=no_contrib)
    with_scenario = BaseScenario(assumptions=with_contrib)

    no_savings = no_scenario.savings_retirement_account_list[0]
    with_savings = with_scenario.savings_retirement_account_list[0]

    assert with_savings[12] > no_savings[12]


# Adding base_monthly_bills should produce a lower savings balance than no bills
def test_savings_decreases_with_bills(minimal_savings_assumptions):
    no_bills = minimal_savings_assumptions
    with_bills = {**minimal_savings_assumptions, "base_monthly_bills": 500.0}

    no_bills_scenario = BaseScenario(assumptions=no_bills)
    with_bills_scenario = BaseScenario(assumptions=with_bills)

    no_savings = no_bills_scenario.savings_retirement_account_list[0]
    with_savings = with_bills_scenario.savings_retirement_account_list[0]

    # Savings with bills should be lower than savings without bills (pre-retirement bills are not subtracted)
    # Actually looking at the code, pre-retirement savings only subtract non-base bills. Let's test post-retirement.
    # Post-retirement savings subtract base_bills_list.
    # Find a post-retirement month index
    retirement_idx = no_bills_scenario.months_until_retirement + 1
    assert with_savings[retirement_idx] < no_savings[retirement_idx]


# yearly_rf_interest should be base_rf_interest_per_yr as a decimal fraction
def test_yearly_rf_interest_is_fraction_of_assumption(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    assert scenario.yearly_rf_interest == pytest.approx(
        minimal_savings_assumptions["base_rf_interest_per_yr"] / 100, rel=1e-6
    )


# monthly_rf_interest should always be less than yearly_rf_interest
def test_monthly_rf_interest_less_than_yearly(minimal_savings_assumptions):
    scenario = BaseScenario(assumptions=minimal_savings_assumptions)
    assert scenario.monthly_rf_interest < scenario.yearly_rf_interest


# With zero interest rate, savings should only decrease by bills (compounding factor = 1)
def test_savings_zero_interest_rate_stays_flat_with_no_bills(
    minimal_savings_assumptions,
):
    assumptions = {**minimal_savings_assumptions, "base_rf_interest_per_yr": 0.0}
    scenario = BaseScenario(assumptions=assumptions)
    savings = scenario.savings_retirement_account_list[0]
    # With no bills and zero interest, savings should stay constant (pre-retirement)
    assert savings[0] == pytest.approx(savings[1], rel=1e-5)


# A Roth IRA initial balance should appear in the roth_ira_balance_list (index 1)
def test_roth_ira_balance_initialized_in_savings_account_list(
    minimal_savings_assumptions,
):
    assumptions = {
        **minimal_savings_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "roth_ira",
                "base_retirement": 20000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    roth_ira_list = scenario.savings_retirement_account_list[1]
    assert roth_ira_list[0] == pytest.approx(20000.0, rel=1e-4)


# A Traditional 401k initial balance should appear in the trad_401k_balance_list (index 3)
def test_trad_401k_balance_initialized_in_savings_account_list(
    minimal_savings_assumptions,
):
    assumptions = {
        **minimal_savings_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 60000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    trad_401k_list = scenario.savings_retirement_account_list[3]
    assert trad_401k_list[0] == pytest.approx(60000.0, rel=1e-4)


# A higher starting savings balance should produce a higher savings balance at every month
def test_higher_base_savings_produces_higher_balance_throughout(
    minimal_savings_assumptions,
):
    low_savings = {**minimal_savings_assumptions, "base_savings": 5000.0}
    high_savings = {**minimal_savings_assumptions, "base_savings": 50000.0}

    low_scenario = BaseScenario(assumptions=low_savings)
    high_scenario = BaseScenario(assumptions=high_savings)

    low_list = low_scenario.savings_retirement_account_list[0]
    high_list = high_scenario.savings_retirement_account_list[0]

    assert high_list[0] > low_list[0]
    assert high_list[12] > low_list[12]
