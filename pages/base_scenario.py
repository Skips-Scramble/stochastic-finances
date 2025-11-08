from dataclasses import dataclass
from datetime import date, datetime
from functools import cached_property

import pandas as pd
from dateutil.relativedelta import relativedelta

DEATH_YEARS = 115
HEALTHCARE_BINS = [0, 19, 45, 65, 85, float("inf")]
HEALTHCARE_LABELS = ["0-18", "19-44", "45-64", "65-84", "85+"]
uniform_lifetime_table = {
    72: 27.4,
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
    86: 15.2,
    87: 14.4,
    88: 13.7,
    89: 12.9,
    90: 12.2,
    91: 11.5,
    92: 10.8,
    93: 10.1,
    94: 9.5,
    95: 8.9,
    96: 8.4,
    97: 7.8,
    98: 7.3,
    99: 6.8,
    100: 6.4,
    101: 6.0,
    102: 5.6,
    103: 5.2,
    104: 4.9,
    105: 4.6,
    106: 4.3,
    107: 4.1,
    108: 3.9,
    109: 3.7,
    110: 3.5,
    111: 3.4,
    112: 3.3,
    113: 3.1,
    114: 3.0,
    115: 2.9,
    116: 2.8,
    117: 2.7,
    118: 2.5,
    119: 2.3,
    120: 2.0,
}


def calc_date_on_age(birthdate: date, age_yrs: int, age_mos: int) -> date:
    """Calculates a date based on a birthdate and a given age in years and months"""
    months_add = age_yrs * 12 + age_mos
    return (birthdate + relativedelta(months=months_add)).replace(day=1)


def calc_pmt_list(
    birthdate: date,
    months_list: list,
    pmt_start_age_yrs: int,
    pmt_start_age_mos: int,
    pmt_length_yrs: int,
    pmt_length_mos: int,
    item_down_pmt: int,
    reg_pmt_amt: float,
    pmt_freq_mos: int,
    inflation_rate: float,
) -> list:
    """Calculate list of payment amounts"""

    pmt_start_date = calc_date_on_age(
        birthdate,
        pmt_start_age_yrs,
        pmt_start_age_mos,
    )

    pmt_end_date = pmt_start_date + relativedelta(
        months=(pmt_length_yrs * 12 + pmt_length_mos - 1)
    )

    item_pmt_list = []
    print(f"pmt_start_date = {pmt_start_date}")
    print(f"Today: {datetime.today().month}")
    months_until_start = (pmt_start_date.year - datetime.today().year) * 12 + (
        pmt_start_date.month - datetime.today().month
    )
    print(f"{months_until_start=}")
    print(f"{inflation_rate=}")

    # If the payment has already started
    if months_until_start <= 0:
        initial_down_pmt: float = 0.0
        initial_reg_pmt_amt = reg_pmt_amt
        months_until_start = 0
    # If the payment will be in the future
    else:
        initial_down_pmt = round(
            item_down_pmt * (1 + inflation_rate) ** months_until_start, 2
        )
        initial_reg_pmt_amt = round(
            reg_pmt_amt * (1 + inflation_rate) ** months_until_start, 2
        )
    for index, month in enumerate(months_list):
        if pmt_start_date <= month <= pmt_end_date:
            if month == pmt_start_date:
                months_until_start = index
                item_pmt_list.append(round(initial_down_pmt + initial_reg_pmt_amt, 2))
            elif (index - months_until_start) % pmt_freq_mos == 0:
                item_pmt_list.append(
                    round(
                        initial_reg_pmt_amt
                        * (1 + inflation_rate) ** (index - months_until_start),
                        2,
                    )
                )
            else:
                item_pmt_list.append(round(0, 2))
        else:
            item_pmt_list.append(round(0, 2))

    return item_pmt_list


