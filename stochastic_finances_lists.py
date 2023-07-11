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


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    months_list = calc_months(birthdate, final_month)
    age_yrs_list = calc_age_yrs(months_list, birthdate)
