"""Tests for stochastic_finances_func output aggregation behavior."""

import random
from datetime import date
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from pages import stochastic_finances_func
from pages.base_scenario import BaseScenario
from pages.random_scenario import RandomScenario


class StubBaseScenario:
    """Minimal BaseScenario stub for deterministic aggregation tests."""

    def __init__(self, _assumptions):
        self.retirement_list = [SimpleNamespace(name="traditional_401k")]

    def create_base_df(self):
        return pd.DataFrame(
            {
                "count": [0, 1],
                "age_yrs": [40, 60],
                "age_mos": [0, 0],
                "savings_account": [1000.0, 1000.0],
                "traditional_401k": [500.0, 500.0],
            }
        )


class StubRandomScenario:
    """Minimal RandomScenario stub with predictable per-scenario balances."""

    def __init__(self, base_scenario, **_kwargs):
        self.base_scenario = base_scenario
        self.base_scenario.scenario_counter = (
            getattr(self.base_scenario, "scenario_counter", 0) + 1
        )
        self.scenario_id = self.base_scenario.scenario_counter
        self._df = pd.DataFrame(
            {
                "count": [0, 1],
                "var_savings_account": [
                    float(self.scenario_id),
                    float(self.scenario_id),
                ],
                "var_traditional_401k": [
                    float(self.scenario_id * 2),
                    float(self.scenario_id * 2),
                ],
            }
        )

    def create_full_df(self):
        return self._df


@pytest.fixture
def deterministic_scenario_stubs(monkeypatch):
    """Patch stochastic_finances_func to deterministic in-memory scenario stubs."""
    monkeypatch.setattr(stochastic_finances_func, "BaseScenario", StubBaseScenario)
    monkeypatch.setattr(stochastic_finances_func, "RandomScenario", StubRandomScenario)
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda self, *args, **kwargs: None)


# Ensures savings average calculation excludes the base scenario account_0 column.
def test_main_savings_avg_uses_only_random_scenarios(deterministic_scenario_stubs):
    """Validate savings averages use only random scenario paths."""
    total_savings_df, _ = stochastic_finances_func.main(assumptions={})

    assert "account_0" not in total_savings_df.columns
    # Mean of integers 1..100 from stub var_savings_account values.
    assert total_savings_df["avg"].iat[0] == pytest.approx(50.5, rel=1e-6)


# Ensures retirement average calculation excludes base scenario columns ending in _0.
def test_main_retirement_avg_uses_only_random_scenarios(deterministic_scenario_stubs):
    """Validate retirement averages use only random scenario paths."""
    _, total_retirement_df = stochastic_finances_func.main(assumptions={})

    assert "traditional_401k_0" not in total_retirement_df.columns
    # Mean of values 2,4,...,200 from stub var_traditional_401k values.
    assert total_retirement_df["avg_traditional_401k"].iat[0] == pytest.approx(
        101.0, rel=1e-6
    )


# ────────────────────────────────────────────────────────────────────────────────
# Zero-variance comparison tests: BaseScenario vs RandomScenario with matching outputs
# ────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def zero_variance_assumptions_with_retirement():
    """Fixture with diversified retirement accounts for zero-variance testing."""
    return {
        "birthdate": date(1970, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 100_000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 250_000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
            {
                "retirement_type": "roth_401k",
                "base_retirement": 150_000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
            {
                "retirement_type": "traditional_ira",
                "base_retirement": 100_000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
            },
        ],
        "ss_incl": False,
        "base_rf_interest_per_yr": 3.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }


@pytest.fixture
def zero_variance_scenarios(zero_variance_assumptions_with_retirement, monkeypatch):
    """Patch randomness to zero and return (base_df, random_df) for comparison."""
    monkeypatch.setattr(np.random, "normal", lambda mean, std_dev: mean)
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    base = BaseScenario(assumptions=zero_variance_assumptions_with_retirement)
    rand = RandomScenario(base_scenario=base)
    return base.create_base_df(), rand.create_full_df()


# When variance is zero, savings account in base scenario should exactly match var_savings_account in random scenario.
def test_zero_variance_savings_account_matches(zero_variance_scenarios):
    """Validate savings balance is identical in base and random with zero variance."""
    base_df, random_df = zero_variance_scenarios
    base_savings = base_df["savings_account"].values
    random_savings = random_df["var_savings_account"].values

    assert len(base_savings) == len(random_savings)
    for i, (base_val, random_val) in enumerate(zip(base_savings, random_savings)):
        assert base_val == pytest.approx(
            random_val, abs=1e-6
        ), f"Month {i}: base savings {base_val} != random savings {random_val}"


# When variance is zero, traditional_401k balance in base should match var_traditional_401k in random for every month.
def test_zero_variance_traditional_401k_matches(zero_variance_scenarios):
    """Validate traditional_401k balance is identical in base and random with zero variance."""
    base_df, random_df = zero_variance_scenarios
    base_trad_401k = base_df["traditional_401k"].values
    random_trad_401k = random_df["var_traditional_401k"].values

    assert len(base_trad_401k) == len(random_trad_401k)
    for i, (base_val, random_val) in enumerate(zip(base_trad_401k, random_trad_401k)):
        assert base_val == pytest.approx(
            random_val, abs=1e-6
        ), f"Month {i}: base trad_401k {base_val} != random trad_401k {random_val}"


# When variance is zero, roth_401k balance in base should match var_roth_401k in random for every month.
def test_zero_variance_roth_401k_matches(zero_variance_scenarios):
    """Validate roth_401k balance is identical in base and random with zero variance."""
    base_df, random_df = zero_variance_scenarios
    base_roth_401k = base_df["roth_401k"].values
    random_roth_401k = random_df["var_roth_401k"].values

    assert len(base_roth_401k) == len(random_roth_401k)
    for i, (base_val, random_val) in enumerate(zip(base_roth_401k, random_roth_401k)):
        assert base_val == pytest.approx(
            random_val, abs=1e-6
        ), f"Month {i}: base roth_401k {base_val} != random roth_401k {random_val}"


# When variance is zero, traditional_ira balance in base should match var_traditional_ira in random for every month.
def test_zero_variance_traditional_ira_matches(zero_variance_scenarios):
    """Validate traditional_ira balance is identical in base and random with zero variance."""
    base_df, random_df = zero_variance_scenarios
    base_trad_ira = base_df["traditional_ira"].values
    random_trad_ira = random_df["var_traditional_ira"].values

    assert len(base_trad_ira) == len(random_trad_ira)
    for i, (base_val, random_val) in enumerate(zip(base_trad_ira, random_trad_ira)):
        assert base_val == pytest.approx(
            random_val, abs=1e-6
        ), f"Month {i}: base trad_ira {base_val} != random trad_ira {random_val}"