def ss_fra(birthdate: date) -> tuple:
    """
    Calculate the full retirement age (FRA) based on the birthdate.

    Args:
        birthdate (date): The birthdate of the individual.

    Returns:
        tuple: A tuple containing the full retirement age in years and months.
    """
    # Define the full retirement age based on birth year
    if birthdate.year < 1938:
        ss_fra_yrs = 65
        ss_fra_mos = 0
    elif 1938 <= birthdate.year < 1955:
        ss_fra_yrs = 66
        ss_fra_mos = 0
    elif 1955 <= birthdate.year < 1960:
        ss_fra_yrs = 66
        ss_fra_mos = (birthdate.year - 1954) * 2
    else:
        ss_fra_yrs = 67
        ss_fra_mos = 0

    return ss_fra_yrs, ss_fra_mos


@dataclass
class ScenarioCoreInfo:
    """Basic information for future calculations"""

    assumptions: dict

    @cached_property
    def start_date(self) -> date:
        """Create start month"""
        return date.today().replace(day=1)

    @cached_property
    def birthdate(self) -> date:
        """Calculate birthdate"""
        if isinstance(self.assumptions["birthdate"], date):
            return self.assumptions["birthdate"]
        return datetime.strptime(self.assumptions["birthdate"], "%m/%d/%Y").date()

    @cached_property
    def death_date(self) -> date:
        """Calculate death date"""
        return calc_date_on_age(self.birthdate, DEATH_YEARS, 0)

    @cached_property
    def monthly_inflation(self) -> float:
        """Calculate the monthly inflation rate"""
        return round(
            (1 + self.assumptions["base_inflation_per_yr"] / 100) ** (1 / 12) - 1, 6
        )

    @cached_property
    def yearly_mkt_interest(self) -> float:
        """Calculate yearly market interest as a percent"""
        return round(self.assumptions["base_mkt_interest_per_yr"] / 100, 6)

    @cached_property
    def monthly_mkt_interest(self) -> float:
        """Caclulate the monthly market interest rate"""
        return round((1 + self.yearly_mkt_interest) ** (1 / 12) - 1, 6)

    @cached_property
    def retirement_date(self) -> date:
        """Calculate retirement date"""
        # return date(2024, 12, 1)
        return calc_date_on_age(
            self.birthdate,
            int(self.assumptions["retirement_age_yrs"]),
            int(self.assumptions["retirement_age_mos"]),
        )

    @cached_property
    def total_months(self) -> int:
        """Calculate total months from start to death"""
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
    def months_until_retirement(self) -> int:
        """Calculate number of months from start date until retirement date"""
        return (self.retirement_date.year - self.start_date.year) * 12 + (
            self.retirement_date.month - self.start_date.month
        )

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


@dataclass
class Payment(ScenarioCoreInfo):
    """Payment item info"""

    pmt_name: str
    pmt_start_age_yrs: int
    pmt_start_age_mos: int
    pmt_length_yrs: int
    pmt_length_mos: int
    down_pmt: float
    reg_pmt_amt: float
    pmt_freq_mos: int
    recurring_purchase: bool
    recurring_timeframe: int
    recurring_length: int

    @cached_property
    def calc_pmt_list(self) -> list:
        """Calculate list of payment amounts"""

        pmt_start_date = calc_date_on_age(
            self.birthdate,
            self.pmt_start_age_yrs,
            self.pmt_start_age_mos,
        )

        pmt_end_date = pmt_start_date + relativedelta(
            months=(self.pmt_length_yrs * 12 + self.pmt_length_mos - 1)
        )

        item_pmt_list = []
        print(f"pmt_start_date = {pmt_start_date}")
        print(f"Today: {datetime.today().month}")
        months_until_start = (pmt_start_date.year - datetime.today().year) * 12 + (
            pmt_start_date.month - datetime.today().month
        )
        print(f"{months_until_start=}")
        print(f"{self.monthly_inflation=}")

        # If the payment has already started
        if months_until_start <= 0:
            initial_down_pmt: float = 0.0
            initial_reg_pmt_amt = self.reg_pmt_amt
            months_until_start = 0
        # If the payment will be in the future
        else:
            initial_down_pmt = round(
                self.down_pmt * (1 + self.monthly_inflation) ** months_until_start, 2
            )
            initial_reg_pmt_amt = round(
                self.reg_pmt_amt * (1 + self.monthly_inflation) ** months_until_start, 2
            )
        for index, month in enumerate(self.month_list):
            if pmt_start_date <= month <= pmt_end_date:
                if month == pmt_start_date:
                    months_until_start = index
                    item_pmt_list.append(
                        round(initial_down_pmt + initial_reg_pmt_amt, 2)
                    )
                elif (index - months_until_start) % self.pmt_freq_mos == 0:
                    item_pmt_list.append(
                        round(
                            initial_reg_pmt_amt
                            * (1 + self.monthly_inflation)
                            ** (index - months_until_start),
                            2,
                        )
                    )
                else:
                    item_pmt_list.append(round(0, 2))
            else:
                item_pmt_list.append(round(0, 2))

        return item_pmt_list


