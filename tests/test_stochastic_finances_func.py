"""Tests for stochastic_finances_func output aggregation behavior."""

from types import SimpleNamespace

import pandas as pd
import pytest

from pages import stochastic_finances_func


class StubBaseScenario:
    """Minimal BaseScenario stub for deterministic aggregation tests."""

    def __init__(self, assumptions):
        _ = assumptions
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

    scenario_counter = 0

    def __init__(self, base_scenario):
        self.base_scenario = base_scenario
        type(self).scenario_counter += 1
        self.scenario_id = type(self).scenario_counter
        self._df = pd.DataFrame(
            {
                "count": [0, 1],
                "var_savings_account": [float(self.scenario_id), float(self.scenario_id)],
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
    StubRandomScenario.scenario_counter = 0
    monkeypatch.setattr(stochastic_finances_func, "BaseScenario", StubBaseScenario)
    monkeypatch.setattr(stochastic_finances_func, "RandomScenario", StubRandomScenario)
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda self, *args, **kwargs: None)


# Savings averages should be computed from stochastic scenario CSV paths, not account_0.
def test_main_savings_avg_uses_only_random_scenarios(deterministic_scenario_stubs):
    total_savings_df, _ = stochastic_finances_func.main(assumptions={})

    assert "account_0" not in total_savings_df.columns
    assert total_savings_df["avg"].iat[0] == pytest.approx(50.5, rel=1e-6)


# Retirement averages should be computed from stochastic scenario CSV paths, not *_0.
def test_main_retirement_avg_uses_only_random_scenarios(deterministic_scenario_stubs):
    _, total_retirement_df = stochastic_finances_func.main(assumptions={})

    assert "traditional_401k_0" not in total_retirement_df.columns
    assert total_retirement_df["avg_traditional_401k"].iat[0] == pytest.approx(
        101.0, rel=1e-6
    )
