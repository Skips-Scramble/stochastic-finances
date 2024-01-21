import json
from datetime import date, datetime

import numpy as np
import numpy_financial as npf
import pydantic
import pytest
from dateutil.relativedelta import relativedelta

from financial_situation.models import Inputs
from scenarios.base_scenario import BaseScenario
from stochastic_finances_func import main

with open("input_assumptions.json", encoding="utf-8") as json_data:
    base_assumptions = json.load(json_data)

base_assumptions["birthdate"] = datetime.strptime(
    base_assumptions["birthdate"], "%m/%d/%Y"
).date()


def convert_rate_monthly(rate: float) -> float:
    """Convert an annual interest rate to a monthly rate"""
    return round((1 + rate / 100) ** (1 / 12) - 1, 6)


# Testing if a person is too old. Really testing pydantic
def test_birthdates() -> None:
    """Make sure a person is not crazy old"""
    birthday_assumptions = base_assumptions.copy()
    birthday_assumptions["birthdate"] = date(1800, 1, 1)

    with pytest.raises(pydantic.ValidationError):
        Inputs(**birthday_assumptions)

    birthday_assumptions["birthdate"] = date.today() + relativedelta(months=100)
    with pytest.raises(pydantic.ValidationError):
        Inputs(**birthday_assumptions)


def test_retirement_age() -> None:
    """Make sure the retirement age isn't crazy"""
    retirement_age_assumptions = base_assumptions.copy()

    # Test base case
    Inputs(**retirement_age_assumptions)

    retirement_age_assumptions["retirement_age_yrs"] = 1_000

    with pytest.raises(pydantic.ValidationError):
        Inputs(**retirement_age_assumptions)

    retirement_age_assumptions["retirement_age_yrs"] = "too old"
    with pytest.raises(pydantic.ValidationError):
        Inputs(**retirement_age_assumptions)


def test_base_case_zero():
    """Test simple cases for base scenario"""
    zero_assumptions = base_assumptions.copy()
    zero_case = BaseScenario(zero_assumptions)

    assert zero_case.death_date == date(2110, 1, 1), "Incorrect death date"

    assert zero_case.retirement_date == date(2065, 1, 1), "Incorrect retirement date"

    assert zero_case.monthly_inflation == 0.0, "Incorrect monthly inflation"

    assert set(zero_case.monthly_savings_threshold_list) == {
        0
    }, "Incorred threshold list"

    assert set(zero_case.savings_increase_list) == {
        0
    }, "Incorrect savings increase list"

    assert len(zero_case.non_base_bills_lists) == 1, "Too many non-base bills lists"

    assert set(zero_case.non_base_bills_lists[0]) == {
        0
    }, "Incorrect non-base bills list"

    assert set(zero_case.retirement_increase_list) == {
        0
    }, "Incorrect retirement increase list"

    assert set(zero_case.savings_retirement_account_list[0]) == {
        0
    }, "Incorrect savings list"

    assert set(zero_case.savings_retirement_account_list[1]) == {
        0
    }, "Incorrect retirement list"


def correct_age_count() -> None:
    """Need to confirm that the age in years and months is correct"""
    age_calc_assumptions = base_assumptions.copy()
    age_calc_scen = BaseScenario(age_calc_assumptions)

    months = 49

    age_in_months = [
        relativedelta(
            date.today() + relativedelta(months=x), age_calc_scen.birthdate
        ).months
        for x in range(months)
    ]

    assert (
        age_in_months == age_calc_scen.age_by_month_list[:months]
    ), "Age in month is incorrect"

    age_in_years = [
        relativedelta(
            date.today() + relativedelta(months=x), age_calc_scen.birthdate
        ).years
        for x in range(months)
    ]

    assert (
        age_in_years == age_calc_scen.age_by_year_list[:months]
    ), "Age in years is incorrect"


