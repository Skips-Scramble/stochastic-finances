from datetime import date

from django.core.exceptions import ValidationError


def decimal_validator(input: float):
    """Ensure there are at most 2 decimal point used"""
    if round(input, 2) != input:
        raise ValidationError("Please only use up to 2 decimal points")


def validate_range_age_mos(input: int):
    """Custom validation to ensure an input is between two values"""
    if input < 0 or input > 11:
        raise ValidationError(
            "Please enter a value between 0 (the month you were born) and 11"
        )


def validate_range_birthdate(input: date):
    """Custom validation of the user's birthdate"""
    if input.year < 1900:
        raise ValidationError("Please enter a birthdate after 1900")


def validate_range_age_yrs(input: int):
    """Custom validation to ensure an input is between two values"""
    if input < 0 or input > 110:
        raise ValidationError("Please enter a value between 0 and 110")


def validate_base_savings(input: float):
    """Ensure base_savings is reasonable"""
    if input < -100_000_000 or input > 100_000_000:
        raise ValidationError(
            "That's quite a lot of savings. Try to keep it within $100,000,000, plus or minus"
        )


def validate_base_saved_per_mo(input: float):
    """Ensure base_saved_per_mo is reasonable"""
    if input < -10_000_000 or input > 10_000_000:
        raise ValidationError(
            "That's quite a lot of savings. Try to keep in within $10,000,000, plus or minus"
        )


def validate_base_per_yr_increase(input: float):
    """Ensure base_savings_per_yr_increase is reasonable"""
    if input < -1000 or input > 1000:
        raise ValidationError(
            "That's quite a high year-over-year savings increase. Try to keep in within 1,000%, plus or minus"
        )


def validate_savings_lower_limit(input: float):
    """Ensure savings lower limit is sane"""
    if input > 100_000_000:
        raise ValidationError("Please lower limit to under $100,000,000")


def validate_base_monthly_bills(input: float):
    """Ensure monthly bills are reasonable"""
    if input < -10_000_000 or input > 10_000_000:
        raise ValidationError(
            "Please keep cash flows within plus or minus $10,000,000 a month"
        )


def validate_pmt_start_age_yrs(input: int):
    """Ensure payments start at a reasonable age"""
    if input < 0:
        raise ValidationError("Please ensure the age is at least 0 years")


def validate_pmt_length_yrs(input: float):
    """Ensure payment lengths (in years) is reasonable"""
    if input < 0 or input > 110:
        raise ValidationError("Please enter a value between 0 and 110")


def validate_down_pmt(input: float):
    """Ensure down payments are reasonable"""
    if input < -100_000_000 or input > 100_000_000:
        raise ValidationError(
            "Hey big spender, please keep down payments to less than $100,000,000 in absolute value"
        )


def validate_monthly_pmt(input: float):
    """Ensure down payments are reasonable"""
    if input < -100_000_000 or input > 100_000_000:
        raise ValidationError(
            "Hey big spender, please keep monthly payments to less than $100,000,000 in absolute value"
        )


def validate_base_retirement(input: float):
    """Validate base retirement amount"""
    if input < -100_000_000 or input > 100_000_000:
        raise ValidationError(
            "That's quite a lot of retirement. Try to keep it within $100,000,000, plus or minus"
        )


def validate_base_retirement_per_mo(input: float):
    """Valide the base_retirement_per_mo input"""
    if input < -1_000_000 or input > 1_000_000:
        raise ValidationError("Please enter a value within $1,000,000, plus or minus")


def validate_base_retirement_per_yr_increase(input: float):
    """Validate base_retirement_per_yr_increase input"""
    if input < -1_000_000 or input > 1_000_000:
        raise ValidationError(
            "That looks like a big retirement swing. Please keep values to within $1,000,000, plus or minus"
        )


def validate_retirement_extra_expenses(input: float):
    """Validate retirement extra expenses"""
    limit = 10_000_000
    if not (-1) * limit < input < limit:
        raise ValidationError(f"Please keep values within ${limit}, plus or minus")


def validate_rates_per_yr(input: float):
    """Validate base_rf_interest_per_yr"""
    limit = 1000
    if not (-1) * limit * 100 < input < limit * 100:
        raise ValidationError(f"Please keep values within {limit}%, plus or minus")
