from django.contrib.auth.models import User
from django.db import models


class GeneralInputsModel(models.Model):
    is_active = models.BooleanField(default=False)
    birthday = models.CharField(max_length=10, default="MM/DD/YYYY")
    retirement_age_yrs = models.FloatField()
    retirement_age_mos = models.FloatField()
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
    base_savings = models.FloatField()
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
