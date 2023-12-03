from django import forms

from .models import TestCalc, FinancialInputs

INPUT_CLASSES = "w-full py-4 px-6 rounded-xl border"


class NewTestCalcForm(forms.ModelForm):
    class Meta:
        model = TestCalc
        fields = ["name", "current_savings_account", "current_interest"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "current_savings_account": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "current_interest": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }

    # next_year = forms.FloatField(
    #     required=False, widget=forms.TextInput(attrs={"readonly": 'readonly'})
    # )


class NewFinancialSituation(forms.ModelForm):
    class Meta:
        model = FinancialInputs
        fields = [
            "name",
            "birthday",
            "base_retirement",
            "base_retirement_per_mo",
            "base_retirement_per_yr_increase",
            "base_mkt_interest_per_yr",
            "base_inflation_per_yr",
            "retirement_age_yrs",
            "retirement_age_mos",
            "base_rf_interest_per_yr",
            "rf_interest_change_mos",
            "ss_withdraw_age_yrs",
            "ss_withdraw_age_mos",
            "ss_withdraw_amt",
            "base_savings",
            "base_saved_per_mo",
            "base_savings_per_yr_increase",
            "base_monthly_bills",
            "base_monthly_rent",
            "savings_lower_limit",
            "retirement_extra_expenses",
            "payment_items",
            "rent_end_age_yrs",
            "rent_end_age_months",
        ]
        labels = {
            "name": "Scenario Name",
            "birthday": "Birthday (MM/DD/YYYY)",
            "base_retirement": "Current retirement amount",
            "base_retirement_per_mo": "Monthly retirement contributions",
            "base_retirement_per_yr_increase": "Yearly retirement contribution increase ($)",
            "base_mkt_interest_per_yr": "Assumed retirement interest rate",
            "base_inflation_per_yr": "Assumed inflation per year",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
            "base_rf_interest_per_yr": "Assumed savings account interest rate",
            "rf_interest_change_mos": "How often do you assume savings rate will change (in months)",
            "ss_withdraw_age_yrs": "Age you'll begin to withdraw Social Security (years)",
            "ss_withdraw_age_mos": "Age you'll begin to widthdraw Social Security (months)",
            "ss_withdraw_amt": "How much will you Social Security check be",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "How much do you save per month",
            "base_savings_per_yr_increase": "Yearly retirement contribution increase (%)",
            "base_monthly_bills": "Usual monthly expenses",
            "base_monthly_rent": "Current rent/mortgage payment",
            "savings_lower_limit": "Minimum you'd like in your savings before fully taking from retirement",
            "retirement_extra_expenses": "Extra expenses in retirement (vacations, etc.)",
            "payment_items": "Non-continuous bills (car payments, mortgage, etc.)",
            "rent_end_age_yrs": "When will you stop paying rent (yrs)",
            "rent_end_age_months": "When will you stop paying rent (months)",
                  }
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "birthday": forms.DateInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_mkt_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_inflation_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_rf_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "rf_interest_change_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "ss_withdraw_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "ss_withdraw_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "ss_withdraw_amt": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_monthly_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_monthly_rent": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "savings_lower_limit": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_extra_expenses": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_items": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "rent_end_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "rent_end_age_months": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
