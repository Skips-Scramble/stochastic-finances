from datetime import date, datetime, timedelta
import json
from pyspark.sql import SparkSession

import numpy_financial as npf


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


def main():
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    current_age_yrs, current_age_mos = calculate_current_age(birthdate)
