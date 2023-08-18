import json
import pandas as pd

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import random

from functools import cached_property


def calc_date_on_age(
    birthdate: datetime.date, age_yrs: int, age_mos: int
) -> datetime.date:
    """Calculates a date based on a birthdate and a given age in years and months"""
    if birthdate.month + age_mos <= 12:
        month = birthdate.month + age_mos
        spill_over = 0
    else:
        month = birthdate.month + age_mos - 12
        spill_over = 1

    year = birthdate.year + age_yrs + spill_over
    return date(year, month, 1)


def calc_months(end_date: datetime.date) -> list:
    current_date = date.today()
    start_month = current_date.replace(day=1)
    delta = relativedelta(end_date, start_month)
    months_between = (delta.years * 12) + delta.months

    months_list = []

    for _ in range(months_between):
        start_month = start_month + timedelta(days=31)
        start_month = start_month.replace(day=1)
        months_list.append(start_month)
    return months_list


def calc_age_yrs(months: list, birthdate: datetime.date) -> list:
    age_yrs_list = []
    for month in months:
        age_yrs = month.year - birthdate.year - 1

        # Check if the birthday has already occurred this year
        if month.month == birthdate.month:
            age_yrs += 1
        age_yrs_list.append(age_yrs)
    return age_yrs_list


def calc_age_mos(months: list, birthdate: datetime.date) -> list:
    age_mos_list = [(x.month - birthdate.month) % 12 for x in months]
    return age_mos_list


def calc_monthly_rf_interest(assumptions: dict, pre_retire_months_cnt: int) -> list:
    monthly_interest = float(
        round(((1 + assumptions["base_rf_interest_per_yr"] / 100) ** (1 / 12)) - 1, 4)
    )
    rf_interest_list = [monthly_interest for _ in range(pre_retire_months_cnt)]
    return rf_interest_list


def calc_savings_added_increase(assumptions: dict, pre_retire_months_cnt: int):
    savings_added_increase_list = []
    for i in range(pre_retire_months_cnt):
        if i == 0:
            savings_added_increase_list.append(round(0, 2))
        elif i % 12 == 0:
            savings_added_increase_list.append(
                round(
                    assumptions["base_savings_per_yr_increase"] / 100,
                    2,
                )
            )
        else:
            savings_added_increase_list.append(round(0, 2))

    return savings_added_increase_list


def calc_savings_added(assumptions: dict, savings_added_increase_list: list):
    savings_added_list = []
    for index, value in enumerate(savings_added_increase_list):
        if index == 0:
            savings_added_list.append(round(assumptions["base_saved_per_mo"], 2))
        else:
            savings_added_list.append(
                round(savings_added_list[index - 1] * (1 + value), 2)
            )

    return savings_added_list


def calc_payment_item_dates(
    birthdate: datetime.date,
    item_pmt_start_age_yrs: int,
    item_pmt_start_age_mos: int,
    item_pmt_length_yrs: int,
) -> (datetime.date, datetime.date):
    """Docstring"""
    item_pmt_start_date = calc_date_on_age(
        birthdate,
        item_pmt_start_age_yrs,
        item_pmt_start_age_mos,
    )

    item_pmt_end_yr = item_pmt_start_date.year + item_pmt_length_yrs
    if item_pmt_start_date.month - 1 != 0:
        item_pmt_end_mo = item_pmt_start_date.month - 1
    else:
        item_pmt_end_mo = 12

    return item_pmt_start_date, date(item_pmt_end_yr, item_pmt_end_mo, 1)


def calc_item_monthly_pmt_list(
    months_list: list,
    item_pmt_start_date: datetime.date,
    item_pmt_end_date: datetime.date,
    item_down_pmt: int,
    item_monthly_pmt: float,
):
    """Docstring"""
    item_pmt_list = []
    for month in months_list:
        if month >= item_pmt_start_date and month <= item_pmt_end_date:
            if month == item_pmt_start_date:
                item_pmt_list.append(round(item_monthly_pmt, 2) + item_down_pmt)
            else:
                item_pmt_list.append(round(item_monthly_pmt, 2))
        else:
            item_pmt_list.append(round(0, 2))

    return item_pmt_list


