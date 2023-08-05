import findspark

findspark.init()

import json
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    IntegerType,
    FloatType,
    DateType,
)

import pandas as pd

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np

from utils.tools import make_type_schemas
from functools import cached_property


def calc_final_month(birthdate: datetime.date) -> datetime.date:
    """Go up to 120 years for thoroughness"""
    final_year = birthdate.year + 120
    final_month = birthdate.month
    final_day = 1

    return datetime(final_year, final_month, final_day)


def calc_months(final_month: datetime.date) -> list:
    current_date = date.today()
    start_month = current_date.replace(day=1)
    delta = relativedelta(final_month, start_month)
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


def calc_monthly_interest(assumptions: dict, tot_months: int) -> list:
    monthly_interest = float(
        round(((1 + assumptions["base_interest_per_yr"] / 100) ** (1 / 12)) - 1, 4)
    )
    interest_list = [monthly_interest for _ in range(tot_months)]
    return interest_list


def calc_savings(
    assumptions: dict,
    interest_list: list,
) -> list:
    """Calculate base savings"""
    savings_list = []
    for index, interest in enumerate(interest_list):
        if index == 0:
            savings = float(round(assumptions["current_savings"], 2))
            savings_list.append(savings)
        else:
            savings = float(
                round(
                    (savings + assumptions["base_saved_per_month"]) * (1 + interest), 2
                )
            )
            savings_list.append(savings)
    return savings_list


class FinancialScenario:
    def __init__(
        self,
        spark: SparkSession,
        assumptions: dict,
        birthdate: date,
        final_month: date,
        months_list: list,
        month_count_list: list,
        tot_months: int,
        age_yrs_list: list,
        age_mos_list: list,
        yrly_interest_list: list,
        monthly_interest_list: list,
        savings_list: list,
    ):
        self.spark = spark
        self.assumptions = assumptions
        self.birthdate = birthdate
        self.final_month = final_month
        self.months_list = months_list
        self.month_count_list = month_count_list
        self.tot_months = tot_months
        self.age_yrs_list = age_yrs_list
        self.age_mos_list = age_mos_list
        self.yrly_interest_list = yrly_interest_list
        self.monthly_interest_list = monthly_interest_list
        self.savings_list = savings_list

    @cached_property
    def var_interest_yrly(self) -> list:
        """Function to create list of savings when taking into account added
        savings per month and interest using variable amounts based on a
        distribution
        """
        yrly_interest_array = np.random.normal(
            self.assumptions["base_interest_per_yr"],
            self.assumptions["base_interest_per_yr"] * (1.5),
            self.tot_months,
        )
        return [round(float(x / 100), 4) for x in yrly_interest_array]

    @cached_property
    def var_interest_monthly(self) -> list:
        """Docstring"""
        return [
            round(float(((1 + x) ** (1 / 12) - 1)), 4) for x in self.var_interest_yrly
        ]

    @cached_property
    def var_added_savings(self) -> list:
        """Docstring"""
        var_savings_array = np.random.normal(
            self.assumptions["base_saved_per_month"],
            self.assumptions["base_saved_per_month"] * (0.5),
            self.tot_months,
        )
        return [round(float(x), 2) for x in var_savings_array]

    @cached_property
    def var_savings(self) -> list:
        """Docstring"""
        var_savings = []
        for i in range(self.tot_months):
            if i == 0:
                prev_savings = round(float(self.assumptions["current_savings"]), 2)
                var_savings.append(prev_savings)
            else:
                prev_savings = float(
                    round(
                        prev_savings * (1 + self.var_interest_monthly[i])
                        + self.var_added_savings[i],
                        2,
                    )
                )
                var_savings.append(prev_savings)
        return var_savings

    def create_spark_df(self) -> DataFrame:
        """Docstring"""

        all_columns = [
            self.month_count_list,
            self.months_list,
            self.age_yrs_list,
            self.age_mos_list,
            self.yrly_interest_list,
            self.monthly_interest_list,
            self.savings_list,
            self.var_interest_yrly,
            self.var_interest_monthly,
            self.var_added_savings,
            self.var_savings,
        ]

        cols_transposed = list(map(list, zip(*all_columns)))

        month_count_schemas_base = make_type_schemas(
            ["month_count"],
            [self.month_count_list],
            IntegerType(),
        )
        datetype_schemas = make_type_schemas(["month"], [self.months_list], DateType())
        inttype_schemas_base = make_type_schemas(
            ["age_yrs", "age_mos"],
            [self.age_yrs_list, self.age_mos_list],
            IntegerType(),
        )
        floattype_schemas = make_type_schemas(
            [
                "yrly_interest",
                "monthly_interest",
                "savings",
                "var_interest_yrly",
                "var_interest_monthly",
                "var_added_savings",
                "var_savings_list",
            ],
            [
                self.yrly_interest_list,
                self.monthly_interest_list,
                self.savings_list,
                self.var_interest_yrly,
                self.var_interest_monthly,
                self.var_added_savings,
                self.var_savings,
            ],
            FloatType(),
        )

        all_schemas = StructType(
            month_count_schemas_base
            + datetype_schemas
            + inttype_schemas_base
            + floattype_schemas
        )

        return self.spark.createDataFrame(cols_transposed, all_schemas)

    def create_pandas_df(self) -> pd.DataFrame:
        """Docstring"""
        data = {
            "month_count": self.month_count_list,
            "month": self.months_list,
            "age_yrs": self.age_yrs_list,
            "age_mos": self.age_mos_list,
            "yrly_interest": self.yrly_interest_list,
            "monthly_interest": self.monthly_interest_list,
            "savings": self.savings_list,
            "var_interest_yrly": self.var_interest_yrly,
            "var_interest_monthly": self.var_interest_monthly,
            "var_added_savings": self.var_added_savings,
            "var_savings_list": self.var_savings,
        }

        return pd.DataFrame(data)


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)
    # final_month = datetime(2060, 12, 1)

    months_list = calc_months(final_month)
    month_count_list = [i for i in range(len(months_list))]
    tot_months = len(months_list)
    age_yrs_list = calc_age_yrs(months_list, birthdate)
    age_mos_list = calc_age_mos(months_list, birthdate)
    yrly_interest_list = [
        float(round(assumptions["base_interest_per_yr"] / 100, 4))
        for _ in range(tot_months)
    ]
    monthly_interest_list = calc_monthly_interest(assumptions, tot_months)
    savings_list = calc_savings(assumptions, monthly_interest_list)

    first_class = FinancialScenario(
        spark,
        assumptions,
        birthdate,
        final_month,
        months_list,
        month_count_list,
        tot_months,
        age_yrs_list,
        age_mos_list,
        yrly_interest_list,
        monthly_interest_list,
        savings_list,
    )

    final_list = []
    for i in range(1000):
        new_scen = FinancialScenario(
            spark,
            assumptions,
            birthdate,
            final_month,
            months_list,
            month_count_list,
            tot_months,
            age_yrs_list,
            age_mos_list,
            yrly_interest_list,
            monthly_interest_list,
            savings_list,
        )
        new_scen.create_pandas_df().to_csv(f"./outputs/scen_{i}.csv", index=False)
        # print(f"{new_scen.var_savings[-1]:,.0f}")

        final_list.append(new_scen.var_savings[-1])

    print(f"final average: {(sum(final_list) / len(final_list)):,.0f}")
