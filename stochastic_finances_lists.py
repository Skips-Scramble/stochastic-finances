import findspark

findspark.init()

import json
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, DateType

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

from variable_inputs.savings import calc_base_added_savings
from utils.tools import make_as_df, make_type_schemas


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


# def make_as_df(
#     spark: SparkSession,
#     number_of_scenarios: int,
#     columns: list,
#     tot_months: int,
#     *col_names: str
# ) -> DataFrame:
#     for col in columns:
#         assert len(col) == tot_months

#     cols_transposed = list(map(list, zip(*columns)))
#     # schema_rand_savings = [
#     #     StructField("rand_savings", FloatType(), True) for _ in range(number_of_scenarios)
#     # ]
#     schema_list = [
#         StructField("month", DateType(), True),
#         StructField("age_yrs", IntegerType(), True),
#         StructField("age_mos", IntegerType(), True),
#         StructField("savings", FloatType(), True),
#     ]
#     # for x in schema_rand_savings:
#     #     schema_list.append(x)
#     schema = StructType(schema_list)
#     output_df = spark.createDataFrame(cols_transposed, schema)
#     return output_df


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    # final_month = calc_final_month(birthdate)
    final_month = datetime(2023, 12, 1)

    months_list = calc_months(birthdate, final_month)
    tot_months = len(months_list)
    age_yrs_list = calc_age_yrs(months_list, birthdate)
    age_mos_list = calc_age_mos(months_list, birthdate)
    interest_list = calc_monthly_interest(assumptions, tot_months)
    savings_list = calc_savings(assumptions, interest_list)
    (
        var_interest_yrly_list,
        var_interest_monthly_list,
        var_added_savings_list,
        var_savings_list,
    ) = calc_base_added_savings(assumptions, tot_months)

    data = [months_list, age_yrs_list]
    data_transposed = list(map(list, zip(*data)))
    cols = StructType(
        [
            StructField("month", DateType(), False),
            StructField("age_yrs", IntegerType(), False),
        ]
    )

    df = spark.createDataFrame(data_transposed, cols)

    datetype_schemas = make_type_schemas(["months"], [months_list], DateType())
    inttype_schemas = make_type_schemas(
        ["age_yrs", "age_mos"], [age_yrs_list, age_mos_list], IntegerType()
    )
    floattype_schemas = make_type_schemas(
        [
            "interest",
            "savings",
            "var_interest_yrly",
            "var_interest_monthly",
            "var_added_savings",
            "var_savings_list",
        ],
        [
            interest_list,
            savings_list,
            var_interest_yrly_list,
            var_interest_monthly_list,
            var_added_savings_list,
            var_savings_list,
        ],
        FloatType(),
    )

    all_schemas = StructType(datetype_schemas + inttype_schemas + floattype_schemas)
    all_columns = [
        months_list,
        age_yrs_list,
        age_mos_list,
        interest_list,
        savings_list,
        var_interest_yrly_list,
        var_interest_monthly_list,
        var_added_savings_list,
        var_savings_list,
    ]

    df = make_as_df(spark, all_columns, all_schemas)