@dataclass
class RetirementTrad401k(ScenarioCoreInfo):
    """401k Retirement Account Info"""

    base_retirement: float
    base_retirement_per_mo: float
    base_retirement_per_yr_increase: float
    rmd_age_mos = 0

    @cached_property
    def rmd_age_yrs(self) -> int:
        """Calculate RMD age based on birthdate"""
        if self.birthdate.year <= 1950:
            return 72
        if 1951 <= self.birthdate.year <= 1959:
            return 73
        return 75

    @cached_property
    def retirement_increase_list(self) -> list:
        """List of how much your retirement will increase each month (with assumed increase factor)"""
        retirement_increase_list = []
        for index, value in enumerate(self.pre_retire_month_count_list):
            if index == 0:  # First month
                retirement_increase_list.append(
                    self.assumptions["base_retirement_per_mo"]
                )
            elif value == 0:  # Past your retirement date
                retirement_increase_list.append(0)
            elif index % 12 == 11:  # At the end of the year
                retirement_increase_list.append(
                    retirement_increase_list[index - 1]
                    + round(self.assumptions["base_retirement_per_yr_increase"] / 12, 6)
                )
            else:  # Middle of the year
                retirement_increase_list.append(retirement_increase_list[index - 1])

        return [float(round(x, 6)) for x in retirement_increase_list]

    @cached_property
    def retirement_account_list(self) -> list:
        """Calculate amount in your retirement account by month"""
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        6,
                    )
                )
            else:
                retirement = float(round((1 + self.monthly_mkt_interest), 6))

            retirement_list.append(retirement)

        return retirement_list


@dataclass
class RetirementRoth401k(ScenarioCoreInfo):
    """Roth 401k Retirement Account Info"""

    base_retirement: float
    base_retirement_per_mo: float
    base_retirement_per_yr_increase: float

    @cached_property
    def retirement_increase_list(self) -> list:
        """List of how much your retirement will increase each month (with assumed increase factor)"""
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
                    + round(self.assumptions["base_retirement_per_yr_increase"] / 12, 6)
                )
            else:
                retirement_increase_list.append(retirement_increase_list[index - 1])

        return [float(round(x, 6)) for x in retirement_increase_list]

    @cached_property
    def retirement_account_list(self) -> list:
        """Calculate amount in your retirement account by month"""
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        6,
                    )
                )
            else:
                retirement = float(round((1 + self.monthly_mkt_interest), 6))

            retirement_list.append(retirement)

        return retirement_list


@dataclass
class RetirementTradIRA(ScenarioCoreInfo):
    """Traditional IRA Retirement Account Info"""

    base_retirement: float
    base_retirement_per_mo: float
    base_retirement_per_yr_increase: float

    @cached_property
    def retirement_increase_list(self) -> list:
        """List of how much your retirement will increase each month (with assumed increase factor)"""
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
                    + round(self.assumptions["base_retirement_per_yr_increase"] / 12, 6)
                )
            else:
                retirement_increase_list.append(retirement_increase_list[index - 1])

        return [float(round(x, 6)) for x in retirement_increase_list]

    @cached_property
    def retirement_account_list(self) -> list:
        """Calculate amount in your retirement account by month"""
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        6,
                    )
                )
            else:
                retirement = float(round((1 + self.monthly_mkt_interest), 6))

            retirement_list.append(retirement)

        return retirement_list


