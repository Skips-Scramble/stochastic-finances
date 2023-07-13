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
    monthly_interest = round(((1 + interest_rate / 100) ** (1 / 12)) - 1, 4)
    savings_list = []
    for i in range(tot_months):
        savings_list.append(round(savings * (1 + monthly_interest) ** i), 2)
    return savings_list


def calc_variable_savings(
    tot_months: int, savings: float, interest_rate: float
) -> list:
    var_interest_list = np.random.normal(interest_rate, 1, tot_months)
    var_savings_list = []
    for i in range(tot_months):
        if i == 0:
            var_savings_list.append(savings)
            prev_savings = savings
        else:
            monthly_interest = round(
                (1 + (var_interest_list[i] / 100)) ** (1 / 12) - 1, 4
            )
            # print(f'monthly_interest is {monthly_interest}')
            prev_savings = round(prev_savings * (1 + monthly_interest), 2)
            # print(f'prev_savings is {prev_savings}')
            var_savings_list.append(prev_savings)
    return var_savings_list


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    with open("input_assumptions.json") as json_data:
        assumptions = json.load(json_data)

    birthdate = datetime.strptime(assumptions["birthday"], "%m/%d/%Y").date()

    final_month = calc_final_month(birthdate)

    months_list = calc_months(birthdate, final_month)
    tot_months = len(months_list)
    age_yrs_list = calc_age_yrs(months_list, birthdate)
    age_mos_list = calc_age_mos(months_list, birthdate)
    savings_list = calc_savings(
        tot_months, assumptions["current_savings"], assumptions["mean_interest_per_yr"]
    )
    for _ in range(100):
        var_savings_master_list = []
        variable_savings_list = calc_variable_savings(
            tot_months,
            assumptions["current_savings"],
            assumptions["mean_interest_per_yr"],
        )
        var_savings_master_list.append(variable_savings_list)
