from django import forms

from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)

INPUT_CLASSES = "w-full py-4 px-6 rounded-xl border"


class GeneralInputsForm(forms.ModelForm):
    """Class to contain all pertinent general information"""

    class Meta:
        model = GeneralInputsModel
        fields = [
            "is_active",
            "birthday",
            "retirement_age_yrs",
            "retirement_age_mos",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "birthday": "Birthday (MM/DD/YYYY)",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "birthday": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }


class SavingsInputsForm(forms.ModelForm):
    """Class to contain all pertinent savings information"""

    class Meta:
        model = SavingsInputsModel
        fields = [
            "is_active",
            "base_savings",
            "base_saved_per_mo",
            "base_savings_per_yr_increase",
            "savings_lower_limit",
            "base_monthly_bills",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "How much do you save per month",
            "base_savings_per_yr_increase": "Yearly savings contribution increase (%)",
            "savings_lower_limit": "The lowest amount of savings before you fully use retirement",
            "base_monthly_bills": "Usual monthly expenses",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "savings_lower_limit": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_monthly_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }


class PaymentsInputsForm(forms.ModelForm):
    """Class to contain all pertinent payment information"""

    class Meta:
        model = PaymentsInputsModel
        fields = [
            "is_active",
            "pmt_name",
            "pmt_start_age_yrs",
            "pmt_start_age_mos",
            "pmt_length_yrs",
            "pmt_length_mos",
            "down_pmt",
            "monthly_pmt",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "pmt_name": "Extra payment name",
            "pmt_start_age_yrs": "Extra payment start age in years",
            "pmt_start_age_mos": "Extra payment start age months",
            "pmt_length_yrs": "Extra payment length in years",
            "pmt_length_mos": "Extra payment length in months",
            "down_pmt": "Extra payment down payment",
            "monthly_pmt": "Extra payment monthly payment",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "pmt_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "pmt_start_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_start_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_length_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_length_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "down_pmt": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "monthly_pmt": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }


class RetirementInputsForm(forms.ModelForm):
    """Class to contain all pertinent financial information"""

    class Meta:
        model = RetirementInputsModel
        fields = [
            "is_active",
            "base_retirement",
            "base_retirement_per_mo",
            "base_retirement_per_yr_increase",
            "retirement_extra_expenses",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "base_retirement": "Current retirement amount",
            "base_retirement_per_mo": "Monthly retirement contributions",
            "base_retirement_per_yr_increase": "Yearly retirement contribution increase ($)",
            "retirement_extra_expenses": "Extra expenses in retirement (vacations, etc.)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "base_retirement": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "retirement_extra_expenses": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
        }


class RatesInputsForm(forms.ModelForm):
    """Class to contain all pertinent financial information"""

    class Meta:
        model = RatesInputsModel
        fields = [
            "is_active",
            "base_rf_interest_per_yr",
            "base_mkt_interest_per_yr",
            "rf_interest_change_mos",
            "base_inflation_per_yr",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "base_rf_interest_per_yr": "Assumed savings account interest rate",
            "base_mkt_interest_per_yr": "Assumed retirement interest rate",
            "rf_interest_change_mos": "How often do you assume savings rate will change (in months)",
            "base_inflation_per_yr": "Assumed inflation per year",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "base_rf_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_mkt_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "rf_interest_change_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_inflation_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
