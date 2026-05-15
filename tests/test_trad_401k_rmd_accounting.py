"""Regression tests for Traditional 401k RMD transfer/tax accounting."""

from datetime import date

import pytest

from pages.base_scenario import BaseScenario
from pages.random_scenario import RandomScenario


@pytest.fixture
# Assumptions that isolate traditional 401k RMD flows from threshold-driven withdrawals.
def rmd_only_assumptions():
    return {
        "birthdate": date(1970, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 1_000_000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 500_000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            }
        ],
        "ss_incl": False,
        "base_rf_interest_per_yr": 2.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }


@pytest.fixture
# Edge-case assumptions with no traditional 401k account configured.
def no_trad_401k_assumptions():
    return {
        "birthdate": date(1970, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 1_000_000.0,
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


# Base scenario CSV fields should satisfy: trad_401k_rmd == traditional_401k_transfer + trad_401k_tax each month.
def test_base_df_rmd_equals_traditional_401k_transfer_plus_tax_each_month(
    rmd_only_assumptions,
):
    base_df = BaseScenario(assumptions=rmd_only_assumptions).create_base_df()

    assert (base_df["trad_401k_rmd"] > 0).any()
    for month_index, row in base_df.iterrows():
        assert row["trad_401k_rmd"] == pytest.approx(
            row["traditional_401k_transfer"] + row["trad_401k_tax"],
            abs=1e-6,
        ), (
            f"Month {month_index}: expected rmd {row['trad_401k_rmd']} to equal "
            f"transfer+tax {row['traditional_401k_transfer'] + row['trad_401k_tax']}"
        )


# Random scenario CSV fields should satisfy: var_trad_401k_rmd == var_traditional_401k_transfer + var_trad_401k_tax each month.
def test_random_df_rmd_equals_traditional_401k_transfer_plus_tax_each_month(
    rmd_only_assumptions,
):
    base_scenario = BaseScenario(assumptions=rmd_only_assumptions)
    random_df = RandomScenario(base_scenario=base_scenario).create_full_df()

    assert (random_df["var_trad_401k_rmd"] > 0).any()
    for month_index, row in random_df.iterrows():
        assert row["var_trad_401k_rmd"] == pytest.approx(
            row["var_traditional_401k_transfer"] + row["var_trad_401k_tax"],
            abs=1e-6,
        ), (
            f"Month {month_index}: expected var rmd {row['var_trad_401k_rmd']} to equal "
            f"transfer+tax {row['var_traditional_401k_transfer'] + row['var_trad_401k_tax']}"
        )


# With no traditional 401k account, RMD/transfer/tax fields should remain zero for every month.
def test_base_df_rmd_transfer_and_tax_are_zero_without_traditional_401k(
    no_trad_401k_assumptions,
):
    base_df = BaseScenario(assumptions=no_trad_401k_assumptions).create_base_df()

    assert (base_df["trad_401k_rmd"] == 0.0).all()
    assert (base_df["traditional_401k_transfer"] == 0.0).all()
    assert (base_df["trad_401k_tax"] == 0.0).all()


# Random scenario should also keep var RMD/transfer/tax at zero without a traditional 401k account.
def test_random_df_rmd_transfer_and_tax_are_zero_without_traditional_401k(
    no_trad_401k_assumptions,
):
    base_scenario = BaseScenario(assumptions=no_trad_401k_assumptions)
    random_df = RandomScenario(base_scenario=base_scenario).create_full_df()

    assert (random_df["var_trad_401k_rmd"] == 0.0).all()
    assert (random_df["var_traditional_401k_transfer"] == 0.0).all()
    assert (random_df["var_trad_401k_tax"] == 0.0).all()
