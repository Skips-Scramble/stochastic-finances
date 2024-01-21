import typing
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentItems(BaseModel):
    pmt_name: str = Field(..., max_length=100, examples=["Car", "Mortgage"])
    pmt_start_age_yrs: int = Field(..., ge=0, le=110, examples=[65])
    pmt_start_age_mos: int = Field(..., ge=0, le=11, examples=[6])
    pmt_length_yrs: int = Field(..., ge=0, le=110, examples=[5])
    pmt_length_mos: int = Field(..., ge=0, le=11, examples=[6])
    down_pmt: int = Field(..., ge=-10_000_000_000, le=10_000_000_000, examples=[11_111])
    monthly_pmt: int = Field(..., ge=-10_000_000, le=10_000_000, examples=([777]))


class Inputs(BaseModel):
    birthdate: date = Field(
        ..., gt=date(1850, 1, 1), lt=date.today(), examples=[date(1990, 1, 1)]
    )
    retirement_age_yrs: int = Field(..., ge=0, le=110, examples=[65])
    retirement_age_mos: int = Field(..., ge=0, le=11, examples=[4])
    base_savings: int = Field(
        ..., ge=-10_000_000_000, le=10_000_000_000, examples=[100_000]
    )
    base_saved_per_mo: int = Field(..., ge=-10_000_000, le=10_000_000, examples=[100])
    base_savings_per_yr_increase: Decimal = Field(
        ..., max_digits=5, decimal_places=1, examples=[3.5]
    )
    savings_lower_limit: int = Field(
        ..., ge=-10_000_000, le=10_000_000, examples=[10_000]
    )
    base_monthly_bills: int = Field(
        ..., ge=-10_000_000, le=10_000_000, examples=[1_000]
    )
    payment_items: list[PaymentItems] | None = []
    base_retirement: int = Field(
        ..., ge=-10_000_000_000, le=10_000_000_000, examples=[100_000]
    )
    base_retirement_per_mo: int = Field(
        ..., ge=-10_000_000, le=10_000_000, examples=[100]
    )
    base_retirement_per_yr_increase: int = Field(
        ..., ge=-10_000_000, le=10_000_000, examples=[100]
    )
    retirement_extra_expenses: int = Field(
        ..., ge=-10_000_000, le=10_000_000, examples=[1_000]
    )
    base_rf_interest_per_yr: Decimal = Field(
        ..., ge=0, max_digits=5, decimal_places=1, examples=[3.5]
    )
    base_mkt_interest_per_yr: Decimal = Field(
        ..., max_digits=5, decimal_places=1, examples=[3.5]
    )
    base_inflation_per_yr: Decimal = Field(
        ..., max_digits=5, decimal_places=1, examples=[3.5]
    )


from dateutil.relativedelta import relativedelta


class InvalidBirthdateError(Exception):
    """Raised when the birthdate is not valid"""

    pass


class InvalidRetirementAge(Exception):
    """Raised when the retirement age is too old"""

    pass


class InvalidBaseSavings(Exception):
    """Raised when the retirement age is too old"""

    pass


class InvalidBaseSavedPerMo(Exception):
    """Raised when the saved per month is too extreme"""

    pass


class InvalidBaseSavingsIncrease(Exception):
    """Raised when the savings increase is nonsensical"""

    pass


class InvalidSavingsLowerLimit(Exception):
    """Raised when the savings lower limit is negative"""

    pass


class InvalidBaseMonthlyBills(Exception):
    """Raised when the savings lower limit is negative"""

    pass


def apply_validations(assumptions: dict) -> None:
    """Validate inputs"""

    # Birthdate in the future
    if assumptions["birthdate"] > date.today():
        raise InvalidBirthdateError("Please enter a valid birthdate")

    # Birthdate too old
    if assumptions["birthdate"] > date.today() - relativedelta(years=120):
        raise InvalidBirthdateError("Please enter a valid birthdate")

    # Retirement age in years is negative
    if assumptions["retirement_age_yrs"] < 0:
        raise InvalidRetirementAge("Please enter a valid retirement age")

    # Retirement age in months is negative
    if assumptions["retirement_age_mos"] < 0:
        raise InvalidRetirementAge("Please enter a valid retirement age (months)")

    # Retirement age in months between 0 and 11
    if assumptions["retirement_age_mos"] > 11:
        raise InvalidRetirementAge("Please enter a valid retirement age (months)")

    # Base savings is sensical
    if (
        10_000_000_000 < assumptions["base_savings"]
        or assumptions["base_savings"] < -10_000_000_000
    ):
        raise InvalidBaseSavings("Please enter a more modest base savings")

    # Base saved per month is sensical
    if (
        10_000_000 < assumptions["base_saved_per_mo"]
        or assumptions["base_saved_per_mo"] < -10_000_000
    ):
        raise InvalidBaseSavedPerMo("Please enter a more modest saved per month")

    # Base savings increase is sensical
    if (
        1_000 < assumptions["base_savings_per_yr_increase"]
        or assumptions["base_savings_per_yr_increase"] < -1_000
    ):
        raise InvalidBaseSavingsIncrease(
            "Please enter a more modest savings per year increase"
        )

    # Base savings lower limit is non-negative
    if assumptions["base_savings_lower_limit"] < 0:
        raise InvalidSavingsLowerLimit(
            "Please enter a non-negative savings lower limit"
        )

    # Base monthly bills is sensical
    if (
        10_000_000 < assumptions["base_monthly_bills"]
        or assumptions["base_monthly_bills"] < -10_000_000
    ):
        raise InvalidBaseMonthlyBills(
            "Please enter a more modest amount for base monthly bills"
        )
