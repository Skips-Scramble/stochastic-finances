"""Tests for payment item behavior within BaseScenario."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario


@pytest.fixture
# Full base assumptions for testing payment item behavior in isolation

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


# With no payment_items, non_base_bills_lists should be empty.
def test_non_base_bills_lists_empty_with_no_payment_items(base_assumptions):
    scenario = BaseScenario(assumptions=base_assumptions)
    assert scenario.non_base_bills_lists == []


# With one payment item, non_base_bills_lists should contain one sublist.
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


# A payment item's calc_pmt_list should be all zeros outside its active window.
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
    pre_payment_values = [
        pmt_list[i] for i, age in enumerate(scenario.age_by_year_list) if age < 40
    ]
    assert all(v == 0.0 for v in pre_payment_values)


# A payment item should produce non-zero values during its active window.
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
    active_values = [
        pmt_list[i] for i, age in enumerate(scenario.age_by_year_list) if 40 <= age < 45
    ]
    assert any(v > 0 for v in active_values)


# The payments_list should have one Payment object per payment_items entry.
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
