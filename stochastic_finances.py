import findspark

findspark.init()

import json
from pyspark.sql import SparkSession, DataFrame

import numpy_financial as npf
import pyspark.sql.functions as spark_funcs

from pyspark.sql.types import DateType, StructType, StructField, IntegerType
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import typing


def calc_age_yrs(
    birthdate: datetime.date, base_date: datetime.date
) -> typing.Tuple[int, int]:
    """Calculate how old a person is in yrs and months based on birthdate"""
    age_yrs = base_date.year - birthdate.year

    # Check if the birthday has already occurred this year
    if base_date.month < birthdate.month or (
        base_date.month == birthdate.month and base_date.day < birthdate.day
    ):
        age_yrs -= 1

    return age_yrs


def calc_age_mos(birthdate: datetime.date, base_date: datetime.date) -> int:
    age_mos = (base_date.month - birthdate.month) % 12

    # if base_date.day < birthdate.day:
    #     age_mos -= 1

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
    delta = relativedelta(start_month, final_month)
    months_between = ((delta.years * 12) + delta.months) * -1

    months_list = []

    for i in range(months_between):
        next_month = start_month + timedelta(days=31 * i)
        first_day_next_month = next_month.replace(day=1)
        months_list.append(first_day_next_month)

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


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    initial_df = create_initial_df(spark, birthdate, final_month)
    initial_w_age = add_age(initial_df)