def calc_payments(
    assumptions: dict,
    birthdate: datetime.date,
    months_list: list,
) -> list:
    """Docstring"""
    payments_list = []
    for item in assumptions["payment_items"]:
        item_pmt_start_date, item_pmt_end_date = calc_payment_item_dates(
            birthdate,
            item["item_pmt_start_age_yrs"],
            item["item_pmt_start_age_mos"],
            item["item_pmt_length_yrs"],
        )
        payments_list.append(
            calc_item_monthly_pmt_list(
                months_list,
                item_pmt_start_date,
                item_pmt_end_date,
                item["item_down_pmt"],
                item["item_monthly_pmt"],
            )
        )
    return payments_list


def calc_savings(
    assumptions: dict,
    interest_list: list,
    savings_added_list: list,
    payments_list: list,
) -> list:
    """Calculate base savings"""
    tot_pmts_list = [sum(sublist) for sublist in zip(*payments_list)]
    savings_list = []
    for index, interest in enumerate(interest_list):
        if index == 0:
            savings = float(round(assumptions["current_savings"], 2))
            savings_list.append(savings)
        else:
            savings = float(
                round(
                    (savings + savings_added_list[index] - tot_pmts_list[index])
                    * (1 + interest),
                    2,
                )
            )
            savings_list.append(savings)
    return savings_list


def calc_monthly_mkt_interest(assumptions: dict, pre_retire_months_cnt: int) -> list:
    monthly_interest = float(
        round(((1 + assumptions["base_mkt_interest_per_yr"] / 100) ** (1 / 12)) - 1, 4)
    )
    mkt_interest_list = [monthly_interest for _ in range(pre_retire_months_cnt)]
    return mkt_interest_list


def calc_ret_added_increase(assumptions: dict, pre_retire_months_cnt: int):
    ret_added_increase_list = []
    for i in range(pre_retire_months_cnt):
        if i == 0:
            ret_added_increase_list.append(round(0, 2))
        elif i % 12 == 0:
            ret_added_increase_list.append(
                round(
                    assumptions["base_retirement_per_yr_increase"] / 12,
                    2,
                )
            )
        else:
            ret_added_increase_list.append(round(0, 2))

    return ret_added_increase_list


def calc_ret_added(assumptions: dict, ret_added_increase_list: list):
    ret_added_list = []
    for index, value in enumerate(ret_added_increase_list):
        if index == 0:
            ret_added_list.append(round(assumptions["base_retirement_per_mo"], 2))
        else:
            ret_added_list.append(round(ret_added_list[index - 1] + value, 2))

    return ret_added_list


def calc_retirement(
    assumptions: dict,
    mkt_intersest_list: list,
    retirement_added_list: list,
) -> list:
    """Calculate base savings"""
    retirement_list = []
    for index, interest in enumerate(mkt_intersest_list):
        if index == 0:
            retirement = float(round(assumptions["base_retirement"], 2))
            retirement_list.append(retirement)
        else:
            retirement = float(
                round(
                    (retirement + retirement_added_list[index]) * (1 + interest),
                    2,
                )
            )
            retirement_list.append(retirement)
    return retirement_list


