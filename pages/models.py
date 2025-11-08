from django.db import models

from accounts.models import CustomUser

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
    validate_pmt_length_yrs,
    validate_pmt_start_age_yrs,
    validate_range_age_mos,
    validate_range_age_yrs,
    validate_range_birthdate,
    validate_rates_per_yr,
    validate_retirement_extra_expenses,
    validate_savings_lower_limit,
    validate_reg_pmt_amt,
    validate_positive_int,
    validate_non_negative_int,
)


class GeneralInputsModel(models.Model):
    """General inputs to the model"""

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

    add_healthcare = models.BooleanField(
        default=False,
    )

    retirement_extra_expenses = models.FloatField(
        validators=[validate_retirement_extra_expenses, decimal_validator],
        default=0,
    )

    created_by = models.ForeignKey(
        CustomUser,
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
        CustomUser,
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
    reg_pmt_amt = models.FloatField(
        null=True, blank=True, validators=[validate_reg_pmt_amt, decimal_validator]
    )
    pmt_freq_mos = models.IntegerField(
        null=True, blank=True, validators=[validate_positive_int]
    )
    recurring_purchase = models.BooleanField(default=False)
    recurring_timeframe = models.IntegerField(
        null=True, blank=True, validators=[validate_positive_int]
    )
    recurring_length = models.IntegerField(
        null=True, blank=True, validators=[validate_non_negative_int]
    )

    created_by = models.ForeignKey(
        CustomUser,
        related_name="payments_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payments_Inputs"


class RetirementInputsModel(models.Model):
    RETIREMENT_TYPE_CHOICES = [
        ("traditional_401k", "Traditional 401(k)"),
        ("roth_401k", "Roth 401(k)"),
        ("traditional_ira", "Traditional IRA"),
        ("roth_ira", "Roth IRA"),
    ]

    is_active = models.BooleanField(default=False)
    retirement_type = models.CharField(
        max_length=20,
        choices=RETIREMENT_TYPE_CHOICES,
        default="traditional_401k",
    )
    base_retirement = models.FloatField(
        validators=[validate_base_retirement, decimal_validator]
    )
    base_retirement_per_mo = models.FloatField(
        validators=[validate_base_retirement_per_mo, decimal_validator]
    )
    base_retirement_per_yr_increase = models.FloatField(
        validators=[validate_base_retirement_per_yr_increase, decimal_validator]
    )
    created_by = models.ForeignKey(
        CustomUser,
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
        CustomUser,
        related_name="rates_inputs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Rates_Inputs"
