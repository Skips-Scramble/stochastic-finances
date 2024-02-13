from datetime import date

from django.core.exceptions import ValidationError


def validate_range_birthdate(input: date):
    """Custom validation of the user's birthdate"""
    if input.year < 1900:
        raise ValidationError("Please enter a birthdate after 1900")


def validate_range_age_yrs(input: int):
    """Custom validation to ensure an input is between two values"""
    if input < 0 or input > 110:
        raise ValidationError("Please enter a value between 0 and 110")


def validate_range_age_mos(input: int):
    """Custom validation to ensure an input is between two values"""
    if input < 0 or input > 11:
        raise ValidationError(
            "Please enter a value between 0 (the month you were born) and 11"
        )


def validate_base_savings(input: float):
    """Ensure base_savings is reasonable"""
    if input < -10_000_000 or input > 10_000_000:
        raise ValidationError(
            "That's quite a lot of savings. Try to keep in under $10,000,000, plus or minus"
        )
