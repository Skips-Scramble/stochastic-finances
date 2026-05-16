from django import forms

from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)

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
            "add_healthcare",
            "include_pre_medicare_insurance",
            "add_medical_bills",
            "monthly_medical_bills",
            "retirement_extra_expenses",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "birthdate": "Birthdate (MM/DD/YYYY)",
            "retirement_age_yrs": "Retirement age (years)",
            "retirement_age_mos": "Retirement age (months)",
            "add_healthcare": "Include healthcare costs for me",
            "include_pre_medicare_insurance": "Include ACA insurance cost when retired and under 65",
            "add_medical_bills": "Include your own monthly medical bills estimate",
            "monthly_medical_bills": "Monthly medical bills amount ($)",
            "retirement_extra_expenses": "Extra expenses in retirement (vacations, etc.)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "birthdate": forms.DateInput(
                attrs={"class": INPUT_CLASSES}, format="%m/%d/%Y"
            ),
            "retirement_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "add_healthcare": forms.CheckboxInput(),
            "include_pre_medicare_insurance": forms.CheckboxInput(),
            "add_medical_bills": forms.CheckboxInput(),
            "monthly_medical_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "retirement_extra_expenses": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
        }


class SavingsInputsForm(forms.ModelForm):
    """Class to contain all pertinent savings information"""

    def clean(self):
        cleaned_data = super().clean()
        use_time_period = cleaned_data.get("use_time_period", False)
        time_period_mode = cleaned_data.get("time_period_mode")
        start_age_yrs = cleaned_data.get("period_start_age_yrs")
        start_age_mos = cleaned_data.get("period_start_age_mos")
        end_age_yrs = cleaned_data.get("period_end_age_yrs")
        end_age_mos = cleaned_data.get("period_end_age_mos")

        if not use_time_period:
            cleaned_data["time_period_mode"] = None
            cleaned_data["period_start_age_yrs"] = None
            cleaned_data["period_start_age_mos"] = None
            cleaned_data["period_end_age_yrs"] = None
            cleaned_data["period_end_age_mos"] = None
            return cleaned_data

        if not time_period_mode:
            self.add_error(
                "time_period_mode",
                "Select how this savings assumption should be time-scoped.",
            )
            return cleaned_data

        start_months = None
        end_months = None
        if start_age_yrs is not None or start_age_mos is not None:
            start_months = (int(start_age_yrs or 0) * 12) + int(start_age_mos or 0)
        if end_age_yrs is not None or end_age_mos is not None:
            end_months = (int(end_age_yrs or 0) * 12) + int(end_age_mos or 0)

        if time_period_mode in {"from", "during"} and start_months is None:
            self.add_error(
                "period_start_age_yrs",
                "Enter a start age (years/months) for this time period.",
            )
        if time_period_mode in {"until", "during"} and end_months is None:
            self.add_error(
                "period_end_age_yrs",
                "Enter an end age (years/months) for this time period.",
            )
        if (
            time_period_mode == "during"
            and start_months is not None
            and end_months is not None
            and end_months <= start_months
        ):
            self.add_error(
                "period_end_age_yrs",
                "End age must be later than start age for 'Use this during'.",
            )

        return cleaned_data

    class Meta:
        model = SavingsInputsModel
        fields = [
            "is_active",
            "use_time_period",
            "time_period_mode",
            "period_start_age_yrs",
            "period_start_age_mos",
            "period_end_age_yrs",
            "period_end_age_mos",
            "base_savings",
            "base_saved_per_mo",
            "base_savings_per_yr_increase",
            "savings_lower_limit",
            "base_monthly_bills",
            "interest_rate_per_yr",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "use_time_period": "Only use these assumptions for a given time period",
            "time_period_mode": "Time period mode",
            "period_start_age_yrs": "Start age (years)",
            "period_start_age_mos": "Start age (months)",
            "period_end_age_yrs": "End age (years)",
            "period_end_age_mos": "End age (months)",
            "base_savings": "Current savings account",
            "base_saved_per_mo": "Savings per month",
            "base_savings_per_yr_increase": "Yearly savings contribution increase (%)",
            "savings_lower_limit": "The lowest amount of savings before you fully use retirement",
            "base_monthly_bills": "Usual monthly expenses (excluding rent, car, other terminal payments)",
            "interest_rate_per_yr": "Interest rate (%) - Leave blank to use Rates form default",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "use_time_period": forms.CheckboxInput(),
            "time_period_mode": forms.Select(attrs={"class": INPUT_CLASSES}),
            "period_start_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "period_start_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "period_end_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "period_end_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_saved_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_savings_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "savings_lower_limit": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_monthly_bills": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "interest_rate_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
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
            "reg_pmt_amt",
            "pmt_freq_mos",
            "recurring_purchase",
            "recurring_timeframe",
            "recurring_length",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "pmt_name": "Extra payment name",
            "pmt_start_age_yrs": "Extra payment start age in years",
            "pmt_start_age_mos": "Extra payment start age months",
            "pmt_length_yrs": "Extra payment length in years",
            "pmt_length_mos": "Extra payment length in months",
            "down_pmt": "Extra payment down payment",
            "reg_pmt_amt": "Extra payment monthly payment",
            "pmt_freq_mos": "Extra payment frequency in months",
            "recurring_purchase": "Will this be purchased again?",
            "recurring_timeframe": "How often will this be purchased (in months)",
            "recurring_length": "How many times will this purchase repeat?",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "pmt_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "pmt_start_age_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_start_age_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_length_yrs": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_length_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "down_pmt": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "reg_pmt_amt": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "pmt_freq_mos": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "recurring_purchase": forms.CheckboxInput(),
            "recurring_timeframe": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "recurring_length": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }


class RetirementInputsForm(forms.ModelForm):
    """Class to contain all pertinent financial information"""

    class Meta:
        model = RetirementInputsModel
        fields = [
            "is_active",
            "retirement_type",
            "base_retirement",
            "base_retirement_per_mo",
            "base_retirement_per_yr_increase",
            "interest_rate_per_yr",
            "use_conservative_rates",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "retirement_type": "Retirement Type",
            "base_retirement": "Current retirement amount",
            "base_retirement_per_mo": "Monthly retirement contributions",
            "base_retirement_per_yr_increase": "Yearly retirement contribution increase ($)",
            "interest_rate_per_yr": "Interest rate (%) - Leave blank to use Rates form default",
            "use_conservative_rates": "Decrease interest rate as I get older",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "retirement_type": forms.Select(attrs={"class": INPUT_CLASSES}),
            "base_retirement": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_mo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "base_retirement_per_yr_increase": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "interest_rate_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "use_conservative_rates": forms.CheckboxInput(),
        }


class RatesInputsForm(forms.ModelForm):
    """Class to contain all pertinent financial information"""

    class Meta:
        model = RatesInputsModel
        fields = [
            "is_active",
            "base_rf_interest_per_yr",
            "base_mkt_interest_per_yr",
            "base_inflation_per_yr",
        ]
        labels = {
            "is_active": "Use this for calculations",
            "base_rf_interest_per_yr": "Assumed savings account interest rate (%)",
            "base_mkt_interest_per_yr": "Assumed retirement interest rate (%)",
            "base_inflation_per_yr": "Assumed inflation per year (%)",
        }
        widgets = {
            "is_active": forms.CheckboxInput(),
            "base_rf_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_mkt_interest_per_yr": forms.NumberInput(
                attrs={"class": INPUT_CLASSES}
            ),
            "base_inflation_per_yr": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
        }
