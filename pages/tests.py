from datetime import date
from functools import cached_property
from unittest.mock import patch

from django.test import SimpleTestCase

from .base_scenario import BaseScenario, RetirementPension
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


def _pension_assumptions(
    pension_start_age_yrs: int = 65,
    pension_start_age_mos: int = 0,
    monthly_pension: float = 1000.0,
) -> dict:
    """Return a minimal assumptions dict that includes a pension retirement account."""
    return {
        "birthdate": date(2000, 1, 1),
        "retirement_age_yrs": pension_start_age_yrs,
        "retirement_age_mos": pension_start_age_mos,
        "add_healthcare": False,
        "medicare_coverage_type": "standard",
        "private_insurance_per_mo": None,
        "retirement_extra_expenses": 0,
        "base_savings": 50000,
        "base_saved_per_mo": 500,
        "base_savings_per_yr_increase": 0,
        "savings_lower_limit": 10000,
        "base_monthly_bills": 2000,
        "payment_items": [],
        "retirement_accounts": [
            {
                "retirement_type": "pension",
                "base_retirement": 0,
                "base_retirement_per_mo": monthly_pension,
                "base_retirement_per_yr_increase": 0,
                "pension_start_age_yrs": pension_start_age_yrs,
                "pension_start_age_mos": pension_start_age_mos,
            }
        ],
        "ss_incl": False,
        "base_rf_interest_per_yr": 1.0,
        "base_mkt_interest_per_yr": 4.0,
        "base_inflation_per_yr": 3.0,
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


class RetirementPensionTests(SimpleTestCase):
    def test_pension_is_in_retirement_list(self):
        """A pension retirement account appears in the scenario's retirement_list."""
        scenario = FixedStartBaseScenario(assumptions=_pension_assumptions())
        self.assertEqual(len(scenario.retirement_list), 1)
        self.assertIsInstance(scenario.retirement_list[0], RetirementPension)

    def test_pension_has_zero_payments_before_start_date(self):
        """Pension payments are 0 for all months before the pension start date."""
        scenario = FixedStartBaseScenario(
            assumptions=_pension_assumptions(pension_start_age_yrs=65)
        )
        pension = scenario.retirement_list[0]
        pre_pension_payments = [
            payment
            for month, payment in zip(pension.month_list, pension.pension_payment_list)
            if month < pension.pension_start_date
        ]
        self.assertTrue(len(pre_pension_payments) > 0, "Expected some pre-pension months")
        self.assertTrue(all(p == 0.0 for p in pre_pension_payments))

    def test_pension_payments_start_at_pension_start_date(self):
        """Pension payments are non-zero starting at the pension start date."""
        scenario = FixedStartBaseScenario(
            assumptions=_pension_assumptions(pension_start_age_yrs=65, monthly_pension=1500.0)
        )
        pension = scenario.retirement_list[0]
        post_pension_payments = [
            payment
            for month, payment in zip(pension.month_list, pension.pension_payment_list)
            if month >= pension.pension_start_date
        ]
        self.assertTrue(len(post_pension_payments) > 0, "Expected some post-pension months")
        self.assertTrue(all(p > 0.0 for p in post_pension_payments))

    def test_pension_payment_increases_over_time(self):
        """Pension payments grow over time due to inflation adjustment (COLA)."""
        scenario = FixedStartBaseScenario(
            assumptions=_pension_assumptions(
                pension_start_age_yrs=65,
                monthly_pension=1000.0,
            )
        )
        pension = scenario.retirement_list[0]
        post_pension_payments = [
            payment
            for month, payment in zip(pension.month_list, pension.pension_payment_list)
            if month >= pension.pension_start_date
        ]
        self.assertGreater(post_pension_payments[-1], post_pension_payments[0])

    def test_pension_has_no_pre_retirement_contributions(self):
        """Pension retirement_increase_list is all zeros (no contributions)."""
        scenario = FixedStartBaseScenario(assumptions=_pension_assumptions())
        pension = scenario.retirement_list[0]
        self.assertTrue(all(x == 0.0 for x in pension.retirement_increase_list))

    def test_pension_start_age_is_independent_of_retirement_age(self):
        """Pension can have a different start age from the main retirement age."""
        assumptions = _pension_assumptions(
            pension_start_age_yrs=67, pension_start_age_mos=0, monthly_pension=1200.0
        )
        # Override retirement age to be different from pension start age
        assumptions = {**assumptions, "retirement_age_yrs": 62, "retirement_age_mos": 0}
        scenario = BaseScenario(assumptions=assumptions)
        pension = scenario.retirement_list[0]
        self.assertEqual(pension.pension_start_age_yrs, 67)
        self.assertEqual(pension.pension_start_age_mos, 0)

    def test_pension_income_added_to_savings_at_retirement(self):
        """Pension income increases savings relative to a scenario without a pension."""
        pension_assumptions = _pension_assumptions(
            pension_start_age_yrs=65, monthly_pension=1000.0
        )
        no_pension_assumptions = {
            **pension_assumptions,
            "retirement_accounts": [],
        }
        with_pension = BaseScenario(assumptions=pension_assumptions)
        without_pension = BaseScenario(assumptions=no_pension_assumptions)

        savings_with = with_pension.savings_retirement_account_list[0]
        savings_without = without_pension.savings_retirement_account_list[0]

        months_until_retirement = with_pension.months_until_retirement
        post_retire_with = savings_with[months_until_retirement:]
        post_retire_without = savings_without[months_until_retirement:]

        avg_with = sum(post_retire_with) / len(post_retire_with)
        avg_without = sum(post_retire_without) / len(post_retire_without)
        self.assertGreater(avg_with, avg_without)
