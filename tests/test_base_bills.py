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


# With positive inflation, base_bills_list should be strictly monotonically increasing
def test_base_bills_list_monotonically_increasing_with_positive_inflation(
    base_assumptions,
):
    scenario = BaseScenario(assumptions=base_assumptions)
    bills = scenario.base_bills_list
    assert all(bills[i] < bills[i + 1] for i in range(len(bills) - 1))


# The last entry in base_bills_list should be greater than the first when inflation > 0
def test_base_bills_list_last_entry_greater_than_first(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.base_bills_list[-1] > scenario.base_bills_list[0]


# All entries in base_bills_list should be positive when base_monthly_bills > 0
def test_base_bills_list_all_positive_when_bills_positive(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(bill > 0 for bill in scenario.base_bills_list)


# Doubling base_monthly_bills should double every entry in base_bills_list
def test_base_bills_list_scales_linearly_with_base_monthly_bills(base_assumptions):
    single = BaseScenario(assumptions=base_assumptions)
    double_assumptions = {**base_assumptions, "base_monthly_bills": 4000.0}
    double = BaseScenario(assumptions=double_assumptions)
    for a, b in zip(single.base_bills_list, double.base_bills_list):
        assert b == pytest.approx(2 * a, rel=1e-5)


# The 12th-month value should match the expected compounded amount with 3% inflation
def test_base_bills_list_month_12_matches_expected_compounded_value(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    monthly_inflation = round(
        ((1 + base_assumptions["base_inflation_per_yr"] / 100) ** (1 / 12)) - 1, 6
    )
    expected = round(
        base_assumptions["base_monthly_bills"] * (1 + monthly_inflation) ** 12, 6
    )
    assert scenario.base_bills_list[12] == pytest.approx(expected, rel=1e-5)


# --- post_retire_extra_bills_list tests ---


# With zero retirement_extra_expenses, every entry in post_retire_extra_bills_list should be zero
def test_post_retire_extra_bills_zero_when_no_extra_expenses(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.post_retire_extra_bills_list)


# The length of post_retire_extra_bills_list should equal the scenario's total_months
def test_post_retire_extra_bills_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.post_retire_extra_bills_list) == scenario.total_months


# With positive retirement_extra_expenses, at least some entries should be non-zero
def test_post_retire_extra_bills_non_zero_with_positive_extra_expenses(
    base_assumptions,
):
    assumptions = {**base_assumptions, "retirement_extra_expenses": 12000.0}
    scenario = BaseScenario(assumptions=assumptions)
    assert any(v > 0 for v in scenario.post_retire_extra_bills_list)


# The first entry of post_retire_extra_bills_list should equal retirement_extra_expenses / 12
# (no inflation applied at month 0 since count_list starts at 0)
def test_post_retire_extra_bills_first_entry_equals_annual_divided_by_twelve(
    base_assumptions,
):
    extra = 12000.0
    assumptions = {
        **base_assumptions,
        "retirement_extra_expenses": extra,
        "base_inflation_per_yr": 0.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert scenario.post_retire_extra_bills_list[0] == pytest.approx(
        extra / 12, rel=1e-5
    )


# With positive inflation and extra expenses, post_retire_extra_bills_list should grow over time
def test_post_retire_extra_bills_grows_with_inflation(base_assumptions):
    assumptions = {**base_assumptions, "retirement_extra_expenses": 12000.0}
    scenario = BaseScenario(assumptions=assumptions)
    bills = scenario.post_retire_extra_bills_list
    assert bills[12] > bills[0]


# --- savings_increase_list tests ---


# The first entry of savings_increase_list should equal base_saved_per_mo
def test_savings_increase_list_first_entry_equals_base_saved_per_mo(base_assumptions):
    assumptions = {**base_assumptions, "base_saved_per_mo": 500.0}
    scenario = BaseScenario(assumptions=assumptions)
    assert scenario.savings_increase_list[0] == pytest.approx(500.0, rel=1e-5)


# All post-retirement entries in savings_increase_list should be zero
def test_savings_increase_list_zero_post_retirement(base_assumptions):
    assumptions = {**base_assumptions, "base_saved_per_mo": 500.0}
    scenario = BaseScenario(assumptions=assumptions)
    increase_list = scenario.savings_increase_list
    post_retire = [
        increase_list[i]
        for i, v in enumerate(scenario.pre_retire_month_count_list)
        if v == 0 and i > 0
    ]
    assert all(v == 0.0 for v in post_retire)


# The length of savings_increase_list should equal total_months
def test_savings_increase_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.savings_increase_list) == scenario.total_months


# With zero base_saved_per_mo, all entries in savings_increase_list should be zero
def test_savings_increase_list_all_zero_when_no_savings_contribution(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.savings_increase_list)


# --- monthly_savings_threshold_list tests ---


# With zero savings_lower_limit, all entries in monthly_savings_threshold_list should be zero
def test_savings_threshold_all_zero_when_lower_limit_zero(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.monthly_savings_threshold_list)


# The first entry of monthly_savings_threshold_list should equal savings_lower_limit
# (no inflation at month 0)
def test_savings_threshold_first_entry_equals_lower_limit(base_assumptions):
    assumptions = {
        **base_assumptions,
        "savings_lower_limit": 5000.0,
        "base_inflation_per_yr": 0.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert scenario.monthly_savings_threshold_list[0] == pytest.approx(5000.0, rel=1e-5)


# With positive inflation, monthly_savings_threshold_list should increase over time
def test_savings_threshold_grows_with_inflation(base_assumptions):
    assumptions = {**base_assumptions, "savings_lower_limit": 5000.0}
    scenario = BaseScenario(assumptions=assumptions)
    threshold = scenario.monthly_savings_threshold_list
    assert threshold[12] > threshold[0]


# The length of monthly_savings_threshold_list should equal total_months
def test_savings_threshold_length_equals_total_months(base_assumptions):
    assumptions = {**base_assumptions, "savings_lower_limit": 5000.0}
    scenario = BaseScenario(assumptions=assumptions)
    assert len(scenario.monthly_savings_threshold_list) == scenario.total_months
