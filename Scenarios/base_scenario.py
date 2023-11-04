import pandas as pd

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from dataclasses import dataclass
from functools import cached_property


def calc_date_on_age(birthdate: date, age_yrs: int, age_mos: int) -> datetime.date:
    """Calculates a date based on a birthdate and a given age in years and months"""
    if birthdate.month + age_mos <= 12:
        month = birthdate.month + age_mos
        spill_over = 0
    else:
        month = birthdate.month + age_mos - 12
        spill_over = 1

    year = birthdate.year + age_yrs + spill_over
    return date(year, month, 1)


def calc_months_list(end_date: datetime.date) -> list:
    current_date = date.today()
    start_month = current_date.replace(day=1)
    delta = relativedelta(end_date, start_month)
    months_between = (delta.years * 12) + delta.months

    months_list = []

    for _ in range(months_between + 1):
        months_list.append(start_month)
        start_month = start_month + timedelta(days=31)
        start_month = start_month.replace(day=1)
    return months_list


@dataclass
class BaseScenario:
    assumptions: dict

    @cached_property
    def death_years(self) -> int:
        """The age you are when you die"""
        return 110

    @property
    def birthdate(self) -> datetime.date:
        """Calculate birthdate"""
        return datetime.strptime(self.assumptions["birthday"], "%m/%d/%Y").date()

    @property
    def deathdate(self) -> date:
        return calc_date_on_age(self.birthdate, self.death_years, 0)

    def create_initial_df(self) -> pd.DataFrame:
        """Create month count and month dataframe"""
        months_list = calc_months_list(self.deathdate)
        return pd.DataFrame(
            {"months": [i for i in range(len(months_list))], "month": months_list}
        )