def test_core_tvm() -> None:
    """Test some basic TVM calcs"""
    simple_interest_assumptions = base_assumptions.copy()

    # 1000 invested with simple interest
    simple_interest_assumptions["base_savings"] = 1000
    simple_interest_assumptions["base_rf_interest_per_yr"] = 5
    simple_interest_assumptions["base_retirement"] = 1000
    simple_interest_assumptions["base_mkt_interest_per_yr"] = 5
    simple_interest_scen = BaseScenario(simple_interest_assumptions)

    assert np.isclose(
        simple_interest_scen.create_base_df()
        .loc[lambda df: df["count"] == 100]["savings_account"]
        .iat[0],
        -1
        * npf.fv(
            rate=convert_rate_monthly(
                simple_interest_assumptions["base_rf_interest_per_yr"]
            ),
            nper=100,
            pmt=0,
            pv=simple_interest_assumptions["base_savings"],
            when="beginning",
        ),
    ), "Simple interest savings test failed"

    assert np.isclose(
        simple_interest_scen.create_base_df()
        .loc[lambda df: df["count"] == 100]["retirement_account"]
        .iat[0],
        -1
        * npf.fv(
            rate=convert_rate_monthly(
                simple_interest_assumptions["base_mkt_interest_per_yr"]
            ),
            nper=100,
            pmt=0,
            pv=simple_interest_assumptions["base_retirement"],
            when="beginning",
        ),
    ), "Simple interest retirement test failed"

    # Now with some base and some monthly contributions

    with_contrib_assumptions = simple_interest_assumptions.copy()
    with_contrib_assumptions["base_saved_per_mo"] = 555
    with_contrib_assumptions["base_retirement_per_mo"] = 666
    with_contrib_scen = BaseScenario(with_contrib_assumptions)

    months = 222

    assert np.isclose(
        with_contrib_scen.create_base_df()
        .loc[lambda df: df["count"] == months]["savings_account"]
        .iat[0],
        -1
        * npf.fv(
            rate=convert_rate_monthly(
                with_contrib_assumptions["base_rf_interest_per_yr"]
            ),
            nper=months,
            pmt=with_contrib_assumptions["base_saved_per_mo"],
            pv=simple_interest_assumptions["base_savings"],
            when="beginning",
        ),
    ), "With contributions savings failed"

    assert np.isclose(
        with_contrib_scen.create_base_df()
        .loc[lambda df: df["count"] == months]["retirement_account"]
        .iat[0],
        -1
        * npf.fv(
            rate=convert_rate_monthly(
                with_contrib_assumptions["base_mkt_interest_per_yr"]
            ),
            nper=months,
            pmt=with_contrib_assumptions["base_retirement_per_mo"],
            pv=simple_interest_assumptions["base_retirement"],
            when="beginning",
        ),
    ), "With contributions savings failed"

    # Test accounting for post-retirement

    months = 400

    retirement_date = with_contrib_assumptions["birthdate"] + relativedelta(
        months=with_contrib_assumptions["retirement_age_yrs"] * 12
        + with_contrib_assumptions["retirement_age_mos"]
    )

    time_until_retirement = relativedelta(retirement_date, date.today().replace(day=1))

    months_to_retirement = (
        time_until_retirement.years * 12 + time_until_retirement.months
    )

    retirement_account_upon_retirement = npf.fv(
        rate=convert_rate_monthly(with_contrib_assumptions["base_mkt_interest_per_yr"]),
        nper=months_to_retirement,
        pmt=-1 * with_contrib_assumptions["base_retirement_per_mo"],
        pv=-1 * simple_interest_assumptions["base_retirement"],
        when="beginning",
    )

    assert np.isclose(
        with_contrib_scen.create_base_df()
        .loc[lambda df: df["count"] == months_to_retirement]["retirement_account"]
        .iat[0],
        retirement_account_upon_retirement,
    ), "With contributions savings failed"

    months_post_retirement = 55

    assert np.isclose(
        with_contrib_scen.create_base_df()
        .loc[lambda df: df["count"] == months_to_retirement + months_post_retirement][
            "retirement_account"
        ]
        .iat[0],
        npf.fv(
            rate=convert_rate_monthly(
                with_contrib_assumptions["base_mkt_interest_per_yr"]
            ),
            nper=months_post_retirement,
            pmt=0,
            pv=-1 * retirement_account_upon_retirement,
            when="beginning",
        ),
    ), "With contributions savings failed"
