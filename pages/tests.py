from datetime import date
from functools import cached_property
from unittest.mock import patch

from django.test import SimpleTestCase

from .base_scenario import BaseScenario
from .random_scenario import RandomScenario


class FixedStartBaseScenario(BaseScenario):
    @cached_property
    def start_date(self) -> date:
        return date(2026, 1, 1)


def _base_assumptions(base_mkt_interest_per_yr: float) -> dict:
    return {
        "birthdate": date(2000, 1, 1),
        "retirement_age_yrs": 29,
        "retirement_age_mos": 0,
        "base_mkt_interest_per_yr": base_mkt_interest_per_yr,
    }


class ConservativeRetirementRateTests(SimpleTestCase):
    def test_base_scenario_steps_down_annually_to_five_percent_floor(self):
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(8.0))
        yearly_rates = scenario.conservative_yearly_mkt_interest

        self.assertEqual(yearly_rates[0], 0.08)
        self.assertEqual(yearly_rates[12], 0.07)
        self.assertEqual(yearly_rates[24], 0.06)
        self.assertEqual(yearly_rates[36], 0.05)
        self.assertEqual(yearly_rates[48], 0.05)

    def test_base_scenario_does_not_adjust_when_start_rate_is_below_floor(self):
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(4.0))
        yearly_rates = scenario.conservative_yearly_mkt_interest

        self.assertEqual(yearly_rates[0], 0.04)
        self.assertEqual(yearly_rates[12], 0.04)
        self.assertEqual(yearly_rates[24], 0.04)

    def test_random_scenario_uses_conservative_annual_schedule(self):
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(8.0))
        random_scenario = RandomScenario(base_scenario=scenario)

        with patch(
            "pages.random_scenario.np.random.normal",
            side_effect=lambda mean, _std: mean,
        ):
            yearly_rates = random_scenario.var_yearly_mkt_interest

        self.assertEqual(yearly_rates[0], 0.08)
        self.assertEqual(yearly_rates[12], 0.07)
        self.assertEqual(yearly_rates[24], 0.06)
        self.assertEqual(yearly_rates[36], 0.05)
