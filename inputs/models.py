from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


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


class GeneralInputsModel(models.Model):
    is_active = models.BooleanField(
        default=False,
        help_text="This determines whether or not these inputs will be used to calculate your financial situation",
    )
    birthdate = models.DateField(
        validators=[validate_range_birthdate],
        help_text="Your birthdate (after 1900) in MM/DD/YYYY format",
    )
    retirement_age_yrs = models.IntegerField(
        validators=[validate_range_age_yrs],
        help_text="The age in years when you will retire. For example, if you are going to retire when you are 65 years and 3 months, put 65",
    )
    retirement_age_mos = models.IntegerField(
        validators=[validate_range_age_mos],
        help_text="The age in months when you will retire. For example, if you are going to retire when you are 65 years and 3 months, this would be 3",
    )
    created_by = models.ForeignKey(
        User,
        related_name="general_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "General_Inputs"


class SavingsInputsModel(models.Model):
    is_active = models.BooleanField(default=False)
    base_savings = models.FloatField(
        validators=[validate_base_savings],
        help_text='This is the amount of money you save each month and contribute to your savings account(s). A negative amount would represent you are spending that amount each month. If this is the case, it would probably be better to put a 0 in this field and move those payments to the "Payemnts" section',
    )
    base_saved_per_mo = models.FloatField()
    base_savings_per_yr_increase = models.FloatField()
    savings_lower_limit = models.FloatField()
    base_monthly_bills = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="savings_inputs",
        on_delete=models.CASCADE,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Savings_Inputs"


class PaymentsInputsModel(models.Model):
    is_active = models.BooleanField(default=False)
    pmt_name = models.CharField(max_length=100, null=True, blank=True)
    pmt_start_age_yrs = models.IntegerField(null=True, blank=True)
    pmt_start_age_mos = models.IntegerField(null=True, blank=True)
    pmt_length_yrs = models.IntegerField(null=True, blank=True)
    pmt_length_mos = models.IntegerField(null=True, blank=True)
    down_pmt = models.FloatField(null=True, blank=True)
    monthly_pmt = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="payments_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payments_Inputs"


class RetirementInputsModel(models.Model):
    is_active = models.BooleanField(default=False)
    base_retirement = models.FloatField()
    base_retirement_per_mo = models.FloatField()
    base_retirement_per_yr_increase = models.FloatField()
    retirement_extra_expenses = models.FloatField()
    created_by = models.ForeignKey(
        User,
        related_name="retirement_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Retirement_Inputs"


class RatesInputsModel(models.Model):
    is_active = models.BooleanField(default=False)
    base_rf_interest_per_yr = models.FloatField()
    base_mkt_interest_per_yr = models.FloatField()
    base_inflation_per_yr = models.FloatField()
    created_by = models.ForeignKey(
        User,
        related_name="rates_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Rates_Inputs"
