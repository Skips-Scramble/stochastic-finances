from django import forms

from .models import GeneralInputsModel, SavingsInputsModel

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
        ]
        labels = {
            "is_active": "Use this for calculations",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "How much do you save per month",
            "base_savings_per_yr_increase": "Yearly savings contribution increase (%)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
        }
