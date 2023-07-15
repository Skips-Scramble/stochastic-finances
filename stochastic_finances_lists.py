import findspark

findspark.init()

import json
from pyspark.sql import SparkSession, DataFrame

import pyspark.sql.functions as spark_funcs

from pyspark.sql.types import (
    DateType,
    StructType,
    StructField,
    FloatType,
    StringType,
    IntegerType,
)
from pyspark.sql.window import Window
from pyspark.sql import SQLContext
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import typing


def calc_final_month(birthdate: datetime.date) -> datetime.date:
    """Go up to 120 years for thoroughness"""
    final_year = birthdate.year + 120
    final_month = birthdate.month
    final_day = 1

    return datetime(final_year, final_month, final_day)


def calc_months(birthdate: datetime.date, final_month: datetime.date) -> list:
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


def calc_savings(tot_months: int, savings: float, interest_rate: float) -> list:
    monthly_interest = float(round(((1 + interest_rate / 100) ** (1 / 12)) - 1, 4))
    savings_list = []
    for i in range(tot_months):
        savings_list.append(float(round(savings * (1 + monthly_interest) ** i, 2)))
    return savings_list


def calc_variable_savings(
    tot_months: int, savings: float, interest_rate: float
) -> list:
    var_interest_list = np.random.normal(interest_rate, 1, tot_months)
    var_savings_list = []
    for i in range(tot_months):
        if i == 0:
            var_savings_list.append(round(float(savings), 2))
            prev_savings = round(float(savings), 2)
        else:
            monthly_interest = float(
                round((1 + (var_interest_list[i] / 100)) ** (1 / 12) - 1, 4)
            )
            # print(f'monthly_interest is {monthly_interest}')
            prev_savings = float(round(prev_savings * (1 + monthly_interest), 2))
            # print(f'prev_savings is {prev_savings}')
            var_savings_list.append(prev_savings)
    return var_savings_list


def make_as_df(
    spark: SparkSession, number_of_scenarios: int, columns: list, tot_months: int, *col_names: str
) -> DataFrame:
    for col in columns:
        assert len(col) == tot_months

    cols_transposed = list(map(list, zip(*columns)))
    schema_rand_savings = [
        StructField("rand_savings", FloatType(), True) for _ in range(number_of_scenarios)
    ]
    schema_list = [
        StructField("month", DateType(), True),
        StructField("age_yrs", IntegerType(), True),
        StructField("age_mos", IntegerType(), True),
        StructField("savings", FloatType(), True),
    ]
    for x in schema_rand_savings:
        schema_list.append(x)
    schema = StructType(schema_list)
    output_df = spark.createDataFrame(cols_transposed, schema)
    return output_df


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)
    # final_month = datetime(2023, 10, 1)

    months_list = calc_months(birthdate, final_month)
    tot_months = len(months_list)
    age_yrs_list = calc_age_yrs(months_list, birthdate)
    age_mos_list = calc_age_mos(months_list, birthdate)
    savings_list = calc_savings(
        tot_months, assumptions["current_savings"], assumptions["mean_interest_per_yr"]
    )

    all_columns = [months_list, age_yrs_list, age_mos_list, savings_list]

    var_savings_master_list = []

    number_of_scenarios = assumptions['number_of_scenarios']

    for i in range(number_of_scenarios):
        variable_savings_list = calc_variable_savings(
            tot_months,
            assumptions["current_savings"],
            assumptions["mean_interest_per_yr"],
        )
        var_savings_master_list.append(variable_savings_list)
        all_columns.append(var_savings_master_list[i])

    savings_to_df = make_as_df(
        spark,
        number_of_scenarios,
        all_columns,
        tot_months,
        "month",
        "age_yrs",
        "age_mos",
        "savings",
        *", ".join("rand_savings" for _ in range(number_of_scenarios)).split(" ")
    )
