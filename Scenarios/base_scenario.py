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


def calc_months_list(start_month: date, end_month: date) -> list:
    delta = relativedelta(end_month, start_month)
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

    @cached_property
    def start_month(self) -> date:
        """Create start month"""
        return date.today().replace(day=1)

    @property
    def birthdate(self) -> date:
        """Calculate birthdate"""
        return datetime.strptime(self.assumptions["birthday"], "%m/%d/%Y").date()

    @property
    def death_month(self) -> date:
        return calc_date_on_age(self.birthdate, self.death_years, 0)

    @property
    def retirement_date(self) -> date:
        return calc_date_on_age(
            self.birthdate,
            self.assumptions["retirement_age_yrs"],
            self.assumptions["retirement_age_mos"],
        )

    def create_initial_df(self) -> pd.DataFrame:
        """Create month count and month dataframe"""
        months_list = calc_months_list(self.start_month, self.death_month)
        return pd.DataFrame(
            {"months": [i for i in range(len(months_list))], "month": months_list}
        ).assign(
            month_cnt_pre_retire=lambda df: relativedelta(
                df.month, self.start_month
            ).months
        )