@dataclass
class RetirementRothIRA(ScenarioCoreInfo):
    """Roth IRA Retirement Account Info"""

    base_retirement: float
    base_retirement_per_mo: float
    base_retirement_per_yr_increase: float

    @cached_property
    def retirement_increase_list(self) -> list:
        """List of how much your retirement will increase each month (with assumed increase factor)"""
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
                    + round(self.assumptions["base_retirement_per_yr_increase"] / 12, 6)
                )
            else:
                retirement_increase_list.append(retirement_increase_list[index - 1])

        return [float(round(x, 6)) for x in retirement_increase_list]

    @cached_property
    def retirement_account_list(self) -> list:
        """Calculate amount in your retirement account by month"""
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        6,
                    )
                )
            else:
                retirement = float(round((1 + self.monthly_mkt_interest), 6))

            retirement_list.append(retirement)

        return retirement_list


@dataclass
class BaseScenario(ScenarioCoreInfo):
    """Calculate a base scenario"""

    assumptions: dict

    @cached_property
    def age_by_year_list(self) -> list:
        """Calculate the person's age in years"""

        return [(month.year - self.birthdate.year) for month in self.month_list]

    @cached_property
    def age_by_month_list(self) -> list:
        """Calculate the person's age in months"""
        return [(x.month - self.birthdate.month) % 12 for x in self.month_list]

    @cached_property
    def yearly_mkt_interest(self) -> float:
        """Calculate yearly market interest as a percent"""
        return round(self.assumptions["base_mkt_interest_per_yr"] / 100, 6)

    @cached_property
    def monthly_mkt_interest(self) -> float:
        """Caclulate the monthly market interest rate"""
        return round((1 + self.yearly_mkt_interest) ** (1 / 12) - 1, 6)

    @cached_property
    def yearly_rf_interest(self) -> float:
        """Calculate the base risk-free interest APY"""
        return round(self.assumptions["base_rf_interest_per_yr"] / 100, 6)

    @cached_property
    def monthly_rf_interest(self) -> float:
        """Caclulate the monthly risk-free interest rate"""
        return round((1 + self.yearly_rf_interest) ** (1 / 12) - 1, 6)

    @cached_property
    def monthly_savings_threshold_list(self) -> list:
        # Do we hold off on this for now?
        """Calculate the minimum monthly savings threshold by month"""
        return [
            round(
                self.assumptions["savings_lower_limit"]
                * (1 + self.monthly_inflation) ** count,
                6,
            )
            for count in self.count_list
        ]

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
                        6,
                    )
                )
            else:
                savings_increase_list.append(savings_increase_list[index - 1])

        return [float(round(x, 6)) for x in savings_increase_list]

    @cached_property
    def base_bills_list(self) -> list:
        """List of the base bills per month (inflation adjusted)"""
        monthly_inflation = round(
            ((1 + self.assumptions["base_inflation_per_yr"] / 100) ** (1 / 12)) - 1, 6
        )
        return [
            round(
                self.assumptions["base_monthly_bills"] * (1 + monthly_inflation) ** i, 6
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
                6,
            )
            for count in self.count_list
        ]

    @cached_property
    def payments_list(self) -> list[Payment]:
        """List of Payment objects based on assumptions"""
        payments_list = []
        for item in self.assumptions["payment_items"]:
            payments_list.append(
                Payment(
                    assumptions=self.assumptions,
                    pmt_name=item["pmt_name"],
                    pmt_start_age_yrs=item["pmt_start_age_yrs"],
                    pmt_start_age_mos=item["pmt_start_age_mos"],
                    pmt_length_yrs=item["pmt_length_yrs"],
                    pmt_length_mos=item["pmt_length_mos"],
                    down_pmt=item["down_pmt"],
                    reg_pmt_amt=item["reg_pmt_amt"],
                    pmt_freq_mos=item["pmt_freq_mos"],
                    recurring_purchase=item["recurring_purchase"],
                    recurring_timeframe=item["recurring_timeframe"],
                    recurring_length=item["recurring_length"],
                )
            )
        return payments_list

    @cached_property
    def non_base_bills_lists(self) -> list[list]:
        """Return payments for each month"""
        non_base_bills_lists = []
        for item in self.payments_list:
            non_base_bills_lists.append(item.calc_pmt_list)

        return non_base_bills_lists

    @cached_property
    def retirement_list(
        self,
    ) -> list[
        RetirementTrad401k | RetirementRoth401k | RetirementTradIRA | RetirementRothIRA
    ]:
        # Don't know if this will be used
        """List of Retirement objects"""
        retirement_list: list[
            RetirementTrad401k
            | RetirementRoth401k
            | RetirementTradIRA
            | RetirementRothIRA
        ] = []
        for item in self.assumptions["retirement_accounts"]:
            if item["retirement_type"] == "traditional_401k":
                retirement_list.append(
                    RetirementTrad401k(
                        assumptions=self.assumptions,
                        base_retirement=item["base_retirement"],
                        base_retirement_per_mo=item["base_retirement_per_mo"],
                        base_retirement_per_yr_increase=item[
                            "base_retirement_per_yr_increase"
                        ],
                    )
                )
            elif item["retirement_type"] == "roth_401k":
                retirement_list.append(
                    RetirementRoth401k(
                        assumptions=self.assumptions,
                        base_retirement=item["base_retirement"],
                        base_retirement_per_mo=item["base_retirement_per_mo"],
                        base_retirement_per_yr_increase=item[
                            "base_retirement_per_yr_increase"
                        ],
                    )
                )
            elif item["retirement_type"] == "traditional_ira":
                retirement_list.append(
                    RetirementTradIRA(
                        assumptions=self.assumptions,
                        base_retirement=item["base_retirement"],
                        base_retirement_per_mo=item["base_retirement_per_mo"],
                        base_retirement_per_yr_increase=item[
                            "base_retirement_per_yr_increase"
                        ],
                    )
                )
            else:
                retirement_list.append(
                    RetirementRothIRA(
                        assumptions=self.assumptions,
                        base_retirement=item["base_retirement"],
                        base_retirement_per_mo=item["base_retirement_per_mo"],
                        base_retirement_per_yr_increase=item[
                            "base_retirement_per_yr_increase"
                        ],
                    )
                )
        return retirement_list

    @cached_property
    def healthcare_costs(self) -> list:
        """Add in health care costs (if chosen)"""
        if self.assumptions["add_healthcare"]:
            starting_df = pd.DataFrame(
                {"age_yrs": self.age_by_year_list, "month": self.month_list}
            ).assign(
                age_band=lambda df: pd.cut(
                    df["age_yrs"],
                    bins=HEALTHCARE_BINS,
                    labels=HEALTHCARE_LABELS,
                    right=False,
                ).astype("string")
            )

            healthcare_inputs_df = pd.read_csv(
                r"./research/healthcare/healthcare_inputs.csv"
            ).assign(
                month=lambda df: pd.to_datetime(df["month"]).dt.date,
                age_band=lambda df: df["age_band"].astype("string"),
            )

            healthcare_df = starting_df.merge(
                healthcare_inputs_df, on=["age_band", "month"], how="left"
            )

            healthcare_total_list: list[float] = []
            for index, month in enumerate(self.month_list):
                if month < healthcare_df["month"][index]:
                    healthcare_total_list.append(0.0)
                else:
                    healthcare_total_list.append(
                        float(round(healthcare_df["healthcare_cost"][index], 2))
                    )

            return healthcare_total_list

        return [0.0] * self.total_months

    @cached_property
    def savings_retirement_account_list_real(self) -> tuple[list, list]:
        """Calculate the amount of money in your savings and retirement accounts over time
        
        When savings falls below threshold:
        - Stop making Roth IRA contributions
        - Withdraw Roth IRA contributions (not interest) to cover shortfall
        - Allow savings to go negative if Roth IRA contributions are depleted
        
        Returns:
            tuple: (savings_list, roth_ira_list)
        """
        total_non_base_bills_list = [
            sum(sublist) for sublist in zip(*self.non_base_bills_lists)
        ]
        
        # Initialize account lists
        savings_list = []
        roth_ira_list = []
        
        # Track Roth IRA contributions separately from growth
        roth_ira_contributions = 0.0
        
        # Get Roth IRA account if it exists
        roth_ira = None
        for ret_account in self.retirement_list:
            if isinstance(ret_account, RetirementRothIRA):
                roth_ira = ret_account
                break
        
        for i in range(self.total_months):
            if i == 0:
                # Initialize accounts
                savings = float(round(self.assumptions["base_savings"], 6))
                roth_ira_bal = float(round(roth_ira.base_retirement, 6)) if roth_ira else 0.0
                # Starting balance counts as contributions
                roth_ira_contributions = roth_ira_bal
                
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                # Calculate expenses
                total_expenses = (
                    total_non_base_bills_list[i]
                    + self.healthcare_costs[i]
                )
                
                # Check if we're below threshold
                below_threshold = savings <= self.monthly_savings_threshold_list[i]
                
                # Update savings (pay expenses from savings)
                savings = float(
                    round(
                        (
                            savings
                            + self.savings_increase_list[i]
                            - total_expenses
                        )
                        * (1 + self.monthly_rf_interest),
                        6,
                    )
                )
                
                # If below threshold, pull from Roth IRA contributions
                if below_threshold and savings < 0 and roth_ira and roth_ira_contributions > 0:
                    # Calculate how much we need to cover the shortfall
                    shortfall = abs(savings)
                    withdrawal = min(shortfall, roth_ira_contributions)
                    
                    # Update balances
                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions -= withdrawal
                
                # Grow Roth IRA with interest (and contributions if above threshold)
                if roth_ira:
                    if below_threshold:
                        # Below threshold: no new contributions, just grow existing balance
                        roth_ira_bal = float(
                            round(
                                roth_ira_bal * (1 + self.monthly_mkt_interest),
                                6,
                            )
                        )
                    else:
                        # Above threshold: add contributions and grow
                        contribution = roth_ira.retirement_increase_list[i]
                        roth_ira_bal = float(
                            round(
                                (roth_ira_bal + contribution)
                                * (1 + self.monthly_mkt_interest),
                                6,
                            )
                        )
                        # Track the contribution amount (before growth)
                        roth_ira_contributions += contribution
                
            else:  # If you are retired
                # Calculate total expenses for the month
                total_expenses = (
                    self.base_bills_list[i]
                    + self.post_retire_extra_bills_list[i]
                    + total_non_base_bills_list[i]
                    + self.healthcare_costs[i]
                )
                
                # Pay expenses from savings
                savings = float(
                    round(
                        (savings - total_expenses) * (1 + self.monthly_rf_interest),
                        6,
                    )
                )
                
                # If below threshold and savings is negative, pull from Roth IRA contributions
                below_threshold = savings_list[i - 1] <= self.monthly_savings_threshold_list[i - 1]
                if below_threshold and savings < 0 and roth_ira and roth_ira_contributions > 0:
                    shortfall = abs(savings)
                    withdrawal = min(shortfall, roth_ira_contributions)
                    
                    savings += withdrawal
                    roth_ira_bal -= withdrawal
                    roth_ira_contributions -= withdrawal
                
                # Grow Roth IRA (no contributions in retirement)
                if roth_ira:
                    roth_ira_bal = float(
                        round(
                            roth_ira_bal * (1 + self.monthly_mkt_interest),
                            6,
                        )
                    )
            
            # Append current balances to lists
            savings_list.append(savings)
            roth_ira_list.append(roth_ira_bal)
        
        return savings_list, roth_ira_list

    @cached_property
    def savings_retirement_account_list(self) -> tuple[list, list]:
        """Calculate amount in your savings account by month"""
        total_non_base_bills_list = [
            sum(sublist) for sublist in zip(*self.non_base_bills_lists)
        ]
        savings_list = []
        retirement_list = []
        for i in range(self.total_months):
            if i == 0:
                savings = float(round(self.assumptions["base_savings"], 6))
                retirement = float(round(self.assumptions["base_retirement"], 2))
            elif self.pre_retire_month_count_list[i] != 0:  # If you're not retired
                savings = float(
                    round(
                        (
                            savings
                            + self.savings_increase_list[i]
                            - total_non_base_bills_list[i]
                            - self.healthcare_costs[i]
                        )
                        * (1 + self.monthly_rf_interest),
                        6,
                    )
                )
                retirement = float(
                    round(
                        (retirement + self.retirement_increase_list[i])
                        * (1 + self.monthly_mkt_interest),
                        6,
                    )
                )
            else:  # If you are retired
                # If you are below your savings threshold, use all retirement
                if (
                    savings_list[i - 1]
                    <= self.monthly_savings_threshold_list[i - 1]
                ):
                    savings = float(
                        round(
                            savings_list[i - 1] * (1 + self.monthly_rf_interest), 6
                        )
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - self.base_bills_list[i]
                                - self.post_retire_extra_bills_list[i]
                                - total_non_base_bills_list[i]
                                - self.healthcare_costs[i]
                            )
                            * (1 + self.monthly_mkt_interest),
                            6,
                        )
                    )
                # If you are within your savings threshold, use savings and retirement equally
                else:
                    savings = float(
                        round(
                            (
                                savings
                                + self.savings_increase_list[i]
                                - (self.base_bills_list[i] / 2)
                                - (self.post_retire_extra_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                                - (self.healthcare_costs[i] / 2)
                            )
                            * (1 + self.monthly_rf_interest),
                            6,
                        )
                    )
                    retirement = float(
                        round(
                            (
                                retirement
                                - (self.base_bills_list[i] / 2)
                                - (self.post_retire_extra_bills_list[i] / 2)
                                - (total_non_base_bills_list[i] / 2)
                                - (self.healthcare_costs[i] / 2)
                            )
                            * (1 + self.monthly_mkt_interest),
                            6,
                        )
                    )
            savings_list.append(savings)
            retirement_list.append(retirement)
        return savings_list, retirement_list

    @cached_property
    def ss_amt_by_date(self) -> list[float]:
        """
        Calculate the Social Security amount by date.
        """
        if not self.assumptions["ss_incl"]:
            return [0.0] * self.total_months

        retirement_date = calc_date_on_age(
            self.birthdate,
            self.assumptions["retirement_age_yrs"],
            self.assumptions["retirement_age_mos"],
        )

        return [
            (
                self.assumptions["ss_amt_per_mo"]
                * (1 + self.assumptions["base_inflation_per_yr"] / 100) ** (index / 12)
                if month >= retirement_date
                else 0.0
            )
            for index, month in enumerate(self.month_list)
        ]

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
            f"pmt_{i}" for i in range(len(self.non_base_bills_lists))
        ]
        non_base_items_lists = {
            k: v for (k, v) in zip(non_base_items_names, self.non_base_bills_lists)
        }
        data_3 = {
            "healthcare_cost": self.healthcare_costs,
            "savings_account": self.savings_retirement_account_list[0],
            "yearly_mkt_interest": self.yearly_mkt_interest,
            "monthly_mkt_interest": self.monthly_mkt_interest,
            "retirement_increase": self.retirement_increase_list,
            "retirement_account": self.savings_retirement_account_list[1],
        }

        data = {**data_1, **non_base_items_lists, **data_3}

        return pd.DataFrame(data).rename(
            columns={
                f"pmt_{i}": v["pmt_name"]
                for i, v in enumerate(self.assumptions["payment_items"])
            }
        )
