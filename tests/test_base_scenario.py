"""Tests for BaseScenario core properties and combined scenario calculations."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario, ss_fra


@pytest.fixture
# Full base assumptions for testing miscellaneous BaseScenario properties
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


# --- ScenarioCoreInfo / BaseScenario date and list properties ---


# total_months should be a positive integer
def test_total_months_is_positive(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.total_months > 0


# month_list length should equal total_months
def test_month_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.month_list) == scenario.total_months


# count_list should equal list(range(total_months))
def test_count_list_equals_range_of_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.count_list == list(range(scenario.total_months))


# pre_retire_month_count_list length should equal total_months
def test_pre_retire_month_count_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.pre_retire_month_count_list) == scenario.total_months


# post_retire_month_count_list length should equal total_months
def test_post_retire_month_count_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.post_retire_month_count_list) == scenario.total_months


# pre_retire_month_count_list should be zero for all months >= retirement_date
def test_pre_retire_month_count_list_zero_after_retirement(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    for i, month in enumerate(scenario.month_list):
        if month >= scenario.retirement_date:
            assert scenario.pre_retire_month_count_list[i] == 0


# post_retire_month_count_list should be zero for all months < retirement_date
def test_post_retire_month_count_list_zero_before_retirement(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    for i, month in enumerate(scenario.month_list):
        if month < scenario.retirement_date:
            assert scenario.post_retire_month_count_list[i] == 0


# age_by_year_list length should equal total_months
def test_age_by_year_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.age_by_year_list) == scenario.total_months


# age_by_month_list length should equal total_months
def test_age_by_month_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.age_by_month_list) == scenario.total_months


# All values in age_by_month_list should be between 0 and 11 inclusive
def test_age_by_month_list_values_between_0_and_11(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(0 <= m <= 11 for m in scenario.age_by_month_list)


# monthly_inflation should be positive when inflation rate is positive
def test_monthly_inflation_positive_when_annual_inflation_positive(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.monthly_inflation > 0


# monthly_inflation should be zero when annual inflation rate is zero
def test_monthly_inflation_zero_when_annual_inflation_zero(base_assumptions):
    assumptions = {**base_assumptions, "base_inflation_per_yr": 0.0}
    scenario = BaseScenario(assumptions=assumptions)
    assert scenario.monthly_inflation == pytest.approx(0.0, abs=1e-6)


# yearly_mkt_interest should equal base_mkt_interest_per_yr / 100 (as a decimal)
def test_yearly_mkt_interest_derived_from_assumption(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    expected = round(base_assumptions["base_mkt_interest_per_yr"] / 100, 6)
    assert scenario.yearly_mkt_interest == pytest.approx(expected, rel=1e-6)


# monthly_mkt_interest should be less than yearly_mkt_interest (compounding effect)
def test_monthly_mkt_interest_less_than_yearly_mkt_interest(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.monthly_mkt_interest < scenario.yearly_mkt_interest


# months_until_retirement should be positive for a young person retiring at 65
def test_months_until_retirement_positive_for_young_person(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.months_until_retirement > 0


# --- Social Security tests ---


# When ss_incl is False, all entries in ss_amt_by_date should be zero
def test_ss_amt_by_date_all_zero_when_not_included(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.ss_amt_by_date)


# When ss_incl is True, entries before retirement should be zero
def test_ss_amt_by_date_zero_before_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "ss_incl": True,
        "ss_amt_per_mo": 2000.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    for i, month in enumerate(scenario.month_list):
        if month < scenario.retirement_date:
            assert scenario.ss_amt_by_date[i] == 0.0


# When ss_incl is True, entries at or after retirement should be positive
def test_ss_amt_by_date_positive_at_and_after_retirement(base_assumptions):
    assumptions = {
        **base_assumptions,
        "ss_incl": True,
        "ss_amt_per_mo": 2000.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    post_retire_values = [
        scenario.ss_amt_by_date[i]
        for i, month in enumerate(scenario.month_list)
        if month >= scenario.retirement_date
    ]
    assert all(v > 0 for v in post_retire_values)


# When ss_incl is True, ss_amt_by_date should grow with inflation over time
def test_ss_amt_by_date_grows_with_inflation(base_assumptions):
    assumptions = {
        **base_assumptions,
        "ss_incl": True,
        "ss_amt_per_mo": 2000.0,
        "base_inflation_per_yr": 3.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    ss_list = scenario.ss_amt_by_date
    # Find two post-retirement indices separated by one year
    post_retire_indices = [
        i
        for i, month in enumerate(scenario.month_list)
        if month >= scenario.retirement_date
    ]
    assert ss_list[post_retire_indices[12]] > ss_list[post_retire_indices[0]]


# The ss_amt_by_date list length should equal total_months
def test_ss_amt_by_date_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.ss_amt_by_date) == scenario.total_months


# ss_fra should return (67, 0) for someone born in 1990 or later
def test_ss_fra_returns_67_0_for_1990_birthdate():
    yrs, mos = ss_fra(date(1990, 1, 1))
    assert yrs == 67
    assert mos == 0


# ss_fra should return (65, 0) for someone born before 1938
def test_ss_fra_returns_65_0_for_pre_1938_birthdate():
    yrs, mos = ss_fra(date(1930, 6, 15))
    assert yrs == 65
    assert mos == 0


# ss_fra should return (66, 0) for someone born in 1943
def test_ss_fra_returns_66_0_for_1943_birthdate():
    yrs, mos = ss_fra(date(1943, 3, 1))
    assert yrs == 66
    assert mos == 0


# --- Healthcare cost tests ---


# When add_healthcare is False, healthcare_costs should be all zeros
def test_healthcare_costs_all_zero_when_not_added(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.healthcare_costs)


# healthcare_costs list length should equal total_months
def test_healthcare_costs_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.healthcare_costs) == scenario.total_months


# --- Medical bills tests ---


# When add_medical_bills is not set, medical_bills_list should be all zeros
def test_medical_bills_list_all_zero_when_not_enabled(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.medical_bills_list)


# When add_medical_bills is True and monthly_medical_bills > 0, some values should be non-zero
def test_medical_bills_list_non_zero_when_enabled(base_assumptions):
    assumptions = {
        **base_assumptions,
        "add_medical_bills": True,
        "monthly_medical_bills": 300.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert any(v > 0 for v in scenario.medical_bills_list)


# medical_bills_list length should equal total_months
def test_medical_bills_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.medical_bills_list) == scenario.total_months


# --- Conservative rate tests ---


# conservative_yearly_mkt_interest should be a list of length total_months
def test_conservative_yearly_mkt_interest_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.conservative_yearly_mkt_interest) == scenario.total_months


# conservative_monthly_mkt_interest should be a list of length total_months
def test_conservative_monthly_mkt_interest_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.conservative_monthly_mkt_interest) == scenario.total_months


# When the starting rate is at or below MIN_CONSERVATIVE_RETIREMENT_RATE_PCT (5%),
# the conservative rate should be flat throughout
def test_conservative_rate_flat_when_start_rate_at_floor(base_assumptions):
    assumptions = {**base_assumptions, "base_mkt_interest_per_yr": 5.0}
    scenario = BaseScenario(assumptions=assumptions)
    rates = scenario.conservative_yearly_mkt_interest
    # All rates should be the same since we start at the floor
    assert all(r == pytest.approx(rates[0], rel=1e-5) for r in rates)


# When the starting rate is above the floor, the conservative rate should decrease over time
def test_conservative_rate_decreases_for_high_starting_rate(base_assumptions):
    assumptions = {**base_assumptions, "base_mkt_interest_per_yr": 10.0}
    scenario = BaseScenario(assumptions=assumptions)
    rates = scenario.conservative_yearly_mkt_interest
    # The rate at start should be higher than the rate far in the future
    assert rates[0] > rates[-1]


# --- Payment items tests ---


# With no payment_items, non_base_bills_lists should be empty
def test_non_base_bills_lists_empty_with_no_payment_items(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.non_base_bills_lists == []


# With one payment item, non_base_bills_lists should contain one sublist
def test_non_base_bills_lists_has_one_sublist_with_one_payment_item(base_assumptions):
    assumptions = {
        **base_assumptions,
        "payment_items": [
            {
                "pmt_name": "car_loan",
                "pmt_start_age_yrs": 35,
                "pmt_start_age_mos": 0,
                "pmt_length_yrs": 5,
                "pmt_length_mos": 0,
                "down_pmt": 0.0,
                "reg_pmt_amt": 400.0,
                "pmt_freq_mos": 1,
                "recurring_purchase": False,
                "recurring_timeframe": 0,
                "recurring_length": 0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert len(scenario.non_base_bills_lists) == 1


# A payment item's calc_pmt_list should be all zeros outside its active window
def test_payment_item_zero_outside_active_window(base_assumptions):
    assumptions = {
        **base_assumptions,
        "payment_items": [
            {
                "pmt_name": "car_loan",
                "pmt_start_age_yrs": 40,
                "pmt_start_age_mos": 0,
                "pmt_length_yrs": 5,
                "pmt_length_mos": 0,
                "down_pmt": 0.0,
                "reg_pmt_amt": 400.0,
                "pmt_freq_mos": 1,
                "recurring_purchase": False,
                "recurring_timeframe": 0,
                "recurring_length": 0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    payment = scenario.payments_list[0]
    pmt_list = payment.calc_pmt_list
    # Before age 40 the payment should be zero
    pre_payment_values = [
        pmt_list[i] for i, age in enumerate(scenario.age_by_year_list) if age < 40
    ]
    assert all(v == 0.0 for v in pre_payment_values)


# A payment item should produce non-zero values during its active window
def test_payment_item_non_zero_during_active_window(base_assumptions):
    assumptions = {
        **base_assumptions,
        "payment_items": [
            {
                "pmt_name": "car_loan",
                "pmt_start_age_yrs": 40,
                "pmt_start_age_mos": 0,
                "pmt_length_yrs": 5,
                "pmt_length_mos": 0,
                "down_pmt": 0.0,
                "reg_pmt_amt": 400.0,
                "pmt_freq_mos": 1,
                "recurring_purchase": False,
                "recurring_timeframe": 0,
                "recurring_length": 0,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    payment = scenario.payments_list[0]
    pmt_list = payment.calc_pmt_list
    # During age 40-44 the payment should be non-zero
    active_values = [
        pmt_list[i] for i, age in enumerate(scenario.age_by_year_list) if 40 <= age < 45
    ]
    assert any(v > 0 for v in active_values)


# The payments_list should have one Payment object per payment_items entry
def test_payments_list_length_matches_payment_items(base_assumptions):
    assumptions = {
        **base_assumptions,
        "payment_items": [
            {
                "pmt_name": "car_loan",
                "pmt_start_age_yrs": 40,
                "pmt_start_age_mos": 0,
                "pmt_length_yrs": 5,
                "pmt_length_mos": 0,
                "down_pmt": 0.0,
                "reg_pmt_amt": 400.0,
                "pmt_freq_mos": 1,
                "recurring_purchase": False,
                "recurring_timeframe": 0,
                "recurring_length": 0,
            },
            {
                "pmt_name": "mortgage",
                "pmt_start_age_yrs": 35,
                "pmt_start_age_mos": 0,
                "pmt_length_yrs": 30,
                "pmt_length_mos": 0,
                "down_pmt": 0.0,
                "reg_pmt_amt": 1500.0,
                "pmt_freq_mos": 1,
                "recurring_purchase": False,
                "recurring_timeframe": 0,
                "recurring_length": 0,
            },
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    assert len(scenario.payments_list) == 2


# --- Combination and edge case tests ---


# With very high bills and low savings, savings should eventually go negative without threshold protection
def test_savings_goes_negative_with_high_bills_and_no_threshold(base_assumptions):
    assumptions = {
        **base_assumptions,
        "base_savings": 1000.0,
        "base_monthly_bills": 5000.0,
        "base_saved_per_mo": 0.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    # After retirement with high bills, savings should eventually be negative
    post_retire_idx = scenario.months_until_retirement + 12
    assert (
        savings_list[post_retire_idx] < savings_list[scenario.months_until_retirement]
    )


# With high enough savings and low bills, savings should remain positive throughout retirement
def test_savings_stays_positive_with_high_savings_and_low_bills(base_assumptions):
    assumptions = {
        **base_assumptions,
        "base_savings": 5000000.0,
        "base_monthly_bills": 500.0,
        "base_saved_per_mo": 0.0,
        "base_rf_interest_per_yr": 4.0,
        "base_inflation_per_yr": 0.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    savings_list = scenario.savings_retirement_account_list[0]
    # All savings values should remain positive
    assert all(v > 0 for v in savings_list)


# Retirement with later age should allow more time for retirement account to grow
def test_later_retirement_age_produces_larger_401k_balance_at_retirement(
    base_assumptions,
):
    early_retire = {
        **base_assumptions,
        "retirement_age_yrs": 55,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 500.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    late_retire = {
        **base_assumptions,
        "retirement_age_yrs": 65,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 500.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
    }
    early_scenario = BaseScenario(assumptions=early_retire)
    late_scenario = BaseScenario(assumptions=late_retire)

    early_balance_at_retire = early_scenario.retirement_list[0].retirement_account_list[
        early_scenario.months_until_retirement
    ]
    late_balance_at_retire = late_scenario.retirement_list[0].retirement_account_list[
        late_scenario.months_until_retirement
    ]

    assert late_balance_at_retire > early_balance_at_retire


# The birthdate property should return a date object
def test_birthdate_property_returns_date_object(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert isinstance(scenario.birthdate, date)


# Passing birthdate as a string in MM/DD/YYYY format should parse correctly
def test_birthdate_parsed_from_string(base_assumptions):
    assumptions = {**base_assumptions, "birthdate": "01/01/1990"}
    scenario = BaseScenario(assumptions=assumptions)
    assert scenario.birthdate == date(1990, 1, 1)


# The death_date should be birthdate + 115 years
def test_death_date_is_birthdate_plus_115_years(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    from dateutil.relativedelta import relativedelta

    expected_death = (date(1990, 1, 1) + relativedelta(years=115)).replace(day=1)
    assert scenario.death_date == expected_death


# The retirement_increase_list on BaseScenario should aggregate all retirement account contributions
def test_base_scenario_retirement_increase_list_aggregates_all_accounts(
    base_assumptions,
):
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 0.0,
                "base_retirement_per_mo": 300.0,
                "base_retirement_per_yr_increase": 0.0,
            },
            {
                "retirement_type": "roth_ira",
                "base_retirement": 0.0,
                "base_retirement_per_mo": 200.0,
                "base_retirement_per_yr_increase": 0.0,
            },
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    # The aggregate increase at month 0 should be 300 + 200 = 500
    assert scenario.retirement_increase_list[0] == pytest.approx(500.0, rel=1e-5)


# The BaseScenario retirement_increase_list should be all zeros when no accounts exist
def test_base_scenario_retirement_increase_list_all_zero_with_no_accounts(
    base_assumptions,
):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(v == 0.0 for v in scenario.retirement_increase_list)
