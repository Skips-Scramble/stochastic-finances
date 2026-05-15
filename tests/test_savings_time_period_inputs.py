"""Tests for savings time-period model/form integration helpers."""

from types import SimpleNamespace

from pages.forms import SavingsInputsForm
from pages.utils import build_savings_inputs_dict


def _valid_form_data() -> dict:
    return {
        "is_active": True,
        "use_time_period": True,
        "time_period_mode": "during",
        "period_start_age_yrs": 45,
        "period_start_age_mos": 0,
        "period_end_age_yrs": 55,
        "period_end_age_mos": 0,
        "base_savings": 50000,
        "base_saved_per_mo": 1000,
        "base_savings_per_yr_increase": 2,
        "savings_lower_limit": 5000,
        "base_monthly_bills": 3000,
        "interest_rate_per_yr": "",
    }


# A "during" period should require the end age to be later than the start age.
def test_savings_inputs_form_rejects_non_increasing_during_range():
    form_data = _valid_form_data() | {
        "period_start_age_yrs": 55,
        "period_start_age_mos": 0,
        "period_end_age_yrs": 55,
        "period_end_age_mos": 0,
    }
    form = SavingsInputsForm(data=form_data)
    assert not form.is_valid()
    assert "period_end_age_yrs" in form.errors


# Disabling time periods should clear period-specific fields during form cleaning.
def test_savings_inputs_form_clears_time_period_fields_when_disabled():
    form_data = _valid_form_data() | {"use_time_period": False}
    form = SavingsInputsForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data["time_period_mode"] is None
    assert form.cleaned_data["period_start_age_yrs"] is None
    assert form.cleaned_data["period_end_age_yrs"] is None


# Building savings assumptions should include period rows while keeping one base row.
def test_build_savings_inputs_dict_includes_savings_time_periods():
    base_row = SimpleNamespace(
        use_time_period=False,
        time_period_mode=None,
        period_start_age_yrs=None,
        period_start_age_mos=None,
        period_end_age_yrs=None,
        period_end_age_mos=None,
        base_savings=10000.0,
        base_saved_per_mo=500.0,
        base_savings_per_yr_increase=0.0,
        savings_lower_limit=0.0,
        base_monthly_bills=2000.0,
        interest_rate_per_yr=None,
    )
    period_row = SimpleNamespace(
        use_time_period=True,
        time_period_mode="from",
        period_start_age_yrs=55,
        period_start_age_mos=0,
        period_end_age_yrs=None,
        period_end_age_mos=None,
        base_savings=10000.0,
        base_saved_per_mo=750.0,
        base_savings_per_yr_increase=0.0,
        savings_lower_limit=0.0,
        base_monthly_bills=3000.0,
        interest_rate_per_yr=None,
    )

    savings_inputs_dict, base_inputs = build_savings_inputs_dict([base_row, period_row])

    assert len(base_inputs) == 1
    assert savings_inputs_dict is not None
    assert savings_inputs_dict["base_saved_per_mo"] == 500.0
    assert savings_inputs_dict["savings_time_periods"] == [
        {
            "base_saved_per_mo": 750.0,
            "base_monthly_bills": 3000.0,
            "start_age_yrs": 55,
            "start_age_mos": 0,
        }
    ]


# Multiple non-period rows should be treated as invalid for calculations input selection.
def test_build_savings_inputs_dict_requires_exactly_one_base_row():
    base_row_a = SimpleNamespace(
        use_time_period=False,
        time_period_mode=None,
        period_start_age_yrs=None,
        period_start_age_mos=None,
        period_end_age_yrs=None,
        period_end_age_mos=None,
        base_savings=10000.0,
        base_saved_per_mo=500.0,
        base_savings_per_yr_increase=0.0,
        savings_lower_limit=0.0,
        base_monthly_bills=2000.0,
        interest_rate_per_yr=None,
    )
    base_row_b = SimpleNamespace(
        use_time_period=False,
        time_period_mode=None,
        period_start_age_yrs=None,
        period_start_age_mos=None,
        period_end_age_yrs=None,
        period_end_age_mos=None,
        base_savings=12000.0,
        base_saved_per_mo=600.0,
        base_savings_per_yr_increase=0.0,
        savings_lower_limit=0.0,
        base_monthly_bills=2200.0,
        interest_rate_per_yr=None,
    )

    savings_inputs_dict, base_inputs = build_savings_inputs_dict([base_row_a, base_row_b])

    assert savings_inputs_dict is None
    assert len(base_inputs) == 2
