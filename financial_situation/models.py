from django.contrib.auth.models import User
from django.db import models


class TestCalc(models.Model):
    name = models.CharField(max_length=255)
    current_savings_account = models.FloatField()
    current_interest = models.FloatField()
    next_year = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Test_Calcs"

    def __str__(self):
        return self.name


class FinancialInputs(models.Model):
    name = models.CharField(max_length=255, default="test")
    birthday = models.CharField(max_length=10, default="MM/DD/YYYY")
    retirement_age_yrs = models.FloatField()
    retirement_age_mos = models.FloatField()
    base_savings = models.FloatField()
    base_saved_per_mo = models.FloatField()
    base_savings_per_yr_increase = models.FloatField()
    base_monthly_bills = models.FloatField()
    payment_1_item_name = models.CharField(max_length=100, null=True, blank=True)
    payment_1_item_pmt_start_age_yrs = models.IntegerField(null=True, blank=True)
    payment_1_item_pmt_start_age_mos = models.IntegerField(null=True, blank=True)
    payment_1_item_pmt_length_yrs = models.IntegerField(null=True, blank=True)
    payment_1_item_down_pmt = models.FloatField(null=True, blank=True)
    payment_1_item_monthly_pmt = models.FloatField(null=True, blank=True)
    base_rf_interest_per_yr = models.FloatField()
    base_retirement = models.FloatField()
    base_retirement_per_mo = models.FloatField()
    base_retirement_per_yr_increase = models.FloatField()
    base_mkt_interest_per_yr = models.FloatField()
    rf_interest_change_mos = models.FloatField()
    savings_lower_limit = models.FloatField()
    base_inflation_per_yr = models.FloatField()
    retirement_extra_expenses = models.FloatField()
    input_dict = models.CharField(max_length=10000, null=True, blank=True)
    created_by = models.ForeignKey(
        User, related_name="items", on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Fiancial_Inputs"

    def __str__(self):
        return self.name


class GeneralInputsModel(models.Model):
    birthday = models.CharField(max_length=10, default="MM/DD/YYYY")
    retirement_age_yrs = models.FloatField()
    retirement_age_mos = models.FloatField()

    class Meta:
        verbose_name_plural = "General_Inputs"


class SavingsInputsModel(models.Model):
    base_savings = models.FloatField()
    base_saved_per_mo = models.FloatField()
    base_savings_per_yr_increase = models.FloatField()

    class Meta:
        verbose_name_plural = "Savings_Inputs"
