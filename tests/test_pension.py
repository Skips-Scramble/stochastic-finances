"""Tests for pension retirement account implementation."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario, RetirementPension


@pytest.fixture
def base_assumptions():
    """Base assumptions dict for pension tests."""
    return {
        "birthdate": date(1980, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0,
        "base_savings": 50000.0,
        "base_saved_per_mo": 500.0,
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


@pytest.fixture
def pension_assumptions(base_assumptions):
    """Assumptions with a pension account starting at age 65."""
    return {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "pension",
                "base_retirement": 0.0,
                "base_retirement_per_mo": 2000.0,
                "base_retirement_per_yr_increase": 0.0,
                "pension_start_age_yrs": 65,
                "pension_start_age_mos": 0,
                "use_conservative_rates": True,
            }
        ],
    }


def test_retirement_list_contains_pension(pension_assumptions):
    """retirement_list should include a RetirementPension when pension type is given."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    assert len(scenario.retirement_list) == 1
    assert isinstance(scenario.retirement_list[0], RetirementPension)


def test_pension_payment_zero_before_start_age(pension_assumptions):
    """Pension payments should be zero before the pension start age."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    pension = scenario.retirement_list[0]

    # Find the index of the month just before age 65
    pre_retire_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 64 and mo == 11
    )
    assert pension.pension_payment_list[pre_retire_idx] == 0.0


def test_pension_payment_nonzero_at_start_age(pension_assumptions):
    """Pension payments should be nonzero at the pension start age."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    pension = scenario.retirement_list[0]

    start_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 65 and mo == 0
    )
    assert pension.pension_payment_list[start_idx] > 0.0


def test_pension_payment_inflation_adjusted(pension_assumptions):
    """Pension payment should grow with inflation over time."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    pension = scenario.retirement_list[0]

    start_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 65 and mo == 0
    )
    payment_at_start = pension.pension_payment_list[start_idx]
    payment_one_year_later = pension.pension_payment_list[start_idx + 12]

    # With 3% inflation the payment one year later should be ~3% higher
    assert payment_one_year_later > payment_at_start
    expected_growth = pytest.approx(payment_at_start * 1.03, rel=0.01)
    assert payment_one_year_later == expected_growth


def test_pension_base_amount_in_todays_dollars(pension_assumptions):
    """Pension base amount should be expressed in today's dollars and inflated at start."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    pension = scenario.retirement_list[0]

    start_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 65 and mo == 0
    )
    # Payment at start should equal base_retirement_per_mo * (1+monthly_inflation)^start_idx
    monthly_inflation = pension.monthly_inflation
    expected = round(2000.0 * (1 + monthly_inflation) ** start_idx, 6)
    assert pension.pension_payment_list[start_idx] == pytest.approx(expected, rel=1e-4)


def test_pension_no_pre_retirement_contributions(pension_assumptions):
    """A pension should have no pre-retirement contributions (retirement_increase_list is all zeros)."""
    scenario = BaseScenario(assumptions=pension_assumptions)
    pension = scenario.retirement_list[0]
    assert all(v == 0.0 for v in pension.retirement_increase_list)


def test_pension_start_at_custom_age(base_assumptions):
    """Pension starting at a non-default age should pay nothing before that age."""
    assumptions = {
        **base_assumptions,
        "retirement_accounts": [
            {
                "retirement_type": "pension",
                "base_retirement": 0.0,
                "base_retirement_per_mo": 1500.0,
                "base_retirement_per_yr_increase": 0.0,
                "pension_start_age_yrs": 62,
                "pension_start_age_mos": 0,
                "use_conservative_rates": True,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    pension = scenario.retirement_list[0]

    # Before age 62 should be zero
    pre_start_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 61 and mo == 11
    )
    assert pension.pension_payment_list[pre_start_idx] == 0.0

    # At age 62 should be nonzero
    start_idx = next(
        i
        for i, (yr, mo) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if yr == 62 and mo == 0
    )
    assert pension.pension_payment_list[start_idx] > 0.0
