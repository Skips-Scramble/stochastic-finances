from dataclasses import dataclass
from functools import cached_property

import pandas as pd
import random
import numpy as np

from Scenarios.base_scenario import BaseScenario


@dataclass
class RandomScenario:
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
            elif index % self.base_scenario.assumptions["rf_interest_change_mos"] != 0:
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

    # @cached_property
    # def var_inflation_yrly_list(self) -> list:
    #     """Calculate a random monthly inflation rate"""
    #     variable_inflation_list = []
    #     for index, rate in enumerate(self.var_rf_interest_yrly_list):
    #         if index % self.base_scenario.assumptions["rf_interest_change_mos"] != 0:
    #             variable_inflation_list.append(variable_inflation_list[index - 1])
    #         else:
    #             variable_inflation_list.append(
    #                 round(rate + random.randint(-5, 5) * 0.001, 4)
    #             )

    #     return variable_inflation_list

    # @cached_property
    # def var_inflation_monthly_list(self) -> list:
    #     """Take the annualized risk free rate and create a monthly rate"""
    #     return [
    #         round(((1 + x) ** (1 / 12) - 1), 6) for x in self.var_inflation_yrly_list
    #     ]

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
    def var_savings_retirement_account_list(self) -> [list, list]:
        """Calculate amount in your savings account by month"""
        total_non_base_bills_list = [
            sum(sublist) for sublist in zip(*self.base_scenario.non_base_bills_lists)
        ]
        var_savings_list = []
        var_retirement_list = []
        for i in range(self.base_scenario.total_months):
            if i == 0:
                savings = float(
                    round(self.base_scenario.assumptions["base_savings"], 2)
                )
                retirement = float(
                    round(self.base_scenario.assumptions["base_retirement"], 2)
                )
            elif (
                self.base_scenario.pre_retire_month_count_list[i] != 0
            ):  # If you're not retired
                savings = float(
                    round(
                        (
                            savings
                            + self.var_savings_increase_list[i]
                            - total_non_base_bills_list[i]
                        )
                        * (1 + self.var_monthly_rf_interest[i]),
                        2,
                    )
                )
                retirement = float(
                    round(
                        (retirement + self.base_scenario.retirement_increase_list[i])
                        * (1 + self.var_monthly_mkt_interest[i]),
                        2,
                    )
                )
            else:  # If you are retired
                if (
                    var_savings_list[i - 1]
                    <= self.base_scenario.assumptions["savings_lower_limit"]
                ):
                    savings = float(
                        round(
                            var_savings_list[i - 1]
                            * (1 + self.var_monthly_rf_interest[i]),
                            2,
                        )
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - self.var_base_bills_list[i]
                                - total_non_base_bills_list[i]
                            )
                            * (1 + self.var_monthly_mkt_interest[i]),
                            2,
                        )
                    )
                else:
                    savings = float(
                        round(
                            (
                                savings
                                + self.var_savings_increase_list[i]
                                - (self.var_base_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                            )
                            * (1 + self.var_monthly_rf_interest[i]),
                            2,
                        )
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - (self.var_base_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                            )
                            * (1 + self.var_monthly_mkt_interest[i]),
                            2,
                        )
                    )
            var_savings_list.append(savings)
            var_retirement_list.append(retirement)
        return var_savings_list, var_retirement_list

    def create_full_df(self) -> pd.DataFrame:
        """Create full dataframe with base and variable scenarios"""
        var_df = pd.DataFrame(
            {
                "count": self.base_scenario.count_list,
                "var_yearly_rf_interest": self.var_yearly_rf_interest,
                "var_monthly_rf_interest": self.var_monthly_rf_interest,
                "var_base_bills": self.var_base_bills_list,
                "var_savings_increase": self.var_savings_increase_list,
                "var_savings_account": self.var_savings_retirement_account_list[0],
                "var_yearly_mkt_interest": self.var_yearly_mkt_interest,
                "var_monthly_mkt_interest": self.var_monthly_mkt_interest,
                "var_retirement_account": self.var_savings_retirement_account_list[1],
            }
        )
        return self.base_scenario.create_base_df().merge(var_df, on="count", how="left")