class FinancialScenario:
    def __init__(
        self,
        assumptions: dict,
        birthdate: date,
        retirement_date: date,
        months_list: list,
        month_cnt_list: list,
        pre_retire_months_cnt: int,
        age_yrs_list: list,
        age_mos_list: list,
        yrly_rf_interest_list: list,
        monthly_rf_interest_list: list,
        savings_increase_list: list,
        savings_added_list: list,
        item_pmt_list: list,
        savings_list: list,
        yrly_mkt_interest_list: list,
        monthly_mkt_interest_list: list,
        retirement_increase_list: list,
        retirement_added_list: list,
        retirement_list: list,
    ):
        self.assumptions = assumptions
        self.birthdate = birthdate
        self.retirement_date = retirement_date
        self.months_list = months_list
        self.month_cnt_list = month_cnt_list
        self.pre_retire_months_cnt = pre_retire_months_cnt
        self.age_yrs_list = age_yrs_list
        self.age_mos_list = age_mos_list
        self.yrly_rf_interest_list = yrly_rf_interest_list
        self.monthly_rf_interest_list = monthly_rf_interest_list
        self.savings_increase_list = savings_increase_list
        self.savings_added_list = savings_added_list
        self.item_pmt_list = item_pmt_list
        self.savings_list = savings_list
        self.yrly_mkt_interest_list = yrly_mkt_interest_list
        self.monthly_mkt_interest_list = monthly_mkt_interest_list
        self.retirement_increase_list = retirement_increase_list
        self.retirement_added_list = retirement_added_list
        self.retirement_list = retirement_list

    @cached_property
    def tot_pmt_list(self):
        """Docstring"""
        return [sum(sublist) for sublist in zip(*self.item_pmt_list)]

    @cached_property
    def var_rf_interest_yrly(self) -> list:
        """Function to create list of savings when taking into account added
        savings per month and interest using variable amounts based on a
        distribution
        """
        base_list = [
            self.assumptions["base_rf_interest_per_yr"] / 100
        ] * self.pre_retire_months_cnt

        variable_rf_list = []
        for index, rate in enumerate(base_list):
            if index == 0:
                variable_rf_list.append(rate)
            elif index % self.assumptions["rf_interest_change_mos"] != 0:
                variable_rf_list.append(variable_rf_list[index - 1])
            else:
                adj_factor = random.randint(-1, 1) * 0.0015
                variable_rf_list.append(
                    min(max(0.001, variable_rf_list[index - 1] + adj_factor), 0.07)
                )

        return variable_rf_list

    @cached_property
    def var_rf_interest_monthly(self) -> list:
        """Docstring"""
        return [
            round(float(((1 + x) ** (1 / 12) - 1)), 4)
            for x in self.var_rf_interest_yrly
        ]

    @cached_property
    def var_added_savings(self) -> list:
        """Docstring"""
        return [
            round(
                np.random.normal(
                    x,
                    x * (0.5),
                ),
                2,
            )
            for x in self.savings_added_list
        ]

    @cached_property
    def var_savings(self) -> list:
        """Docstring"""
        var_savings = []
        for i in range(self.pre_retire_months_cnt):
            if i == 0:
                prev_savings = round(float(self.assumptions["current_savings"]), 2)
                var_savings.append(prev_savings)
            else:
                prev_savings = float(
                    round(
                        prev_savings * (1 + self.var_rf_interest_monthly[i])
                        + self.var_added_savings[i]
                        - self.tot_pmt_list[i],
                        2,
                    )
                )
                var_savings.append(prev_savings)
        return var_savings

    @cached_property
    def var_mkt_interest_yrly(self) -> list:
        """Docstring"""
        return [
            round(
                np.random.normal(
                    self.assumptions["base_mkt_interest_per_yr"],
                    self.assumptions["base_mkt_interest_per_yr"] * 1.5,
                )
                / 100,
                4,
            )
            for _ in range(self.pre_retire_months_cnt)
        ]

    @cached_property
    def var_mkt_interest_monthly(self) -> list:
        """Docstring"""
        return [round(((1 + x) ** (1 / 12) - 1), 4) for x in self.var_mkt_interest_yrly]

    @cached_property
    def var_retirement(self) -> list:
        """Docstring"""
        var_retirement = []
        for i in range(self.pre_retire_months_cnt):
            if i == 0:
                prev_retirement = round(self.assumptions["base_retirement"], 2)
                var_retirement.append(prev_retirement)
            else:
                prev_retirement = round(
                    prev_retirement * (1 + self.var_mkt_interest_monthly[i])
                    + self.retirement_added_list[i],
                    2,
                )
                var_retirement.append(prev_retirement)
        return var_retirement

    @cached_property
    def retirement_count_list(self) -> list:
        retirement_count_list = []
        for month in self.months_list:
            if month < self.retirement_date:
                retirement_count_list.append(0)
            else:
                retirement_count_list.append(
                    relativedelta(month, self.retirement_date).months
                )
        return retirement_count_list

    # @cached_property
    # def var_bills_monthly(self) ->list:
    #     base_bills = self.assumptions['1500']
    #     inflation = self.assumptions['base_inflation_yr']
    #     base_bills_retirement = base_bills * (1+inflation)**

    def create_pandas_df(self) -> pd.DataFrame:
        """Docstring"""
        data_1 = {
            "month_count": self.month_cnt_list,
            "month": self.months_list,
            "age_yrs": self.age_yrs_list,
            "age_mos": self.age_mos_list,
            "yrly_rf_interest": self.yrly_rf_interest_list,
            "monthly_rf_interest": self.monthly_rf_interest_list,
            "savings_increase": self.savings_increase_list,
            "savings_added": self.savings_added_list,
        }

        pmt_item_names = [
            f'{x["item_name"]}_pmt' for x in self.assumptions["payment_items"]
        ]
        pmt_items = {k: v for (k, v) in zip(pmt_item_names, self.item_pmt_list)}

        data_3 = {
            "savings": self.savings_list,
            "yrly_mkt_interst": self.yrly_mkt_interest_list,
            "monthly_mkt_interst": self.monthly_mkt_interest_list,
            "retirement_increase": self.retirement_increase_list,
            "retirement_added": self.retirement_added_list,
            "retirement": self.retirement_list,
            "var_rf_interest_yrly": self.var_rf_interest_yrly,
            "var_rf_interest_monthly": self.var_rf_interest_monthly,
            "var_added_savings": self.var_added_savings,
            "var_savings": self.var_savings,
            "var_mkt_interest_yrly": self.var_mkt_interest_yrly,
            "var_mkt_interest_monthly": self.var_mkt_interest_monthly,
            "var_retirement": self.var_retirement,
        }

        data = {**data_1, **pmt_items, **data_3}

        return pd.DataFrame(data)


