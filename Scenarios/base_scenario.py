from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import cached_property

import pandas as pd
from dateutil.relativedelta import relativedelta

DEATH_YEARS = 110


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


def calc_payment_item_dates(
    birthdate: datetime.date,
    pmt_start_age_yrs: int,
    pmt_start_age_mos: int,
    pmt_length_yrs: int,
) -> (datetime.date, datetime.date):
    """Docstring"""
    item_pmt_start_date = calc_date_on_age(
        birthdate,
        pmt_start_age_yrs,
        pmt_start_age_mos,
    )

    item_pmt_end_yr = item_pmt_start_date.year + pmt_length_yrs
    if item_pmt_start_date.month - 1 != 0:
        item_pmt_end_mo = item_pmt_start_date.month - 1
    else:
        item_pmt_end_mo = 12

    return item_pmt_start_date, date(item_pmt_end_yr, item_pmt_end_mo, 1)


def calc_item_monthly_pmt_list(
    months_list: list,
    item_pmt_start_date: datetime.date,
    item_pmt_end_date: datetime.date,
    item_down_pmt: int,
    item_monthly_pmt: float,
):
    """Docstring"""
    item_pmt_list = []
    for month in months_list:
        if month >= item_pmt_start_date and month <= item_pmt_end_date:
            if month == item_pmt_start_date:
                item_pmt_list.append(round(item_monthly_pmt, 2) + item_down_pmt)
            else:
                item_pmt_list.append(round(item_monthly_pmt, 2))
        else:
            item_pmt_list.append(round(0, 2))

    return item_pmt_list


