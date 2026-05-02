import random
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd

from .base_scenario import (
    BaseScenario,
    RetirementRothIRA,
    RetirementRoth401k,
    RetirementTrad401k,
    RetirementTradIRA,
    RetirementHSA,
    RetirementBrokerage,
    RetirementPension,
    ROTH_IRA_WITHDRAWAL_AGE_MOS,
    ROTH_IRA_WITHDRAWAL_AGE_YRS,
    HSA_WITHDRAWAL_AGE_YRS,
    TRAD_401K_TAX_RATE,
    BROKERAGE_TAX_RATE,
    MIN_CONSERVATIVE_RETIREMENT_RATE_PCT,
    uniform_lifetime_table,
)

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
    def var_medical_bills_list(self) -> list:
        """Calculate variable monthly medical bills.
        Uses low volatility (std = 10% of mean) and clamps to non-negative
        so the value never decreases savings below zero from this line item.
        Returns zeros when the toggle is off.
        """
        return [
            max(
                0.0,
                round(
                    np.random.normal(
                        x,
                        x * 0.1,
                    ),
                    2,
                ),
            )
            for x in self.base_scenario.medical_bills_list
        ]

    @cached_property
    def var_healthcare_costs_list(self) -> list:
        """Variable out-of-pocket healthcare costs.
        Uses low volatility (std = 10% of mean) and clamps to non-negative.
        Returns zeros when the toggle is off.
        """
        return [
            max(0.0, round(np.random.normal(x, x * 0.1), 2))
            for x in self.base_scenario.healthcare_costs
        ]

    @cached_property
    def var_medicare_part_b_premium_costs_list(self) -> list:
        """Variable Medicare Part B premium costs.
        Uses low volatility (std = 10% of mean) and clamps to non-negative.
        Returns zeros for months before Medicare eligibility or when toggle is off.
        """
        return [
            max(0.0, round(np.random.normal(x, x * 0.1), 2))
            for x in self.base_scenario.medicare_part_b_premium_costs
        ]

    @cached_property
    def var_medicare_part_d_premium_costs_list(self) -> list:
        """Variable Medicare Part D premium costs.
        Uses low volatility (std = 10% of mean) and clamps to non-negative.
        Returns zeros for months before Medicare eligibility or when toggle is off.
        """
        return [
            max(0.0, round(np.random.normal(x, x * 0.1), 2))
            for x in self.base_scenario.medicare_part_d_premium_costs
        ]

    @cached_property
    def var_private_insurance_costs_list(self) -> list:
        """Variable pre-Medicare private insurance (ACA) costs.
        Uses low volatility (std = 10% of mean) and clamps to non-negative.
        Returns zeros when not applicable or when toggle is off.
        """
        return [
            max(0.0, round(np.random.normal(x, x * 0.1), 2))
            for x in self.base_scenario.private_insurance_costs
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
        variable_mkt_list = []
        for conservative_rate in self.base_scenario.conservative_yearly_mkt_interest:
            conservative_rate_pct = conservative_rate * 100
            sampled_rate_pct = np.random.normal(
                conservative_rate_pct,
                conservative_rate_pct * 1.5,
            )
            if conservative_rate_pct > MIN_CONSERVATIVE_RETIREMENT_RATE_PCT:
                sampled_rate_pct = min(sampled_rate_pct, conservative_rate_pct)
            variable_mkt_list.append(round(sampled_rate_pct / 100, 4))

        return variable_mkt_list

    @cached_property
    def var_monthly_mkt_interest(self) -> list:
        """Docstring"""
        return [
            round(((1 + x) ** (1 / 12) - 1), 4) for x in self.var_yearly_mkt_interest
        ]

    @cached_property
    def var_savings_retirement_account_list(
        self,
    ) -> tuple[
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
        list,
    ]:
        """Calculate the amount of money in your savings and retirement accounts over time,
        stopping Roth IRA contributions and withdrawing contributions (not interest) when
        savings falls below threshold. Once age >= 59.5, withdraw from full Roth IRA
        balance (including earnings) penalty-free. At RMD age, take required minimum
        distributions from Traditional 401k and direct them into savings.
        Roth IRAs and Roth 401(k)s are exempt from RMDs (SECURE Act 2.0).
        HSA funds can be withdrawn for general expenses at age 65+ (no RMDs ever).
        Brokerage funds can be withdrawn at any age (no RMDs, no penalties).
        Brokerage withdrawals are subject to capital gains tax on the gains portion.
        Pension income is added to savings unconditionally each month during retirement.

        Returns:
            tuple of (savings_list, roth_ira_balance_list,
                      roth_401k_balance_list,
                      trad_401k_balance_list, trad_401k_rmd_list,
                      roth_ira_transfer_list, roth_401k_transfer_list,
                      trad_401k_transfer_list, trad_ira_balance_list,
                      hsa_balance_list, hsa_transfer_list,
                      brokerage_balance_list, brokerage_transfer_list,
                      trad_401k_tax_list, brokerage_interest_list,
                      brokerage_income_tax_list, brokerage_tax_list,
                      pension_payment_list)
        """
        total_non_base_bills_list = (
            [sum(sublist) for sublist in zip(*self.base_scenario.non_base_bills_lists)]
            if self.base_scenario.non_base_bills_lists
            else [0.0] * self.base_scenario.total_months
        )

        # Initialize account lists
        savings_list = []
        roth_ira_balance_list = []
        roth_ira_contributions_list = []
        roth_401k_balance_list = []
        trad_401k_balance_list = []
        trad_ira_balance_list = []
        hsa_balance_list = []
        brokerage_balance_list = []
        trad_401k_rmd_list = []
        roth_ira_transfer_list = []
        roth_401k_transfer_list = []
        trad_401k_transfer_list = []
        hsa_transfer_list = []
        brokerage_transfer_list = []
        trad_401k_tax_list = []
        brokerage_interest_list = []
        brokerage_income_tax_list = []
        brokerage_tax_list = []
        pension_payment_list = []

        # Track Roth IRA contributions separately from growth
        roth_ira_contributions = 0.0
        brokerage_cost_basis = 0.0

        # Get Roth IRA account if it exists. Assume only one Roth IRA for simplicity.
        roth_ira = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementRothIRA):
                roth_ira = ret_account
                break

        # Get Roth 401k account if it exists. Assume only one Roth 401k for simplicity.
        roth_401k = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementRoth401k):
                roth_401k = ret_account
                break

        # Get Traditional 401k account if it exists. Assume only one for simplicity.
        trad_401k = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementTrad401k):
                trad_401k = ret_account
                break

        # Get Traditional IRA account if it exists. Assume only one for simplicity.
        trad_ira = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementTradIRA):
                trad_ira = ret_account
                break

        # Get HSA account if it exists. Assume only one for simplicity.
        hsa = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementHSA):
                hsa = ret_account
                break

        # Get Brokerage account if it exists. Assume only one for simplicity.
        brokerage = None
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementBrokerage):
                brokerage = ret_account
                break

        # Get Pension accounts (multiple pensions allowed).
        pension_accounts = [
            ret_account
            for ret_account in self.base_scenario.retirement_list
            if isinstance(ret_account, RetirementPension)
        ]

        for i in range(self.base_scenario.total_months):
            roth_ira_transfer = 0.0
            roth_401k_transfer = 0.0
            trad_401k_transfer = 0.0
            hsa_transfer = 0.0
            brokerage_transfer = 0.0
            trad_401k_tax = 0.0
            brokerage_tax = 0.0
            brokerage_interest = 0.0
            brokerage_income_tax = 0.0

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
                roth_401k_bal = (
                    float(round(roth_401k.base_retirement, 6)) if roth_401k else 0.0
                )
                trad_401k_bal = (
                    float(round(trad_401k.base_retirement, 6)) if trad_401k else 0.0
                )
                trad_ira_bal = (
                    float(round(trad_ira.base_retirement, 6)) if trad_ira else 0.0
                )
                hsa_bal = float(round(hsa.base_retirement, 6)) if hsa else 0.0
                brokerage_bal = (
                    float(round(brokerage.base_retirement, 6)) if brokerage else 0.0
                )
                brokerage_cost_basis = brokerage_bal

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
                            - self.var_healthcare_costs_list[i]
                            - self.var_medicare_part_b_premium_costs_list[i]
                            - self.var_medicare_part_d_premium_costs_list[i]
                            - self.var_private_insurance_costs_list[i]
                            - self.var_medical_bills_list[i]
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
                    roth_ira_transfer += withdrawal

                # If still below threshold, withdraw from brokerage (no age restriction)
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if still_below and brokerage and brokerage_bal > 0:
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, brokerage_bal)
                    savings += withdrawal
                    brokerage_bal -= withdrawal
                    brokerage_transfer += withdrawal

                # If still below threshold and age >= 59.5, withdraw from full Roth IRA balance
                age_yrs = self.base_scenario.age_by_year_list[i]
                age_mos = self.base_scenario.age_by_month_list[i]
                can_withdraw_earnings = age_yrs > ROTH_IRA_WITHDRAWAL_AGE_YRS or (
                    age_yrs == ROTH_IRA_WITHDRAWAL_AGE_YRS
                    and age_mos >= ROTH_IRA_WITHDRAWAL_AGE_MOS
                )
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and roth_ira
                    and roth_ira_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, roth_ira_bal)
                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions = max(0, roth_ira_contributions - withdrawal)
                    roth_ira_transfer += withdrawal

                # If still below threshold and age >= 59.5, withdraw from Roth 401k
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and roth_401k
                    and roth_401k_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, roth_401k_bal)
                    savings += withdrawal
                    roth_401k_bal -= withdrawal
                    roth_401k_transfer += withdrawal

                # If still below threshold and age >= 59.5, withdraw from Traditional 401k
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and trad_401k
                    and trad_401k_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    gross_needed = shortfall / (1 - TRAD_401K_TAX_RATE)
                    withdrawal = min(gross_needed, trad_401k_bal)
                    tax = withdrawal * TRAD_401K_TAX_RATE
                    trad_401k_tax += tax
                    savings += withdrawal - tax
                    trad_401k_bal -= withdrawal
                    trad_401k_transfer += withdrawal - tax

                # If still below threshold and age >= 65, withdraw from HSA for general expenses
                age_yrs = self.base_scenario.age_by_year_list[i]
                can_withdraw_hsa = age_yrs >= HSA_WITHDRAWAL_AGE_YRS
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if still_below and can_withdraw_hsa and hsa and hsa_bal > 0:
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, hsa_bal)
                    savings += withdrawal
                    hsa_bal -= withdrawal
                    hsa_transfer += withdrawal

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

                # Grow Roth 401k with interest and contributions pre-retirement
                if roth_401k:
                    contribution_401k = roth_401k.retirement_increase_list[i]
                    roth_401k_bal = float(
                        round(
                            (roth_401k_bal + contribution_401k)
                            * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Traditional 401k with interest and contributions pre-retirement
                if trad_401k:
                    contribution_trad_401k = trad_401k.retirement_increase_list[i]
                    trad_401k_bal = float(
                        round(
                            (trad_401k_bal + contribution_trad_401k)
                            * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Traditional IRA with interest and contributions pre-retirement
                if trad_ira:
                    contribution_trad_ira = trad_ira.retirement_increase_list[i]
                    trad_ira_bal = float(
                        round(
                            (trad_ira_bal + contribution_trad_ira)
                            * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow HSA with interest and contributions pre-retirement
                if hsa:
                    contribution_hsa = hsa.retirement_increase_list[i]
                    hsa_bal = float(
                        round(
                            (hsa_bal + contribution_hsa)
                            * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Brokerage with interest and contributions pre-retirement
                if brokerage:
                    contribution_brokerage = brokerage.retirement_increase_list[i]
                    brokerage_cost_basis += contribution_brokerage
                    pre_growth_bal = brokerage_bal + contribution_brokerage
                    interest_earned = pre_growth_bal * self.var_monthly_mkt_interest[i]
                    brokerage_interest = interest_earned
                    brokerage_bal = float(
                        round(
                            pre_growth_bal + interest_earned,
                            6,
                        )
                    )

            else:  # If you are retired
                # Add pension income to savings before paying expenses
                pension_income = sum(
                    p.pension_payment_list[i] for p in pension_accounts
                )

                # Pay expenses from savings
                savings = float(
                    round(
                        (
                            savings
                            + pension_income
                            - (
                                self.var_base_bills_list[i]
                                + self.var_post_retire_extra_bills_list[i]
                                + total_non_base_bills_list[i]
                                + self.var_healthcare_costs_list[i]
                                + self.var_medicare_part_b_premium_costs_list[i]
                                + self.var_medicare_part_d_premium_costs_list[i]
                                + self.var_private_insurance_costs_list[i]
                                + self.var_medical_bills_list[i]
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
                    roth_ira_transfer += withdrawal

                # If still below threshold, withdraw from brokerage (no age restriction)
                # Capital gains tax applies to the gains portion of the withdrawal
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if still_below and brokerage and brokerage_bal > 0:
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    gain_ratio = max(
                        0, (brokerage_bal - brokerage_cost_basis) / brokerage_bal
                    )
                    effective_tax_rate = gain_ratio * BROKERAGE_TAX_RATE
                    gross_needed = (
                        shortfall / (1 - effective_tax_rate)
                        if effective_tax_rate < 1
                        else shortfall
                    )
                    withdrawal = min(gross_needed, brokerage_bal)
                    tax = withdrawal * gain_ratio * BROKERAGE_TAX_RATE
                    basis_ratio = brokerage_cost_basis / brokerage_bal
                    brokerage_cost_basis -= withdrawal * basis_ratio
                    brokerage_bal -= withdrawal
                    savings += withdrawal - tax
                    brokerage_transfer += withdrawal - tax
                    brokerage_tax += tax

                # If still below threshold and age >= 59.5, withdraw from full Roth IRA balance
                age_yrs = self.base_scenario.age_by_year_list[i]
                age_mos = self.base_scenario.age_by_month_list[i]
                can_withdraw_earnings = age_yrs > ROTH_IRA_WITHDRAWAL_AGE_YRS or (
                    age_yrs == ROTH_IRA_WITHDRAWAL_AGE_YRS
                    and age_mos >= ROTH_IRA_WITHDRAWAL_AGE_MOS
                )
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and roth_ira
                    and roth_ira_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, roth_ira_bal)
                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions = max(0, roth_ira_contributions - withdrawal)
                    roth_ira_transfer += withdrawal

                # If still below threshold and age >= 59.5, withdraw from Roth 401k
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and roth_401k
                    and roth_401k_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, roth_401k_bal)
                    savings += withdrawal
                    roth_401k_bal -= withdrawal
                    roth_401k_transfer += withdrawal

                # If still below threshold and age >= 59.5, withdraw from Traditional 401k
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if (
                    still_below
                    and can_withdraw_earnings
                    and trad_401k
                    and trad_401k_bal > 0
                ):
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    gross_needed = shortfall / (1 - TRAD_401K_TAX_RATE)
                    withdrawal = min(gross_needed, trad_401k_bal)
                    tax = withdrawal * TRAD_401K_TAX_RATE
                    trad_401k_tax += tax
                    savings += withdrawal - tax
                    trad_401k_bal -= withdrawal
                    trad_401k_transfer += withdrawal - tax

                # If still below threshold and age >= 65, withdraw from HSA for general expenses
                can_withdraw_hsa = age_yrs >= HSA_WITHDRAWAL_AGE_YRS
                still_below = (
                    savings <= self.base_scenario.monthly_savings_threshold_list[i]
                )
                if still_below and can_withdraw_hsa and hsa and hsa_bal > 0:
                    shortfall = (
                        self.base_scenario.monthly_savings_threshold_list[i] - savings
                    )
                    withdrawal = min(shortfall, hsa_bal)
                    savings += withdrawal
                    hsa_bal -= withdrawal
                    hsa_transfer += withdrawal

                # Grow Roth IRA (no contributions in retirement)
                if roth_ira:
                    roth_ira_bal = float(
                        round(
                            roth_ira_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Roth 401k (no contributions in retirement)
                if roth_401k:
                    roth_401k_bal = float(
                        round(
                            roth_401k_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Traditional 401k (no contributions in retirement)
                if trad_401k:
                    trad_401k_bal = float(
                        round(
                            trad_401k_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Traditional IRA (no contributions in retirement)
                if trad_ira:
                    trad_ira_bal = float(
                        round(
                            trad_ira_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow HSA (no contributions in retirement)
                if hsa:
                    hsa_bal = float(
                        round(
                            hsa_bal * (1 + self.var_monthly_mkt_interest[i]),
                            6,
                        )
                    )

                # Grow Brokerage (no contributions in retirement)
                if brokerage:
                    interest_earned = brokerage_bal * self.var_monthly_mkt_interest[i]
                    brokerage_interest = interest_earned
                    brokerage_bal = float(
                        round(
                            brokerage_bal + interest_earned,
                            6,
                        )
                    )

            # RMD for Traditional 401k: If at or past RMD age, take required minimum distribution
            trad_401k_rmd_amount = 0.0
            if trad_401k and trad_401k_bal > 0:
                age_yrs_rmd = self.base_scenario.age_by_year_list[i]
                age_mos_rmd = self.base_scenario.age_by_month_list[i]
                at_rmd_age = age_yrs_rmd > trad_401k.rmd_age_yrs or (
                    age_yrs_rmd == trad_401k.rmd_age_yrs
                    and age_mos_rmd >= trad_401k.rmd_age_mos
                )
                if at_rmd_age and age_yrs_rmd in uniform_lifetime_table:
                    distribution_period = uniform_lifetime_table[age_yrs_rmd]
                    annual_rmd = trad_401k_bal / distribution_period
                    monthly_rmd = annual_rmd / 12
                    trad_401k_rmd_amount = min(monthly_rmd, trad_401k_bal)
                    tax = trad_401k_rmd_amount * TRAD_401K_TAX_RATE
                    trad_401k_tax += tax
                    savings += trad_401k_rmd_amount - tax
                    trad_401k_bal -= trad_401k_rmd_amount
                    trad_401k_transfer += trad_401k_rmd_amount - tax

            # Append current balances to lists
            savings_list.append(savings)
            roth_ira_balance_list.append(roth_ira_bal)
            roth_ira_contributions_list.append(roth_ira_contributions)
            roth_401k_balance_list.append(roth_401k_bal if roth_401k else 0.0)
            trad_401k_balance_list.append(trad_401k_bal if trad_401k else 0.0)
            trad_ira_balance_list.append(trad_ira_bal if trad_ira else 0.0)
            hsa_balance_list.append(hsa_bal if hsa else 0.0)
            brokerage_balance_list.append(brokerage_bal if brokerage else 0.0)
            trad_401k_rmd_list.append(trad_401k_rmd_amount)
            roth_ira_transfer_list.append(roth_ira_transfer)
            roth_401k_transfer_list.append(roth_401k_transfer)
            trad_401k_transfer_list.append(trad_401k_transfer)
            hsa_transfer_list.append(hsa_transfer)
            brokerage_transfer_list.append(brokerage_transfer)
            trad_401k_tax_list.append(trad_401k_tax)
            brokerage_tax_list.append(brokerage_tax)
            brokerage_interest_list.append(round(brokerage_interest, 6))
            brokerage_income_tax_list.append(brokerage_income_tax)
            pension_payment_list.append(
                sum(p.pension_payment_list[i] for p in pension_accounts)
            )

        return (
            savings_list,
            roth_ira_balance_list,
            roth_401k_balance_list,
            trad_401k_balance_list,
            trad_401k_rmd_list,
            roth_ira_transfer_list,
            roth_401k_transfer_list,
            trad_401k_transfer_list,
            trad_ira_balance_list,
            hsa_balance_list,
            hsa_transfer_list,
            brokerage_balance_list,
            brokerage_transfer_list,
            trad_401k_tax_list,
            brokerage_interest_list,
            brokerage_income_tax_list,
            brokerage_tax_list,
            pension_payment_list,
        )

    def create_full_df(self) -> pd.DataFrame:
        """Create full dataframe with base and variable scenarios"""
        var_data = {
            "count": self.base_scenario.count_list,
            "var_yearly_rf_interest": self.var_yearly_rf_interest,
            "var_monthly_rf_interest": self.var_monthly_rf_interest,
            "var_base_bills": self.var_base_bills_list,
            "var_retire_extra": self.var_post_retire_extra_bills_list,
            "var_savings_increase": self.var_savings_increase_list,
            "var_medical_bills_cost": self.var_medical_bills_list,
            "var_healthcare_cost": self.var_healthcare_costs_list,
            "var_medicare_part_b_premium": self.var_medicare_part_b_premium_costs_list,
            "var_medicare_part_d_premium": self.var_medicare_part_d_premium_costs_list,
            "var_private_insurance_cost": self.var_private_insurance_costs_list,
            "var_savings_account": self.var_savings_retirement_account_list[0],
            "var_trad_401k_rmd": self.var_savings_retirement_account_list[4],
            "var_roth_ira_transfer": self.var_savings_retirement_account_list[5],
            "var_roth_401k_transfer": self.var_savings_retirement_account_list[6],
            "var_traditional_401k_transfer": self.var_savings_retirement_account_list[
                7
            ],
            "var_hsa_transfer": self.var_savings_retirement_account_list[10],
            "var_brokerage_transfer": self.var_savings_retirement_account_list[12],
            "var_trad_401k_tax": self.var_savings_retirement_account_list[13],
            "var_brokerage_interest": self.var_savings_retirement_account_list[14],
            "var_brokerage_income_tax": self.var_savings_retirement_account_list[15],
            "var_brokerage_tax": self.var_savings_retirement_account_list[16],
            "var_yearly_mkt_interest": self.var_yearly_mkt_interest,
            "var_monthly_mkt_interest": self.var_monthly_mkt_interest,
        }
        for ret_account in self.base_scenario.retirement_list:
            if isinstance(ret_account, RetirementRothIRA):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[1]
                )
            elif isinstance(ret_account, RetirementRoth401k):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[2]
                )
            elif isinstance(ret_account, RetirementTrad401k):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[3]
                )
            elif isinstance(ret_account, RetirementTradIRA):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[8]
                )
            elif isinstance(ret_account, RetirementHSA):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[9]
                )
            elif isinstance(ret_account, RetirementBrokerage):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[11]
                )
            elif isinstance(ret_account, RetirementPension):
                var_data[f"var_{ret_account.name}"] = (
                    self.var_savings_retirement_account_list[17]
                )

        var_df = pd.DataFrame(var_data)
        return self.base_scenario.create_base_df().merge(var_df, on="count", how="left")
