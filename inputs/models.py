from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from .model_validators import (
    validate_base_per_yr_increase,
    validate_base_saved_per_mo,
    validate_base_savings,
    validate_range_age_mos,
    validate_range_age_yrs,
    validate_range_birthdate,
)


class GeneralInputsModel(models.Model):
    is_active = models.BooleanField(
        default=False,
    )
    birthdate = models.DateField(
        validators=[validate_range_birthdate],
    )
    retirement_age_yrs = models.IntegerField(
        validators=[validate_range_age_yrs],
    )
    retirement_age_mos = models.IntegerField(
        validators=[validate_range_age_mos],
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
    is_active = models.BooleanField(
        default=False,
        help_text="This determines whether or not these inputs will be used to calculate your financial situation",
    )
    base_savings = models.FloatField(
        validators=[validate_base_savings],
        help_text='This is the amount of money you save each month and contribute to your savings account(s). A negative amount would represent you are spending that amount each month. If this is the case, it would probably be better to put a 0 in this field and move those payments to the "Payemnts" section',
    )
    base_saved_per_mo = models.FloatField(
        validators=[validate_base_saved_per_mo],
        help_text="This is the average amount of money you save per month. Said another way, this is the average amount your savings account increases by each month (excluding interest). This could be negative.",
    )
    base_savings_per_yr_increase = models.FloatField(
        validators=[validate_base_per_yr_increase],
        help_text="The year-over-year savings increase (as a percent). For example, if you expect a 3% salary increase every year, you might put 3% here.",
    )
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
