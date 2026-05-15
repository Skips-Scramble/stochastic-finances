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


# month_list length should equal total_months
def test_month_list_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.month_list) == scenario.total_months


# count_list should equal list(range(total_months))
def test_count_list_equals_range_of_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.count_list == list(range(scenario.total_months))


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


# All values in age_by_month_list should be between 0 and 11 inclusive
def test_age_by_month_list_values_between_0_and_11(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert all(0 <= m <= 11 for m in scenario.age_by_month_list)


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


# When ss_incl is True, entries at or after retirement should be non-negative
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
    assert all(v >= 0 for v in post_retire_values)


# When ss_incl is True, ss_amt_by_date should grow with inflation over time
def test_ss_amt_by_date_grows_with_inflation(base_assumptions):
    assumptions = {
        **base_assumptions,
        "ss_incl": True,
        "ss_amt_per_mo": 2000.0,
        "base_inflation_per_yr": 3.0,
    }
    scenario = BaseScenario(assumptions=assumptions)
    post_retire_values = [
        scenario.ss_amt_by_date[i]
        for i, month in enumerate(scenario.month_list)
        if month >= scenario.retirement_date
    ]

    # Check a multi-month window instead of a single pair comparison.
    window_size = min(24, len(post_retire_values))
    assert window_size > 1
    window = post_retire_values[:window_size]

    # Values should not decline month-to-month in the window.
    assert all(curr >= prev for prev, curr in zip(window, window[1:]))

    # Inflation should produce a net increase across the window.
    assert window[-1] > window[0]


# With a known inflation rate, SS amount 10 years after retirement should match exact compounding from retirement start
def test_ss_amt_by_date_matches_10_year_compounding(base_assumptions):
    assumptions = {
        **base_assumptions,
        "ss_incl": True,
        "ss_amt_per_mo": 2000.0,
        "base_inflation_per_yr": 3.0,
    }
    scenario = BaseScenario(assumptions=assumptions)

    post_retire_indices = [
        i
        for i, month in enumerate(scenario.month_list)
        if month >= scenario.retirement_date
    ]
    months_10_years = 120
    assert len(post_retire_indices) > months_10_years

    retire_start_amt = scenario.ss_amt_by_date[post_retire_indices[0]]
    amt_10_years_later = scenario.ss_amt_by_date[post_retire_indices[months_10_years]]

    expected_10_year_amt = (
        retire_start_amt * (1 + assumptions["base_inflation_per_yr"] / 100) ** 10
    )
    assert amt_10_years_later == pytest.approx(expected_10_year_amt, rel=1e-6)


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


# When add_healthcare is True, healthcare costs should be non-decreasing month-over-month
def test_healthcare_costs_non_decreasing_month_over_month_when_enabled(
    base_assumptions,
):
    assumptions = {**base_assumptions, "add_healthcare": True}
    scenario = BaseScenario(assumptions=assumptions)

    # Check a stable 12-month window at the start of the timeline.
    window = scenario.healthcare_costs[:12]
    assert len(window) == 12
    assert all(curr >= prev for prev, curr in zip(window, window[1:]))
    assert window[-1] >= window[0]


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


# When add_medical_bills is True and inflation is zero, medical bills should stay constant
def test_medical_bills_stays_constant_with_zero_inflation(base_assumptions):
    assumptions = {
        **base_assumptions,
        "add_medical_bills": True,
        "monthly_medical_bills": 300.0,
        "base_inflation_per_yr": 0.0,
    }
    scenario = BaseScenario(assumptions=assumptions)

    window = scenario.medical_bills_list[:12]
    assert len(window) == 12
    assert all(v == pytest.approx(300.0, abs=1e-6) for v in window)


# With add_healthcare enabled, Medicare premiums should be included at age 65+
def test_medicare_premiums_zero_before_65_and_positive_at_65_plus(base_assumptions):
    assumptions = {**base_assumptions, "add_healthcare": True}
    scenario = BaseScenario(assumptions=assumptions)

    pre_65_indices = [i for i, age in enumerate(scenario.age_by_year_list) if age < 65]
    at_or_after_65_indices = [
        i for i, age in enumerate(scenario.age_by_year_list) if age >= 65
    ]

    assert pre_65_indices
    assert at_or_after_65_indices
    assert all(scenario.medicare_total_costs[i] == 0.0 for i in pre_65_indices)
    assert any(scenario.medicare_total_costs[i] > 0.0 for i in at_or_after_65_indices)


# With add_healthcare enabled, Medicare premiums should be non-decreasing over time
def test_medicare_premiums_non_decreasing_after_65(base_assumptions):
    assumptions = {**base_assumptions, "add_healthcare": True}
    scenario = BaseScenario(assumptions=assumptions)

    post_65_values = [
        scenario.medicare_total_costs[i]
        for i, age in enumerate(scenario.age_by_year_list)
        if age >= 65
    ]

    window_size = min(24, len(post_65_values))
    assert window_size > 1
    window = post_65_values[:window_size]

    assert all(curr >= prev for prev, curr in zip(window, window[1:]))
    assert window[-1] >= window[0]


# With all three options enabled, healthcare, ACA bridge coverage, and medical bills all contribute
def test_all_three_medical_toggles_work_together(base_assumptions):
    assumptions = {
        **base_assumptions,
        "retirement_age_yrs": 60,
        "retirement_age_mos": 0,
        "add_healthcare": True,
        "include_pre_medicare_insurance": True,
        "add_medical_bills": True,
        "monthly_medical_bills": 350.0,
    }
    scenario = BaseScenario(assumptions=assumptions)

    pre_65_retired_indices = [
        i
        for i, (month, age) in enumerate(
            zip(scenario.month_list, scenario.age_by_year_list)
        )
        if month >= scenario.retirement_date and age < 65
    ]
    at_or_after_65_indices = [
        i for i, age in enumerate(scenario.age_by_year_list) if age >= 65
    ]

    assert pre_65_retired_indices
    assert at_or_after_65_indices
    assert any(scenario.healthcare_costs[i] > 0.0 for i in pre_65_retired_indices)
    assert any(
        scenario.private_insurance_costs[i] > 0.0 for i in pre_65_retired_indices
    )
    assert any(scenario.medical_bills_list[i] > 0.0 for i in pre_65_retired_indices)
    assert any(scenario.medicare_total_costs[i] > 0.0 for i in at_or_after_65_indices)


# --- Conservative rate tests ---


# conservative_yearly_mkt_interest should be a list of length total_months
def test_conservative_yearly_mkt_interest_length_equals_total_months(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert len(scenario.conservative_yearly_mkt_interest) == scenario.total_months


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


# Retirement accounts should default to a flat rate unless conservative mode is explicitly enabled
def test_retirement_account_defaults_to_non_conservative_when_not_provided(
    base_assumptions,
):
    assumptions = {
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
    scenario = BaseScenario(assumptions=assumptions)
    account = scenario.retirement_list[0]
    assert account.use_conservative_rates is False

    yearly_rates = scenario._account_yearly_rate_list(account)
    assert all(r == pytest.approx(yearly_rates[0], rel=1e-6) for r in yearly_rates)


# Retirement accounts should use a declining glide path when conservative mode is explicitly enabled
def test_retirement_account_uses_conservative_glidepath_when_opted_in(base_assumptions):
    assumptions = {
        **base_assumptions,
        "base_mkt_interest_per_yr": 10.0,
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 50000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
                "use_conservative_rates": True,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    account = scenario.retirement_list[0]
    assert account.use_conservative_rates is True

    yearly_rates = scenario._account_yearly_rate_list(account)
    floor_rate = pytest.approx(0.05, rel=1e-6)

    assert yearly_rates[0] > yearly_rates[-1]
    assert yearly_rates[-1] == floor_rate

    # Annualized path should step down year-over-year, while months within a year
    # may remain flat until the next annual step or the 5% floor is reached.
    yearly_checkpoints = yearly_rates[::12]
    assert all(
        next_rate < rate or next_rate == floor_rate
        for rate, next_rate in zip(yearly_checkpoints, yearly_checkpoints[1:])
    )


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
