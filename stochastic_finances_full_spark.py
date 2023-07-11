import findspark

findspark.init()

import json
from pyspark.sql import SparkSession, DataFrame

import pyspark.sql.functions as spark_funcs

from pyspark.sql.types import DateType, StructType, StructField, FloatType
from pyspark.sql.window import Window
from pyspark.sql import SQLContext
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import typing


def calc_age_yrs(
    birthdate: datetime.date, base_date: datetime.date
) -> typing.Tuple[int, int]:
    """Calculate how old a person is in yrs and months based on birthdate"""
    age_yrs = base_date.year - birthdate.year - 1

    # Check if the birthday has already occurred this year
    if base_date.month == birthdate.month:
        age_yrs += 1

    return age_yrs


def calc_age_mos(birthdate: datetime.date, base_date: datetime.date) -> int:
    age_mos = (base_date.month - birthdate.month) % 12

    return age_mos


def calc_final_month(birthdate: datetime.date) -> datetime.date:
    """Go up to 120 years for thoroughness"""
    final_year = birthdate.year + 120
    final_month = birthdate.month
    final_day = 1

    return datetime(final_year, final_month, final_day)


def create_initial_df(
    spark: SparkSession, birthdate: datetime.date, final_month: datetime.date
) -> DataFrame:
    """Create an initial df with just birthdate and month columns"""
    current_date = date.today()
    start_month = current_date.replace(day=1)
    delta = relativedelta(final_month, start_month)
    months_between = (delta.years * 12) + delta.months

    months_list = []

    for _ in range(months_between):
        start_month = start_month + timedelta(days=31)
        start_month = start_month.replace(day=1)
        months_list.append(start_month)

    schema = StructType([StructField("month", DateType(), nullable=False)])

    month_df = spark.createDataFrame([(x,) for x in months_list], schema)
    month_w_bday_df = month_df.withColumn(
        "birthdate", spark_funcs.lit(birthdate).cast(DateType())
    )

    return month_w_bday_df


def add_age(initial_df: DataFrame) -> DataFrame:
    calc_age_yrs_udf = spark_funcs.udf(calc_age_yrs)
    calc_age_mos_udf = spark_funcs.udf(calc_age_mos)

    age_df = initial_df.withColumn(
        "age_yrs", calc_age_yrs_udf("birthdate", "month")
    ).withColumn("age_mos", calc_age_mos_udf("birthdate", "month"))

    return age_df


def count_months(df_w_months: DataFrame) -> DataFrame:
    w = Window().orderBy(spark_funcs.lit("A"))
    count_months_df = df_w_months.withColumn(
        "month_count", spark_funcs.row_number().over(w) - 1
    )

    return count_months_df


def add_interest(initial_w_age: DataFrame, assumed_yrly_interest: float) -> DataFrame:
    initial_w_interest = initial_w_age.withColumn(
        "interest_rate",
        spark_funcs.round(
            spark_funcs.lit(((1 + (assumed_yrly_interest / 100)) ** (1 / 12)) - 1), 6
        ),
    )
    return initial_w_interest


def add_savings(initial_w_count: DataFrame, initial_savings: float) -> DataFrame:
    """Add a column with a savings amount for each month based on an initial amount and assumed interest rate"""
    initial_w_savings = initial_w_count.withColumn(
        "savings",
        spark_funcs.format_number(
            spark_funcs.round(
                initial_savings
                * (1 + spark_funcs.col("interest_rate"))
                ** spark_funcs.col("month_count"),
                2,
            ),
            2,
        ),
    )
    return initial_w_savings


def add_random_interest(
    spark: SparkSession,
    initial_w_savings: DataFrame,
    mean: float,
    initial_savings: float,
) -> DataFrame:
    """Calculate interest rate based on a normal distribution"""
    w_random_interest = initial_w_savings.withColumn(
        "rand_interest",
        spark_funcs.round(
            ((1 + ((mean + mean * spark_funcs.randn()) / 100)) ** (1 / 12)) - 1, 6
        ),
    )

    rand_interest_list = [row["rand_interest"] for row in w_random_interest.collect()]

    savings_rand_interest = []
    for index, interest_val in enumerate(rand_interest_list):
        if index == 0:
            savings_rand_interest.append(initial_savings)
        else:
            savings_rand_interest.append(
                round(savings_rand_interest[index - 1] * (1 + interest_val), 2)
            )

    schema = StructType(
        [StructField("savings_rand_interest", FloatType(), nullable=False)]
    )

    savings_rand_interst_df = spark.createDataFrame(
        [(float(l),) for l in savings_rand_interest], schema
    )

    w = Window().orderBy(spark_funcs.lit("A"))
    savings_rand_interst_count_df = savings_rand_interst_df.withColumn(
        "month_count", spark_funcs.row_number().over(w) - 1
    )

    w_random_savings = w_random_interest.join(
        savings_rand_interst_count_df.select(
            spark_funcs.col("month_count"),
            spark_funcs.format_number(
                spark_funcs.col("savings_rand_interest"), 2
            ).alias("savings_rand_interest"),
        ),
        on="month_count",
        how="left",
    )

    return w_random_savings


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    initial_df = create_initial_df(spark, birthdate, final_month)
    initial_w_age = add_age(initial_df)

    initial_w_count = count_months(initial_w_age)

    initial_w_interest_rate = add_interest(
        initial_w_count, assumptions["mean_interest_per_yr"]
    )

    initial_w_savings = add_savings(
        initial_w_interest_rate, assumptions["current_savings"]
    )

    initial_w_variable_interest = add_random_interest(
        spark,
        initial_w_savings,
        assumptions["mean_interest_per_yr"],
        assumptions["current_savings"],
    )
