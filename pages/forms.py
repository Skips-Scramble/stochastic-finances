from django import forms

from .models import GeneralInputsModel

INPUT_CLASSES = "form-control"


class GeneralInputsForm(forms.ModelForm):
    """Class to contain all pertinent general information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    class Meta:
        model = GeneralInputsModel
        fields = [
            "is_active",
            "birthdate",
            "retirement_age_yrs",
            "retirement_age_mos",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "birthdate": "Birthdate (MM/DD/YYYY)",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "birthdate": forms.DateInput(
                attrs={"class": INPUT_CLASSES}, format="%m/%d/%Y"
            ),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
