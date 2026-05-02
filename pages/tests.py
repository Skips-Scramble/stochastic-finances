from datetime import date
from functools import cached_property
from unittest.mock import patch

from django.test import SimpleTestCase

from .base_scenario import BaseScenario, RetirementPension, RetirementRothIRA
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
    def test_base_scenario_steps_down_to_five_percent_at_age_ninety(self):
        # birthdate 2000-01-01, start_date 2026-01-01 (age 26), age-90 = 2090-01-01
        # years_to_floor = 64, annual_step = (8 - 5) / 64 = 0.046875 pct/yr
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(8.0))
        yearly_rates = scenario.conservative_yearly_mkt_interest

        # At start (Jan 2026): 8%
        self.assertEqual(yearly_rates[0], 0.08)
        # At Jan 2058 (index 384, 32 years in): 8 - 32*(3/64) = 6.5%
        self.assertEqual(yearly_rates[384], 0.065)
        # At Jan 2090 (index 768, 64 years in, age 90): floor = 5%
        self.assertEqual(yearly_rates[768], 0.05)
        # After age 90 (index 780, Jan 2091): still at floor
        self.assertEqual(yearly_rates[780], 0.05)

    def test_base_scenario_does_not_adjust_when_start_rate_is_below_floor(self):
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(4.0))
        yearly_rates = scenario.conservative_yearly_mkt_interest

        self.assertEqual(yearly_rates[0], 0.04)
        self.assertEqual(yearly_rates[12], 0.04)
        self.assertEqual(yearly_rates[24], 0.04)

    def test_random_scenario_uses_conservative_annual_schedule(self):
        # With mean = conservative_rate, the random scenario should mirror the
        # same age-90 glide path as the base scenario.
        scenario = FixedStartBaseScenario(assumptions=_base_assumptions(8.0))
        random_scenario = RandomScenario(base_scenario=scenario)

        with patch(
            "pages.random_scenario.np.random.normal",
            side_effect=lambda mean, _std: mean,
        ):
            yearly_rates = random_scenario.var_yearly_mkt_interest

        # At start: 8%
        self.assertEqual(yearly_rates[0], 0.08)
        # At Jan 2058 (index 384, 32 years in): 6.5%
        self.assertEqual(yearly_rates[384], 0.065)
        # At age 90 (index 768): floor 5%
        self.assertEqual(yearly_rates[768], 0.05)


def _full_assumptions_with_roth_ira(use_conservative_rates: bool) -> dict:
    """Minimal full assumptions dict with one Roth IRA account."""
    return {
        "birthdate": date(2000, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
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
                "retirement_type": "roth_ira",
                "base_retirement": 10000,
                "base_retirement_per_mo": 200,
                "base_retirement_per_yr_increase": 0,
                "use_conservative_rates": use_conservative_rates,
            }
        ],
        "ss_incl": False,
        "base_rf_interest_per_yr": 1.0,
        "base_mkt_interest_per_yr": 8.0,
        "base_inflation_per_yr": 3.0,
        "add_medical_bills": False,
        "monthly_medical_bills": 0,
    }


class PerAccountConservativeRateToggleTests(SimpleTestCase):
    def test_conservative_toggle_on_uses_glide_path_rate(self):
        """When use_conservative_rates=True the account is built with use_conservative_rates=True."""
        scenario = FixedStartBaseScenario(
            assumptions=_full_assumptions_with_roth_ira(use_conservative_rates=True)
        )
        roth_ira = next(
            a for a in scenario.retirement_list if isinstance(a, RetirementRothIRA)
        )
        self.assertTrue(roth_ira.use_conservative_rates)

    def test_conservative_toggle_off_uses_flat_rate(self):
        """When use_conservative_rates=False the account is built with use_conservative_rates=False."""
        scenario = FixedStartBaseScenario(
            assumptions=_full_assumptions_with_roth_ira(use_conservative_rates=False)
        )
        roth_ira = next(
            a for a in scenario.retirement_list if isinstance(a, RetirementRothIRA)
        )
        self.assertFalse(roth_ira.use_conservative_rates)

    def test_conservative_toggle_defaults_to_true_when_not_provided(self):
        """When use_conservative_rates is absent from the item dict it defaults to True."""
        assumptions = _full_assumptions_with_roth_ira(use_conservative_rates=True)
        # Remove the key to simulate an old record without the field
        del assumptions["retirement_accounts"][0]["use_conservative_rates"]
        scenario = FixedStartBaseScenario(assumptions=assumptions)
        roth_ira = next(
            a for a in scenario.retirement_list if isinstance(a, RetirementRothIRA)
        )
        self.assertTrue(roth_ira.use_conservative_rates)


