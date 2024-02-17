from django.contrib.auth.models import User
from django.db import models

from .model_validators import (
    decimal_validator,
    validate_base_monthly_bills,
    validate_base_per_yr_increase,
    validate_base_retirement,
    validate_base_retirement_per_mo,
    validate_base_retirement_per_yr_increase,
    validate_base_saved_per_mo,
    validate_base_savings,
    validate_down_pmt,
    validate_monthly_pmt,
    validate_pmt_length_yrs,
    validate_pmt_start_age_yrs,
    validate_range_age_mos,
    validate_range_age_yrs,
    validate_range_birthdate,
    validate_rates_per_yr,
    validate_retirement_extra_expenses,
    validate_savings_lower_limit,
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
    )
    base_savings = models.FloatField(
        validators=[validate_base_savings, decimal_validator]
    )
    base_saved_per_mo = models.FloatField(
        validators=[validate_base_saved_per_mo, decimal_validator],
    )
    base_savings_per_yr_increase = models.FloatField(
        validators=[validate_base_per_yr_increase, decimal_validator],
    )
    savings_lower_limit = models.FloatField(
        validators=[validate_savings_lower_limit, decimal_validator]
    )
    base_monthly_bills = models.FloatField(
        validators=[validate_base_monthly_bills, decimal_validator]
    )
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
    pmt_start_age_yrs = models.IntegerField(
        null=True, blank=True, validators=[validate_pmt_start_age_yrs]
    )
    pmt_start_age_mos = models.IntegerField(
        null=True, blank=True, validators=[validate_range_age_mos]
    )
    pmt_length_yrs = models.IntegerField(
        null=True, blank=True, validators=[validate_pmt_length_yrs]
    )
    pmt_length_mos = models.IntegerField(
        null=True, blank=True, validators=[validate_range_age_mos]
    )
    down_pmt = models.FloatField(
        null=True, blank=True, validators=[validate_down_pmt, decimal_validator]
    )
    monthly_pmt = models.FloatField(
        null=True, blank=True, validators=[validate_monthly_pmt, decimal_validator]
    )
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
    base_retirement = models.FloatField(
        validators=[validate_base_retirement, decimal_validator]
    )
    base_retirement_per_mo = models.FloatField(
        validators=[validate_base_retirement_per_mo, decimal_validator]
    )
    base_retirement_per_yr_increase = models.FloatField(
        validators=[validate_base_retirement_per_yr_increase, decimal_validator]
    )
    retirement_extra_expenses = models.FloatField(
        validators=[validate_retirement_extra_expenses, decimal_validator]
    )
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
    base_rf_interest_per_yr = models.FloatField(
        validators=[validate_rates_per_yr, decimal_validator]
    )
    base_mkt_interest_per_yr = models.FloatField(
        validators=[validate_rates_per_yr, decimal_validator]
    )
    base_inflation_per_yr = models.FloatField(
        validators=[validate_rates_per_yr, decimal_validator]
    )
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
