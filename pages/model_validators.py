from datetime import date

from django.core.exceptions import ValidationError


def validate_reg_pmt_amt(value: float):
    """Ensure regular payment amount is reasonable (absolute value < $100,000,000)"""
    if abs(value) > 100_000_000:
        raise ValidationError(
            "Please keep regular payments to less than $100,000,000 in absolute value."
        )


def validate_positive_int(value: int):
    """Ensure value is at least 1 (for frequency/timeframe)"""
    if value is not None and value < 1:
        raise ValidationError("Please enter a value of at least 1.")


def validate_non_negative_int(value: int):
    """Ensure value is 0 or greater (for recurring_length)"""
    if value is not None and value < 0:
        raise ValidationError("Please enter a value of 0 or greater.")


def decimal_validator(value: float):
    """Ensure there are at most 2 decimal point used"""
    if round(value, 2) != value:
        raise ValidationError("Please only use up to 2 decimal points")


def validate_range_age_mos(value: int):
    """Custom validation to ensure an input is between two values"""
    if value < 0 or value > 11:
        raise ValidationError(
            "Please enter a value between 0 (the month you were born) and 11"
        )


def validate_range_birthdate(value: date):
    """Custom validation of the user's birthdate"""
    if value.year < 1900:
        raise ValidationError("Please enter a birthdate after 1900")


def validate_range_age_yrs(value: int):
    """Custom validation to ensure an input is between two values"""
    if value < 0 or value > 110:
        raise ValidationError("Please enter a value between 0 and 110")


def validate_base_savings(value: float):
    """Ensure base_savings is reasonable"""
    if value < -100_000_000 or value > 100_000_000:
        raise ValidationError(
            "That's quite a lot of savings. Try to keep it within $100,000,000, plus or minus"
        )


def validate_base_saved_per_mo(value: float):
    """Ensure base_saved_per_mo is reasonable"""
    if value < -10_000_000 or value > 10_000_000:
        raise ValidationError(
            "That's quite a lot of savings. Try to keep in within $10,000,000, plus or minus"
        )


def validate_base_per_yr_increase(value: float):
    """Ensure base_savings_per_yr_increase is reasonable"""
    if value < -1000 or value > 1000:
        raise ValidationError(
            "That's quite a high year-over-year savings increase. Try to keep it within ±1,000% (percent), not dollars."
        )


def validate_savings_lower_limit(value: float):
    """Ensure savings lower limit is sane"""
    if value > 100_000_000:
        raise ValidationError("Please lower limit to under $100,000,000")


def validate_base_monthly_bills(value: float):
    """Ensure monthly bills are reasonable"""
    if value < -10_000_000 or value > 10_000_000:
        raise ValidationError(
            "Please keep cash flows within plus or minus $10,000,000 a month"
        )


def validate_pmt_start_age_yrs(value: int):
    """Ensure payments start at a reasonable age"""
    if value < 0:
        raise ValidationError("Please ensure the age is at least 0 years")


def validate_pmt_length_yrs(value: float):
    """Ensure payment lengths (in years) is reasonable"""
    if value < 0 or value > 110:
        raise ValidationError("Please enter a value between 0 and 110")


def validate_down_pmt(value: float):
    """Ensure down payments are reasonable"""
    if value < -100_000_000 or value > 100_000_000:
        raise ValidationError(
            "Hey big spender, please keep down payments to less than $100,000,000 in absolute value"
        )


def validate_monthly_pmt(value: float):
    """Ensure down payments are reasonable"""
    if value < -100_000_000 or value > 100_000_000:
        raise ValidationError(
            "Hey big spender, please keep monthly payments to less than $100,000,000 in absolute value"
        )


def validate_base_retirement(value: float):
    """Validate base retirement amount"""
    if value < -100_000_000 or value > 100_000_000:
        raise ValidationError(
            "That's quite a lot of retirement. Try to keep it within $100,000,000, plus or minus"
        )


def validate_base_retirement_per_mo(value: float):
    """Valide the base_retirement_per_mo input"""
    if value < -1_000_000 or value > 1_000_000:
        raise ValidationError("Please enter a value within $1,000,000, plus or minus")


def validate_base_retirement_per_yr_increase(value: float):
    """Validate base_retirement_per_yr_increase input"""
    if value < -1_000_000 or value > 1_000_000:
        raise ValidationError(
            "That looks like a big retirement swing. Please keep values to within $1,000,000, plus or minus"
        )


def validate_retirement_extra_expenses(value: float):
    """Validate retirement extra expenses"""
    limit = 10_000_000
    if not (-1) * limit < value < limit:
        raise ValidationError(f"Please keep values within ${limit}, plus or minus")


def validate_rates_per_yr(value: float):
    """Validate interest rates (percent per year)"""
    if value < -100 or value > 100:
        raise ValidationError("Please enter a rate between -100% and 100%.")