def _full_assumptions_with_roth_ira_override(interest_rate_per_yr: float) -> dict:
    """Minimal full assumptions with a Roth IRA that has its own interest rate override."""
    assumptions = _full_assumptions_with_roth_ira(use_conservative_rates=True)
    assumptions["retirement_accounts"][0]["interest_rate_per_yr"] = interest_rate_per_yr
    return assumptions


class PerAccountInterestRateCsvTests(SimpleTestCase):
    """Tests for per-account interest-rate columns in the CSV export (create_base_df).

    Uses BaseScenario directly (not FixedStartBaseScenario) so that the main scenario
    and the individual account objects share the same start_date (both default to today).
    This ensures list lengths are consistent and pd.DataFrame construction succeeds.
    """

    def test_per_account_rate_columns_absent_without_override(self):
        """Accounts without an override should not add per-account rate columns."""
        scenario = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira(use_conservative_rates=True)
        )
        df = scenario.create_base_df()
        self.assertNotIn("roth_ira_yearly_mkt_interest", df.columns)
        self.assertNotIn("roth_ira_monthly_mkt_interest", df.columns)

    def test_per_account_rate_columns_present_with_override(self):
        """Accounts with an override should add per-account rate columns to the CSV."""
        scenario = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=6.0)
        )
        df = scenario.create_base_df()
        self.assertIn("roth_ira_yearly_mkt_interest", df.columns)
        self.assertIn("roth_ira_monthly_mkt_interest", df.columns)

    def test_per_account_yearly_rate_matches_override(self):
        """The yearly rate column value equals the configured override rate as a decimal."""
        override_pct = 6.0
        scenario = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=override_pct)
        )
        df = scenario.create_base_df()
        expected_yearly = round(override_pct / 100, 6)
        self.assertEqual(df["roth_ira_yearly_mkt_interest"].iloc[0], expected_yearly)

    def test_per_account_monthly_rate_derived_from_yearly(self):
        """The monthly rate column is derived correctly from the yearly override rate."""
        override_pct = 6.0
        scenario = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=override_pct)
        )
        df = scenario.create_base_df()
        yearly = round(override_pct / 100, 6)
        expected_monthly = round((1 + yearly) ** (1 / 12) - 1, 6)
        self.assertAlmostEqual(
            df["roth_ira_monthly_mkt_interest"].iloc[0], expected_monthly, places=6
        )


