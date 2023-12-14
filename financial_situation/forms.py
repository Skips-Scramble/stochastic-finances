from django import forms

from .models import TestCalc, FinancialInputs, Job, Person

INPUT_CLASSES = "w-full py-4 px-6 rounded-xl border"


class NewTestCalcForm(forms.ModelForm):
    """Test"""

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
    """Class to contain all pertinent financial information"""

    class Meta:
        model = FinancialInputs
        fields = [
            "name",
            "birthday",
            "retirement_age_yrs",
            "retirement_age_mos",
            "base_savings",
            "base_saved_per_mo",
            "base_savings_per_yr_increase",
            "base_monthly_bills",
            "payment_1_item_name",
            "payment_1_item_pmt_start_age_yrs",
            "payment_1_item_pmt_start_age_mos",
            "payment_1_item_pmt_length_yrs",
            "payment_1_item_down_pmt",
            "payment_1_item_monthly_pmt",
            "base_rf_interest_per_yr",
            "base_retirement",
            "base_retirement_per_mo",
            "base_retirement_per_yr_increase",
            "base_mkt_interest_per_yr",
            "rf_interest_change_mos",
            "savings_lower_limit",
            "base_inflation_per_yr",
            "retirement_extra_expenses",
        ]
        labels = {
            "name": "Scenario Name",
            "birthday": "Birthday (MM/DD/YYYY)",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "How much do you save per month",
            "base_savings_per_yr_increase": "Yearly savings contribution increase (%)",
            "base_monthly_bills": "Usual monthly expenses",
            "payment_1_item_name": "Extra payment 1 name",
            "payment_1_item_pmt_start_age_yrs": "Extra payment 1 start age in years",
            "payment_1_item_pmt_start_age_mos": "Extra payment 1 start age months",
            "payment_1_item_pmt_length_yrs": "Extra payment 1 length in years",
            "payment_1_item_down_pmt": "Extra payment 1 down payment",
            "payment_1_item_monthly_pmt": "Extra payment 1 monthly payment",
            "base_rf_interest_per_yr": "Assumed savings account interest rate",
            "base_retirement": "Current retirement amount",
            "base_retirement_per_mo": "Monthly retirement contributions",
            "base_retirement_per_yr_increase": "Yearly retirement contribution increase ($)",
            "base_mkt_interest_per_yr": "Assumed retirement interest rate",
            "rf_interest_change_mos": "How often do you assume savings rate will change (in months)",
            "savings_lower_limit": "Minimum you'd like in your savings before fully taking from retirement",
            "base_inflation_per_yr": "Assumed inflation per year",
            "retirement_extra_expenses": "Extra expenses in retirement (vacations, etc.)",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "birthday": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_monthly_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "payment_1_item_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "payment_1_item_pmt_start_age_yrs": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_pmt_start_age_mos": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_pmt_length_yrs": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_down_pmt": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_monthly_pmt": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_rf_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_retirement": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_mkt_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "rf_interest_change_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "savings_lower_limit": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_inflation_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_extra_expenses": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
        }


class EditFinancialSituation(forms.ModelForm):
    class Meta:
        model = FinancialInputs
        fields = [
            "name",
            "birthday",
            "retirement_age_yrs",
            "retirement_age_mos",
            "base_savings",
            "base_saved_per_mo",
            "base_savings_per_yr_increase",
            "base_monthly_bills",
            "payment_1_item_name",
            "payment_1_item_pmt_start_age_yrs",
            "payment_1_item_pmt_start_age_mos",
            "payment_1_item_pmt_length_yrs",
            "payment_1_item_down_pmt",
            "payment_1_item_monthly_pmt",
            "base_rf_interest_per_yr",
            "base_retirement",
            "base_retirement_per_mo",
            "base_retirement_per_yr_increase",
            "base_mkt_interest_per_yr",
            "rf_interest_change_mos",
            "savings_lower_limit",
            "base_inflation_per_yr",
            "retirement_extra_expenses",
        ]
        labels = {
            "name": "Scenario Name",
            "birthday": "Birthday (MM/DD/YYYY)",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "How much do you save per month",
            "base_savings_per_yr_increase": "Yearly savings contribution increase (%)",
            "base_monthly_bills": "Usual monthly expenses",
            "payment_1_item_name": "Extra payment 1 name",
            "payment_1_item_pmt_start_age_yrs": "Extra payment 1 start age in years",
            "payment_1_item_pmt_start_age_mos": "Extra payment 1 start age months",
            "payment_1_item_pmt_length_yrs": "Extra payment 1 length in years",
            "payment_1_item_down_pmt": "Extra payment 1 down payment",
            "payment_1_item_monthly_pmt": "Extra payment 1 monthly payment",
            "base_rf_interest_per_yr": "Assumed savings account interest rate",
            "base_retirement": "Current retirement amount",
            "base_retirement_per_mo": "Monthly retirement contributions",
            "base_retirement_per_yr_increase": "Yearly retirement contribution increase ($)",
            "base_mkt_interest_per_yr": "Assumed retirement interest rate",
            "rf_interest_change_mos": "How often do you assume savings rate will change (in months)",
            "savings_lower_limit": "Minimum you'd like in your savings before fully taking from retirement",
            "base_inflation_per_yr": "Assumed inflation per year",
            "retirement_extra_expenses": "Extra expenses in retirement (vacations, etc.)",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "birthday": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_monthly_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "payment_1_item_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "payment_1_item_pmt_start_age_yrs": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_pmt_start_age_mos": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_pmt_length_yrs": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_down_pmt": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "payment_1_item_monthly_pmt": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_rf_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_retirement": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_mkt_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "rf_interest_change_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "savings_lower_limit": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_inflation_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_extra_expenses": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
        }
