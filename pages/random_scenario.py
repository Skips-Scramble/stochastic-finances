import random
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd

from .base_scenario import BaseScenario, RetirementRothIRA

RF_INTEREST_CHANGE_MOS = 6


@dataclass
class RandomScenario:
    """Encapsulates a stochastic financial simulation that perturbs
    rates and cash flows from a base scenario to produce monthly
    savings and retirement balances over time."""

    base_scenario: BaseScenario

    @cached_property
    def var_yearly_rf_interest(self) -> list:
        """Create list of risk free APYs by adjusting by random small amounts
        every so often, based on assumptions
        """
        base_list = [
            self.base_scenario.assumptions["base_rf_interest_per_yr"] / 100
            for _ in range(self.base_scenario.total_months)
        ]

        variable_rf_list = []
        for index, rate in enumerate(base_list):
            if index == 0:
                variable_rf_list.append(rate)
            elif index % RF_INTEREST_CHANGE_MOS != 0:
                variable_rf_list.append(variable_rf_list[index - 1])
            else:
                adj_factor = random.randint(-1, 1) * 0.0015
                variable_rf_list.append(
                    round(
                        min(max(0.001, variable_rf_list[index - 1] + adj_factor), 0.07),
                        6,
                    )
                )

        return variable_rf_list

    @cached_property
    def var_monthly_rf_interest(self) -> list:
        """Take the annualized risk free rate and create a monthly rate"""
        return [
            round(((1 + x) ** (1 / 12) - 1), 6) for x in self.var_yearly_rf_interest
        ]

    @cached_property
    def var_base_bills_list(self) -> list:
        """Calculate variable base bills (for retirement)
        The savings added list indirectly accounts for random changes in base bills
        """
        return [
            round(
                np.random.normal(
                    x,
                    x * (0.5),
                ),
                2,
            )
            for x in self.base_scenario.base_bills_list
        ]

    @cached_property
    def var_post_retire_extra_bills_list(self) -> list:
        """Calculate variable extra money spent post-retirment (on fun things)"""
        return [
            round(
                np.random.normal(
                    x,
                    x * (0.5),
                ),
                2,
            )
            for x in self.base_scenario.post_retire_extra_bills_list
        ]

    @cached_property
    def var_savings_increase_list(self) -> list:
        """Calculate the amount you save per month on random basis based on
        a normal distribution"""
        return [
            round(
                np.random.normal(
                    x,
                    x * (0.5),
                ),
                2,
            )
            for x in self.base_scenario.savings_increase_list
        ]

    @cached_property
    def var_yearly_mkt_interest(self) -> list:
        """Docstring"""
        return [
            round(
                np.random.normal(
                    self.base_scenario.assumptions["base_mkt_interest_per_yr"],
                    self.base_scenario.assumptions["base_mkt_interest_per_yr"] * 1.5,
                )
                / 100,
                4,
            )
            for _ in range(self.base_scenario.total_months)
        ]

    @cached_property
    def var_monthly_mkt_interest(self) -> list:
        """Docstring"""
        return [
            round(((1 + x) ** (1 / 12) - 1), 4) for x in self.var_yearly_mkt_interest
        ]

    @cached_property
    def var_savings_retirement_account_list(self) -> tuple[list, list]:
        """Calculate the amount of money in your savings and retirement accounts over time,
        stopping Roth IRA contributions and withdrawing contributions (not interest) when
        savings falls below threshold.
        """
        total_non_base_bills_list = [
            sum(sublist) for sublist in zip(*self.base_scenario.non_base_bills_lists)
        ]

        # Initialize account lists
        savings_list = []
        roth_ira_balance_list = []
        roth_ira_contributions_list = []

        # Track Roth IRA contributions separately from growth
        roth_ira_contributions = 0.0

        # Get Roth IRA account if it exists. Assume only one Roth IRA for simplicity.
        roth_ira = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementRothIRA):
                roth_ira = ret_account
                break

        for i in range(self.base_scenario.total_months):
            if i == 0:
                # Initialize accounts
                savings = float(
                    round(self.base_scenario.assumptions["base_savings"], 6)
                )
                roth_ira_bal = (
                    float(round(roth_ira.base_retirement, 6)) if roth_ira else 0.0
                )
                # Assume 70% of initial balance is contributions, 30% is growth
                # TODO: refine this assumption later
                roth_ira_contributions = roth_ira_bal * 0.7

            elif (
                self.base_scenario.pre_retire_month_count_list[i] != 0
            ):  # If you're not retired
                # Update savings (pay expenses from savings)
                savings = float(
                    round(
                        (
                            savings
                            + self.var_savings_increase_list[i]
                            - total_non_base_bills_list[i]
                            - self.base_scenario.healthcare_costs[i]
                        )
                        * (1 + self.var_monthly_rf_interest[i]),
                        6,
                    )
                )

                # If below threshold, pull from Roth IRA contributions
                # TODO: adjust below threshold to not get invoked until after a certain point
                below_threshold = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                    and i >= 12 * 10
                )
                if below_threshold and roth_ira_contributions > 0:
                    # Calculate how much we need to reach the threshold
                    withdrawal = min(
                        self.base_scenario.monthly_savings_threshold_list[i] - savings,
                        roth_ira_contributions,
                    )

                    # Update balances
                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions -= withdrawal

                # Grow Roth IRA with interest (and contributions if above threshold)
                if roth_ira:
                    if below_threshold:
                        # Below threshold: no new contributions, just grow existing balance
                        roth_ira_bal = float(
                            round(
                                roth_ira_bal * (1 + self.var_monthly_mkt_interest[i]),
                                6,
                            )
                        )
                    else:
                        # Above threshold: add contributions and grow
                        contribution = roth_ira.retirement_increase_list[i]
                        roth_ira_bal = float(
                            round(
                                (roth_ira_bal + contribution)
                                * (1 + self.var_monthly_mkt_interest[i]),
                                6,
                            )
                        )
                        # Track the contribution amount (before growth)
                        roth_ira_contributions += contribution

            else:  # If you are retired
                # Pay expenses from savings
                savings = float(
                    round(
                        (
                            savings
                            - (
                                self.var_base_bills_list[i]
                                + self.var_post_retire_extra_bills_list[i]
                                + total_non_base_bills_list[i]
                                + self.base_scenario.healthcare_costs[i]
                            )
                        )
                        * (1 + self.var_monthly_rf_interest[i]),
                        6,
                    )
                )

                # If below threshold, pull from Roth IRA contributions to reach threshold
                below_threshold = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if below_threshold and roth_ira and roth_ira_contributions > 0:
                    # Calculate how much we need to reach the threshold
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, roth_ira_contributions)

                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions -= withdrawal

                # Grow Roth IRA (no contributions in retirement)
                if roth_ira:
                    roth_ira_bal = float(
                        round(
                            roth_ira_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

            # Append current balances to lists
            savings_list.append(savings)
            roth_ira_balance_list.append(roth_ira_bal)
            roth_ira_contributions_list.append(roth_ira_contributions)

        return savings_list, roth_ira_balance_list

    def create_full_df(self) -> pd.DataFrame:
        """Create full dataframe with base and variable scenarios"""
        var_data = {
            "count": self.base_scenario.count_list,
            "var_yearly_rf_interest": self.var_yearly_rf_interest,
            "var_monthly_rf_interest": self.var_monthly_rf_interest,
            "var_base_bills": self.var_base_bills_list,
            "var_retire_extra": self.var_post_retire_extra_bills_list,
            "var_savings_increase": self.var_savings_increase_list,
            "var_savings_account": self.var_savings_retirement_account_list[0],
            "var_yearly_mkt_interest": self.var_yearly_mkt_interest,
            "var_monthly_mkt_interest": self.var_monthly_mkt_interest,
        }
        for ret_account in self.base_scenario.retirement_list:
            var_data[f"var_{ret_account.name}"] = ret_account.retirement_account_list

        var_df = pd.DataFrame(var_data)
        return self.base_scenario.create_base_df().merge(var_df, on="count", how="left")
