import findspark
findspark.init()

import json
from pyspark.sql import SparkSession

import numpy_financial as npf
import pyspark.sql.functions as spark_funcs

from pyspark.sql.types import DateType, StructType, StructField, TimestampType
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta






def calculate_current_age(birthdate):
    """Calculate how old a person is in yrs and months based on birthdate"""
    today = date.today()
    current_age_yrs = today.year - birthdate.year

    # Check if the birthday has already occurred this year
    if today.month < birthdate.month or (
        today.month == birthdate.month and today.day < birthdate.day
    ):
        current_age_yrs -= 1

    current_age_mos = (today.month - birthdate.month) % 12

    if today.day < birthdate.day:
        current_age_mos -= 1

    return current_age_yrs, current_age_mos


def calc_final_month(birthdate):
    """Go up to 120 years for thoroughness"""
    final_year = birthdate.year + 120
    final_month = birthdate.month
    final_day = 1

    return datetime(final_year, final_month, final_day)


def create_initial_df(spark, final_month):
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

    return month_df


def main():
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    initial_df = create_initial_df(spark, final_month)

    current_age_yrs, current_age_mos = calculate_current_age(birthdate)