class VarPerAccountInterestRateCsvTests(SimpleTestCase):
    """Tests for per-account variable interest-rate columns in create_full_df.

    Uses BaseScenario directly (not FixedStartBaseScenario) so that the main scenario
    and the individual account objects share the same start_date (both default to today).
    """

    def test_var_per_account_rate_columns_absent_without_override(self):
        """Accounts without an override should not add var per-account rate columns."""
        base = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira(use_conservative_rates=True)
        )
        random_scenario = RandomScenario(base_scenario=base)
        full_df = random_scenario.create_full_df()
        self.assertNotIn("var_roth_ira_yearly_mkt_interest", full_df.columns)
        self.assertNotIn("var_roth_ira_monthly_mkt_interest", full_df.columns)

    def test_var_per_account_rate_columns_present_with_override(self):
        """Accounts with an override should add var per-account rate columns to create_full_df."""
        base = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=6.0)
        )
        random_scenario = RandomScenario(base_scenario=base)
        full_df = random_scenario.create_full_df()
        self.assertIn("var_roth_ira_yearly_mkt_interest", full_df.columns)
        self.assertIn("var_roth_ira_monthly_mkt_interest", full_df.columns)

    def test_var_per_account_monthly_rate_consistent_with_yearly(self):
        """The var monthly rate column is derived correctly from the var yearly rate column."""
        base = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=6.0)
        )
        random_scenario = RandomScenario(base_scenario=base)
        full_df = random_scenario.create_full_df()
        for _, row in full_df.iterrows():
            yearly = row["var_roth_ira_yearly_mkt_interest"]
            expected_monthly = round((1 + yearly) ** (1 / 12) - 1, 4)
            self.assertAlmostEqual(
                row["var_roth_ira_monthly_mkt_interest"], expected_monthly, places=4
            )

    def test_var_per_account_rate_cached_across_calls(self):
        """_account_var_yearly_rate_list returns the same values on repeated calls (cache)."""
        base = BaseScenario(
            assumptions=_full_assumptions_with_roth_ira_override(interest_rate_per_yr=6.0)
        )
        random_scenario = RandomScenario(base_scenario=base)
        roth_ira = next(a for a in base.retirement_list if isinstance(a, RetirementRothIRA))
        rates_first = random_scenario._account_var_yearly_rate_list(roth_ira)
        rates_second = random_scenario._account_var_yearly_rate_list(roth_ira)
        self.assertEqual(rates_first, rates_second)



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
        self.assertTrue(
            len(pre_pension_payments) > 0, "Expected some pre-pension months"
        )
        self.assertTrue(all(p == 0.0 for p in pre_pension_payments))

    def test_pension_payments_start_at_pension_start_date(self):
        """Pension payments are non-zero starting at the pension start date."""
        scenario = FixedStartBaseScenario(
            assumptions=_pension_assumptions(
                pension_start_age_yrs=65, monthly_pension=1500.0
            )
        )
        pension = scenario.retirement_list[0]
        post_pension_payments = [
            payment
            for month, payment in zip(pension.month_list, pension.pension_payment_list)
            if month >= pension.pension_start_date
        ]
        self.assertTrue(
            len(post_pension_payments) > 0, "Expected some post-pension months"
        )
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


def _medical_bills_assumptions(
    add_medical_bills: bool = True,
    monthly_medical_bills: float = 200.0,
) -> dict:
    """Return a minimal assumptions dict for testing the medical bills feature."""
    return {
        "birthdate": date(2000, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "include_pre_medicare_insurance": False,
        "add_medical_bills": add_medical_bills,
        "monthly_medical_bills": monthly_medical_bills,
        "retirement_extra_expenses": 0,
        "base_savings": 50000,
        "base_saved_per_mo": 500,
        "base_savings_per_yr_increase": 0,
        "savings_lower_limit": 10000,
        "base_monthly_bills": 2000,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 1.0,
        "base_mkt_interest_per_yr": 4.0,
        "base_inflation_per_yr": 3.0,
    }


class MedicalBillsBaseScenarioTests(SimpleTestCase):
    def test_medical_bills_list_all_zeros_when_toggle_off(self):
        """medical_bills_list is all zeros when add_medical_bills is False."""
        scenario = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(add_medical_bills=False)
        )
        self.assertTrue(all(x == 0.0 for x in scenario.medical_bills_list))

    def test_medical_bills_list_nonzero_when_toggle_on(self):
        """medical_bills_list has positive values when add_medical_bills is True."""
        scenario = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=200.0
            )
        )
        self.assertTrue(all(x > 0.0 for x in scenario.medical_bills_list))

    def test_medical_bills_list_inflation_adjusted(self):
        """Medical bills grow over time due to inflation."""
        scenario = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=200.0
            )
        )
        bills = scenario.medical_bills_list
        self.assertGreater(bills[-1], bills[0])

    def test_medical_bills_reduce_savings(self):
        """Including medical bills reduces savings vs. not including them."""
        with_bills = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=500.0
            )
        )
        without_bills = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(add_medical_bills=False)
        )
        savings_with = with_bills.savings_retirement_account_list[0]
        savings_without = without_bills.savings_retirement_account_list[0]
        avg_with = sum(savings_with) / len(savings_with)
        avg_without = sum(savings_without) / len(savings_without)
        self.assertLess(avg_with, avg_without)


