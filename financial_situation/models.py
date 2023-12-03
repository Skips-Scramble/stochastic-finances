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
    birthday = models.DateField()
    base_retirement = models.FloatField()
    base_retirement_per_mo = models.FloatField()
    base_retirement_per_yr_increase = models.FloatField()
    base_mkt_interest_per_yr = models.FloatField()
    base_inflation_per_yr = models.FloatField()
    retirement_age_yrs = models.FloatField()
    retirement_age_mos = models.FloatField()
    base_rf_interest_per_yr = models.FloatField()
    rf_interest_change_mos = models.FloatField()
    ss_withdraw_age_yrs = models.FloatField()
    ss_withdraw_age_mos = models.FloatField()
    ss_withdraw_amt = models.FloatField()
    base_savings = models.FloatField()
    base_saved_per_mo = models.FloatField()
    base_savings_per_yr_increase = models.FloatField()
    base_monthly_bills = models.FloatField()
    base_monthly_rent = models.FloatField()
    savings_lower_limit = models.FloatField()
    retirement_extra_expenses = models.FloatField()
    payment_items = models.FloatField()
    rent_end_age_yrs = models.FloatField()
    rent_end_age_months = models.FloatField()
    input_dict = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Fiancial_Inputs"

    def __str__(self):
        return self.name
