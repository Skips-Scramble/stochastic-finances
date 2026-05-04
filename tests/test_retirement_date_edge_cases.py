from datetime import date, timedelta

import pytest

from pages.base_scenario import BaseScenario, calc_date_on_age


def _assumptions_template():
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


@pytest.mark.parametrize(
    "birthdate, age_yrs, age_mos, expected_retirement_date",
    [
        (date(1988, 2, 29), 65, 0, date(2053, 2, 1)),
        (date(1990, 1, 1), 65, 0, date(2055, 1, 1)),
        (date(1990, 12, 31), 65, 0, date(2055, 12, 1)),
        (date(1990, 12, 31), 65, 1, date(2056, 1, 1)),
    ],
)
# calc_date_on_age should handle leap-day birthdays and start/end-of-year rollover dates.
def test_calc_date_on_age_handles_leap_and_year_boundaries(
    birthdate, age_yrs, age_mos, expected_retirement_date
):
    assert calc_date_on_age(birthdate, age_yrs, age_mos) == expected_retirement_date


@pytest.mark.parametrize(
    "birthdate, retirement_age_yrs, retirement_age_mos",
    [
        (date(1988, 2, 29), 65, 0),
        (date(1990, 1, 1), 65, 0),
        (date(1990, 12, 31), 65, 0),
        (date(1990, 12, 31), 65, 1),
    ],
)
# BaseScenario retirement_date should exactly match calc_date_on_age for edge-case birthdays.
def test_base_scenario_retirement_date_matches_calc_date_on_age(
    birthdate, retirement_age_yrs, retirement_age_mos
):
    assumptions = {
        **_assumptions_template(),
        "birthdate": birthdate,
        "retirement_age_yrs": retirement_age_yrs,
        "retirement_age_mos": retirement_age_mos,
    }
    scenario = BaseScenario(assumptions=assumptions)

    expected_retirement_date = calc_date_on_age(
        birthdate, retirement_age_yrs, retirement_age_mos
    )
    assert scenario.retirement_date == expected_retirement_date


# Retirement transition lists should flip exactly at the retirement month boundary.
def test_pre_and_post_retire_lists_switch_at_retirement_month():
    assumptions = {
        **_assumptions_template(),
        "birthdate": date(2000, 2, 29),
        "retirement_age_yrs": 30,
        "retirement_age_mos": 0,
    }
    scenario = BaseScenario(assumptions=assumptions)

    retirement_index = scenario.months_until_retirement

    assert scenario.month_list[retirement_index] == scenario.retirement_date
    assert scenario.pre_retire_month_count_list[retirement_index] == 0
    assert scenario.post_retire_month_count_list[retirement_index] == 1

    if retirement_index > 0:
        assert scenario.month_list[retirement_index - 1] < scenario.retirement_date
        assert (
            scenario.pre_retire_month_count_list[retirement_index - 1]
            == retirement_index - 1
        )
        assert scenario.post_retire_month_count_list[retirement_index - 1] == 0


# JSON assumptions with a pre-1900 birthdate should fail when scenario calculations parse birthdate.
def test_json_assumptions_pre_1900_birthdate_raises_value_error():
    assumptions = {
        **_assumptions_template(),
        "birthdate": "12/31/1899",
    }

    with pytest.raises(ValueError, match="1900"):
        BaseScenario(assumptions=assumptions).retirement_date


# JSON assumptions with a future birthdate should fail when scenario calculations parse birthdate.
def test_json_assumptions_future_birthdate_raises_value_error():
    future_birthdate = (date.today() + timedelta(days=1)).strftime("%m/%d/%Y")
    assumptions = {
        **_assumptions_template(),
        "birthdate": future_birthdate,
    }

    with pytest.raises(ValueError, match="future"):
        BaseScenario(assumptions=assumptions).retirement_date