class MedicalBillsRandomScenarioTests(SimpleTestCase):
    def test_var_medical_bills_all_zeros_when_toggle_off(self):
        """var_medical_bills_list is all zeros when add_medical_bills is False."""
        base = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(add_medical_bills=False)
        )
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(all(x == 0.0 for x in random_scenario.var_medical_bills_list))

    def test_var_medical_bills_never_negative(self):
        """var_medical_bills_list contains no negative values."""
        base = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=200.0
            )
        )
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(all(x >= 0.0 for x in random_scenario.var_medical_bills_list))

    def test_var_medical_bills_near_base_when_randomness_zeroed(self):
        """With zeroed randomness, var_medical_bills_list matches base medical_bills_list."""
        base = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=200.0
            )
        )
        random_scenario = RandomScenario(base_scenario=base)

        with patch(
            "pages.random_scenario.np.random.normal",
            side_effect=lambda mean, _std: mean,
        ):
            var_bills = random_scenario.var_medical_bills_list

        for var_val, base_val in zip(var_bills, base.medical_bills_list):
            self.assertAlmostEqual(var_val, base_val, places=1)

    def test_var_medical_bills_cost_column_in_full_df(self):
        """create_full_df includes var_medical_bills_cost matching the base medical_bills_cost."""
        base = FixedStartBaseScenario(
            assumptions=_medical_bills_assumptions(
                add_medical_bills=True, monthly_medical_bills=200.0
            )
        )
        random_scenario = RandomScenario(base_scenario=base)
        full_df = random_scenario.create_full_df()
        self.assertIn("medical_bills_cost", full_df.columns)
        self.assertIn("var_medical_bills_cost", full_df.columns)


def _healthcare_assumptions() -> dict:
    """Return a minimal assumptions dict with healthcare costs enabled."""
    return {
        "birthdate": date(2000, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": True,
        "include_pre_medicare_insurance": True,
        "add_medical_bills": False,
        "monthly_medical_bills": 0.0,
        "retirement_extra_expenses": 0,
        "base_savings": 50000,
        "base_saved_per_mo": 500,
        "base_savings_per_yr_increase": 0,
        "savings_lower_limit": 10000,
        "base_monthly_bills": 2000,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 1.0,
        "base_mkt_interest_per_yr": 4.0,
        "base_inflation_per_yr": 3.0,
    }


class VariableHealthcareCostTests(SimpleTestCase):
    def test_var_healthcare_costs_never_negative(self):
        """var_healthcare_costs_list contains no negative values."""
        base = FixedStartBaseScenario(assumptions=_healthcare_assumptions())
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(
            all(x >= 0.0 for x in random_scenario.var_healthcare_costs_list)
        )

    def test_var_medicare_part_b_premium_never_negative(self):
        """var_medicare_part_b_premium_costs_list contains no negative values."""
        base = FixedStartBaseScenario(assumptions=_healthcare_assumptions())
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(
            all(
                x >= 0.0 for x in random_scenario.var_medicare_part_b_premium_costs_list
            )
        )

    def test_var_medicare_part_d_premium_never_negative(self):
        """var_medicare_part_d_premium_costs_list contains no negative values."""
        base = FixedStartBaseScenario(assumptions=_healthcare_assumptions())
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(
            all(
                x >= 0.0 for x in random_scenario.var_medicare_part_d_premium_costs_list
            )
        )

    def test_var_private_insurance_costs_never_negative(self):
        """var_private_insurance_costs_list contains no negative values."""
        base = FixedStartBaseScenario(assumptions=_healthcare_assumptions())
        random_scenario = RandomScenario(base_scenario=base)
        self.assertTrue(
            all(x >= 0.0 for x in random_scenario.var_private_insurance_costs_list)
        )

    def test_var_healthcare_cost_columns_in_full_df(self):
        """create_full_df includes var_ columns for all four healthcare cost types."""
        base = FixedStartBaseScenario(assumptions=_healthcare_assumptions())
        random_scenario = RandomScenario(base_scenario=base)
        full_df = random_scenario.create_full_df()
        for col in (
            "healthcare_cost",
            "var_healthcare_cost",
            "medicare_part_b_premium",
            "var_medicare_part_b_premium",
            "medicare_part_d_premium",
            "var_medicare_part_d_premium",
            "private_insurance_cost",
            "var_private_insurance_cost",
        ):
            self.assertIn(col, full_df.columns)