def main() -> None:
    # spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()
    deathdate = calc_date_on_age(birthdate, 110, 0)

    retirement_date = calc_date_on_age(
        birthdate,
        assumptions["retirement_age_yrs"],
        assumptions["retirement_age_mos"],
    )
    # retirement_date = datetime(2026, 12, 1)

    months_list = calc_months(deathdate)
    month_cnt_list = [i for i in range(len(months_list))]

    pre_retire_month_cnt_list = []
    for i in month_cnt_list:
        if months_list[i] <= retirement_date:
            pre_retire_month_cnt_list.append(i)
        else:
            pre_retire_month_cnt_list.append(0)

    pre_retire_months_cnt = len(months_list)

    age_yrs_list = calc_age_yrs(months_list, birthdate)
    age_mos_list = calc_age_mos(months_list, birthdate)
    yrly_rf_interest_list = [
        float(round(assumptions["base_rf_interest_per_yr"] / 100, 4))
        for _ in range(pre_retire_months_cnt)
    ]
    monthly_rf_interest_list = calc_monthly_rf_interest(
        assumptions, pre_retire_months_cnt
    )
    savings_increase_list = calc_savings_added_increase(
        assumptions, pre_retire_months_cnt
    )
    savings_added_list = calc_savings_added(assumptions, savings_increase_list)
    payments_list = calc_payments(assumptions, birthdate, months_list)
    savings_list = calc_savings(
        assumptions, monthly_rf_interest_list, savings_added_list, payments_list
    )
    yrly_mkt_interest_list = [
        round(assumptions["base_mkt_interest_per_yr"] / 100, 4)
        for _ in range(pre_retire_months_cnt)
    ]
    monthly_mkt_interest_list = calc_monthly_mkt_interest(
        assumptions, pre_retire_months_cnt
    )
    retirement_increase_list = calc_ret_added_increase(
        assumptions, pre_retire_months_cnt
    )
    retirement_added_list = calc_ret_added(assumptions, retirement_increase_list)
    retirement_list = calc_retirement(
        assumptions, monthly_mkt_interest_list, retirement_added_list
    )

    final_savings_list = []
    final_retirement_list = []
    for i in range(1000):
        new_scen = FinancialScenario(
            assumptions,
            birthdate,
            retirement_date,
            months_list,
            month_cnt_list,
            pre_retire_months_cnt,
            age_yrs_list,
            age_mos_list,
            yrly_rf_interest_list,
            monthly_rf_interest_list,
            savings_increase_list,
            savings_added_list,
            payments_list,
            savings_list,
            yrly_mkt_interest_list,
            monthly_mkt_interest_list,
            retirement_increase_list,
            retirement_added_list,
            retirement_list,
        )
        new_scen.create_pandas_df().to_csv(f"./outputs/scen_{i}.csv", index=False)
        # print(f"{new_scen.var_savings[-1]:,.0f}")

        final_savings_list.append(new_scen.var_savings[-1])
        final_retirement_list.append(new_scen.var_retirement[-1])

    print(
        f"final average savings: {(sum(final_savings_list) / len(final_savings_list)):,.0f}"
    )
    print(
        f"final average retirement: {(sum(final_retirement_list) / len(final_retirement_list)):,.0f}"
    )