@dataclass
class BaseScenario:
    assumptions: dict

    @cached_property
    def start_date(self) -> date:
        """Create start month"""
        return date.today().replace(day=1)

    @cached_property
    def birthdate(self) -> date:
        """Calculate birthdate"""
        if isinstance(self.assumptions["birthday"], date):
            return self.assumptions["birthday"]
        return datetime.strptime(self.assumptions["birthday"], "%m/%d/%Y").date()

    @cached_property
    def death_date(self) -> date:
        return calc_date_on_age(self.birthdate, DEATH_YEARS, 0)

    @cached_property
    def retirement_date(self) -> date:
        # return date(2024, 12, 1)
        return calc_date_on_age(
            self.birthdate,
            int(self.assumptions["retirement_age_yrs"]),
            int(self.assumptions["retirement_age_mos"]),
        )

    @cached_property
    def total_months(self) -> int:
        return (
            relativedelta(self.death_date, self.start_date).years * 12
            - relativedelta(self.death_date, self.start_date).months
        )

    @cached_property
    def count_list(self) -> list:
        """List of 1,2,3,... for each month"""
        return [i for i in range(self.total_months)]

    @cached_property
    def month_list(self) -> list:
        """List of each month used"""
        return [
            self.start_date + relativedelta(months=i) for i in range(self.total_months)
        ]

    @cached_property
    def pre_retire_month_count_list(self) -> list:
        """List of 1,2,3,... for each month pre-retirement"""
        pre_retire_months_cnt_list = []
        for index, _ in enumerate(self.month_list):
            if self.month_list[index] <= self.retirement_date:
                pre_retire_months_cnt_list.append(index)
            else:
                pre_retire_months_cnt_list.append(0)
        return pre_retire_months_cnt_list

    @cached_property
    def post_retire_month_count_list(self) -> list:
        """List of 1,2,3,... for each month post-retirement"""
        post_retire_months_cnt_list = []
        for index, _ in enumerate(self.month_list):
            if self.month_list[index] <= self.retirement_date:
                post_retire_months_cnt_list.append(0)
            else:
                post_retire_months_cnt_list.append(
                    post_retire_months_cnt_list[index - 1] + 1
                )
        return post_retire_months_cnt_list

    @cached_property
    def age_by_year_list(self) -> list:
        """Calculate the person's age in years"""
        age_yrs_list = []
        for month in self.month_list:
            age_yrs = month.year - self.birthdate.year - 1

            # Check if the birthday has already occurred this year
            if month.month == self.birthdate.month:
                age_yrs += 1
            age_yrs_list.append(age_yrs)

        return age_yrs_list

    @cached_property
    def age_by_month_list(self) -> list:
        """Calculate the person's age in months"""
        return [(x.month - self.birthdate.month) % 12 for x in self.month_list]

    @cached_property
    def monthly_inflation(self) -> float:
        """Calculate the monthly inflation rate"""
        return round(
            (1 + self.assumptions["base_inflation_per_yr"] / 100) ** (1 / 12) - 1, 6
        )

    @cached_property
    def monthly_savings_threshold_list(self) -> list:
        """Calculate the minimum monthly savings threshold by month"""
        return [
            round(
                self.assumptions["savings_lower_limit"]
                * (1 + self.monthly_inflation) ** count,
                2,
            )
            for count in self.count_list
        ]

    @cached_property
    def yearly_rf_interest(self) -> float:
        """Calculate the base risk-free interest APY"""
        return round(self.assumptions["base_rf_interest_per_yr"] / 100, 6)

    @cached_property
    def monthly_rf_interest(self) -> float:
        """Caclulate the monthly risk-free interest rate"""
        return round((1 + self.yearly_rf_interest) ** (1 / 12) - 1, 6)

    @cached_property
    def savings_increase_list(self) -> list:
        """List of how much your savings will increase each month (with assumed increase factor)"""
        savings_increase_list = []
        for index, value in enumerate(self.pre_retire_month_count_list):
            if index == 0:
                savings_increase_list.append(self.assumptions["base_saved_per_mo"])
            elif value == 0:
                savings_increase_list.append(0)
            elif index % 12 == 11:
                savings_increase_list.append(
                    savings_increase_list[index - 1]
                    * round(
                        1 + self.assumptions["base_savings_per_yr_increase"] / 100,
                        3,
                    )
                )
            else:
                savings_increase_list.append(savings_increase_list[index - 1])

        return [float(round(x, 2)) for x in savings_increase_list]

    @cached_property
    def base_bills_list(self) -> list:
        """List of the base bills per month (inflation adjusted)"""
        monthly_inflation = round(
            ((1 + self.assumptions["base_inflation_per_yr"] / 100) ** (1 / 12)) - 1, 6
        )
        return [
            round(
                self.assumptions["base_monthly_bills"] * (1 + monthly_inflation) ** i, 2
            )
            for i in range(self.total_months)
        ]

    @cached_property
    def post_retire_extra_bills_list(self) -> list:
        """Calculate how much extra you will need post-retirement (for fun things)"""
        return [
            round(
                self.assumptions["retirement_extra_expenses"]
                / 12
                * (1 + self.monthly_inflation) ** count,
                2,
            )
            for count in self.count_list
        ]

    @cached_property
    def non_base_bills_lists(self) -> list:
        """Docstring"""
        non_base_bills_lists = []
        for item in self.assumptions["payment_items"]:
            item_pmt_start_date, item_pmt_end_date = calc_payment_item_dates(
                self.birthdate,
                item["pmt_start_age_yrs"],
                item["pmt_start_age_mos"],
                item["pmt_length_yrs"],
            )
            non_base_bills_lists.append(
                calc_item_monthly_pmt_list(
                    self.month_list,
                    item_pmt_start_date,
                    item_pmt_end_date,
                    item["down_pmt"],
                    item["monthly_pmt"],
                )
            )
        if non_base_bills_lists == []:
            non_base_bills_lists = [[0 for _ in range(self.total_months)]]
        return non_base_bills_lists

    @cached_property
    def yearly_mkt_interest(self) -> list:
        """Calculate yearly market interest as a percent"""
        return round(self.assumptions["base_mkt_interest_per_yr"] / 100, 6)

    @cached_property
    def monthly_mkt_interest(self) -> float:
        """Caclulate the monthly market interest rate"""
        return round((1 + self.yearly_mkt_interest) ** (1 / 12) - 1, 6)

    @cached_property
    def retirement_increase_list(self) -> list:
        """List of how much your savings will increase each month (with assumed increase factor)"""
        retirement_increase_list = []
        for index, value in enumerate(self.pre_retire_month_count_list):
            if index == 0:
                retirement_increase_list.append(
                    self.assumptions["base_retirement_per_mo"]
                )
            elif value == 0:
                retirement_increase_list.append(0)
            elif index % 12 == 11:
                retirement_increase_list.append(
                    retirement_increase_list[index - 1]
                    + round(self.assumptions["base_retirement_per_yr_increase"] / 12, 2)
                )
            else:
                retirement_increase_list.append(retirement_increase_list[index - 1])

        return [float(round(x, 2)) for x in retirement_increase_list]

    @cached_property
    def savings_retirement_account_list(self) -> [list, list]:
        """Calculate amount in your savings account by month"""
        total_non_base_bills_list = [
            sum(sublist) for sublist in zip(*self.non_base_bills_lists)
        ]
        savings_list = []
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                savings = float(round(self.assumptions["base_savings"], 2))
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                savings = float(
                    round(
                        (
                            savings
                            + self.savings_increase_list[i]
                            - total_non_base_bills_list[i]
                        )
                        * (1 + self.monthly_rf_interest),
                        2,
                    )
                )
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        2,
                    )
                )
            else:  # If you are retired
                if savings_list[i - 1] <= self.monthly_savings_threshold_list[i - 1]:
                    savings = float(
                        round(savings_list[i - 1] * (1 + self.monthly_rf_interest), 2)
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - self.base_bills_list[i]
                                - self.post_retire_extra_bills_list[i]
                                - total_non_base_bills_list[i]
                            )
                            * (1 + self.monthly_mkt_interest),
                            2,
                        )
                    )
                else:
                    savings = float(
                        round(
                            (
                                savings
                                + self.savings_increase_list[i]
                                - (self.base_bills_list[i] / 2)
                                - (self.post_retire_extra_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                            )
                            * (1 + self.monthly_rf_interest),
                            2,
                        )
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - (self.base_bills_list[i] / 2)
                                - (self.post_retire_extra_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                            )
                            * (1 + self.monthly_mkt_interest),
                            2,
                        )
                    )
            savings_list.append(savings)
            retirement_list.append(retirement)
        return savings_list, retirement_list

    def create_base_df(self) -> pd.DataFrame:
        """Create the inital dataframe without any randomness applied"""
        data_1 = {
            "count": self.count_list,
            "pre_retire_month_cnt": self.pre_retire_month_count_list,
            "post_retire_month_cnt": self.post_retire_month_count_list,
            "month": self.month_list,
            "age_yrs": self.age_by_year_list,
            "age_mos": self.age_by_month_list,
            "monthly_inflation": self.monthly_inflation,
            "min_savings_threshold": self.monthly_savings_threshold_list,
            "yearly_rf_interest": self.yearly_rf_interest,
            "monthly_rf_interest": self.monthly_rf_interest,
            "savings_increase": self.savings_increase_list,
            "base_bills": self.base_bills_list,
            "retire_extra": self.post_retire_extra_bills_list,
        }
        non_base_items_names = [
            f'{x["pmt_name"]}_pmt' for x in self.assumptions["payment_items"]
        ]
        non_base_items_lists = {
            k: v for (k, v) in zip(non_base_items_names, self.non_base_bills_lists)
        }
        data_3 = {
            "savings_account": self.savings_retirement_account_list[0],
            "yearly_mkt_interest": self.yearly_mkt_interest,
            "monthly_mkt_interest": self.monthly_mkt_interest,
            "retirement_increase": self.retirement_increase_list,
            "retirement_account": self.savings_retirement_account_list[1],
        }

        data = {**data_1, **non_base_items_lists, **data_3}

        return pd.DataFrame(data)
