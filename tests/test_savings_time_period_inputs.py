"""Tests for savings time-period model/form integration helpers."""

from datetime import date
import re
from types import SimpleNamespace


from pages.base_scenario import BaseScenario
from pages.forms import SavingsInputsForm
from pages.models import GeneralInputsModel, RatesInputsModel, SavingsInputsModel
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

    savings_inputs_dict, base_inputs = build_savings_inputs_dict(
        [base_row_a, base_row_b]
    )

    assert savings_inputs_dict is None
    assert len(base_inputs) == 2


# Having only scoped savings rows (no all-time base row) should be rejected as incomplete coverage.
def test_build_savings_inputs_dict_rejects_only_scoped_rows():
    scoped_row = SimpleNamespace(
        use_time_period=True,
        time_period_mode="until",
        period_start_age_yrs=None,
        period_start_age_mos=None,
        period_end_age_yrs=60,
        period_end_age_mos=0,
        base_savings=10000.0,
        base_saved_per_mo=800.0,
        base_savings_per_yr_increase=0.0,
        savings_lower_limit=0.0,
        base_monthly_bills=1800.0,
        interest_rate_per_yr=None,
    )

    savings_inputs_dict, base_inputs = build_savings_inputs_dict([scoped_row])

    assert savings_inputs_dict is None
    assert len(base_inputs) == 0


# Calculations should show an incomplete coverage error when savings rows are active but no all-time base row exists.
def test_calculations_shows_incomplete_coverage_for_only_scoped_rows(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-missing-coverage", password="pass1234"
    )
    client.force_login(user)

    GeneralInputsModel.objects.create(
        created_by=user,
        is_active=True,
        birthdate=date(1990, 1, 1),
        retirement_age_yrs=65,
        retirement_age_mos=0,
        add_healthcare=False,
        include_pre_medicare_insurance=False,
        add_medical_bills=False,
        monthly_medical_bills=0,
        retirement_extra_expenses=0,
    )
    RatesInputsModel.objects.create(
        created_by=user,
        is_active=True,
        base_rf_interest_per_yr=2.0,
        base_mkt_interest_per_yr=7.0,
        base_inflation_per_yr=3.0,
    )
    SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="until",
        period_end_age_yrs=60,
        period_end_age_mos=0,
        base_savings=15000,
        base_saved_per_mo=700,
        base_savings_per_yr_increase=1,
        savings_lower_limit=1000,
        base_monthly_bills=2100,
    )

    response = client.get("/calculations")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Categories With Incomplete Time Coverage" in html
    assert "Savings" in html
    assert (
        'Savings time periods do not cover all ages. Add one active scenario to cover all ages, or use the current savings scenario and select "Use for all time periods" to cover all ages'
        in html
    )
    assert "Categories Missing Active Scenarios" not in html


# Calculations should show a missing scenario error when there are no active savings rows.
def test_calculations_shows_missing_savings_when_no_active_savings_rows(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-no-scenario", password="pass1234"
    )
    client.force_login(user)

    GeneralInputsModel.objects.create(
        created_by=user,
        is_active=True,
        birthdate=date(1990, 1, 1),
        retirement_age_yrs=65,
        retirement_age_mos=0,
        add_healthcare=False,
        include_pre_medicare_insurance=False,
        add_medical_bills=False,
        monthly_medical_bills=0,
        retirement_extra_expenses=0,
    )
    RatesInputsModel.objects.create(
        created_by=user,
        is_active=True,
        base_rf_interest_per_yr=2.0,
        base_mkt_interest_per_yr=7.0,
        base_inflation_per_yr=3.0,
    )

    response = client.get("/calculations")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Categories Missing Active Scenarios" in html
    assert "Savings" in html
    assert "Please activate one scenario" in html
    assert "Categories With Incomplete Time Coverage" not in html


def _field_wrapper_classes(html: str, wrapper_id: str) -> str:
    match = re.search(
        rf'<div class="([^"]*)" id="{wrapper_id}"',
        html,
    )
    assert match is not None
    return match.group(1)


def _checkbox_tag(html: str, checkbox_id: str) -> str:
    match = re.search(rf'<input[^>]*id="{checkbox_id}"[^>]*>', html)
    assert match is not None
    return match.group(0)


# Savings period fields should be hidden by default on create when use_time_period is unchecked.
def test_savings_create_hides_time_period_fields_by_default(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-create", password="pass1234"
    )
    client.force_login(user)

    response = client.get("/savings/create/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Use for all time periods" in html
    assert "Use this until" in html
    assert "Use this during" in html
    assert "Use this from" in html
    assert "Time period age range" in html
    assert "checked" in _checkbox_tag(html, "time-period-all")
    assert "checked" not in _checkbox_tag(html, "time-period-until")
    assert "checked" not in _checkbox_tag(html, "time-period-during")
    assert "checked" not in _checkbox_tag(html, "time-period-from")
    assert "d-none" in _field_wrapper_classes(html, "savings-time-period-date-header")
    assert "d-none" in _field_wrapper_classes(html, "time-period-mode-field")
    assert "d-none" in _field_wrapper_classes(html, "period-start-age-yrs-field")
    assert "d-none" in _field_wrapper_classes(html, "period-end-age-yrs-field")


# Savings period fields should be visible on edit when use_time_period is enabled.
def test_savings_edit_shows_time_period_fields_when_enabled(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-edit", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="during",
        period_start_age_yrs=50,
        period_start_age_mos=0,
        period_end_age_yrs=60,
        period_end_age_mos=0,
        base_savings=10000,
        base_saved_per_mo=500,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2000,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "checked" not in _checkbox_tag(html, "time-period-all")
    assert "checked" not in _checkbox_tag(html, "time-period-until")
    assert "checked" in _checkbox_tag(html, "time-period-during")
    assert "checked" not in _checkbox_tag(html, "time-period-from")
    assert "d-none" not in _field_wrapper_classes(
        html, "savings-time-period-date-header"
    )
    assert "d-none" in _field_wrapper_classes(html, "time-period-mode-field")
    assert "d-none" not in _field_wrapper_classes(html, "period-start-age-yrs-field")
    assert "d-none" not in _field_wrapper_classes(html, "period-end-age-yrs-field")
    assert "border-start" in _field_wrapper_classes(html, "period-start-age-yrs-field")


# Selecting "Use this until" should show only end-age fields on edit.
def test_savings_edit_until_shows_end_fields_only(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-edit-until", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="until",
        period_end_age_yrs=62,
        period_end_age_mos=0,
        base_savings=10000,
        base_saved_per_mo=500,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2000,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "checked" in _checkbox_tag(html, "time-period-until")
    assert "d-none" in _field_wrapper_classes(html, "period-start-age-yrs-field")
    assert "d-none" not in _field_wrapper_classes(html, "period-end-age-yrs-field")


# Selecting "Use this from" should show only start-age fields on edit.
def test_savings_edit_from_shows_start_fields_only(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-edit-from", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="from",
        period_start_age_yrs=48,
        period_start_age_mos=0,
        base_savings=10000,
        base_saved_per_mo=500,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2000,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "checked" in _checkbox_tag(html, "time-period-from")
    assert "d-none" not in _field_wrapper_classes(html, "period-start-age-yrs-field")
    assert "d-none" in _field_wrapper_classes(html, "period-end-age-yrs-field")


# --- base_savings visibility for from/during modes ---


# "from" mode form should be valid even when base_savings is omitted.
def test_savings_form_from_mode_valid_without_base_savings():
    form_data = _valid_form_data() | {
        "time_period_mode": "from",
        "period_start_age_yrs": 45,
        "period_start_age_mos": 0,
        "period_end_age_yrs": None,
        "period_end_age_mos": None,
        "base_savings": "",
    }
    form = SavingsInputsForm(data=form_data)
    assert form.is_valid(), form.errors


# "during" mode form should be valid even when base_savings is omitted.
def test_savings_form_during_mode_valid_without_base_savings():
    form_data = _valid_form_data() | {
        "time_period_mode": "during",
        "base_savings": "",
    }
    form = SavingsInputsForm(data=form_data)
    assert form.is_valid(), form.errors


# "from" mode should clean base_savings to None even when a value is provided.
def test_savings_form_from_mode_clears_base_savings():
    form_data = _valid_form_data() | {
        "time_period_mode": "from",
        "period_start_age_yrs": 45,
        "period_start_age_mos": 0,
        "period_end_age_yrs": None,
        "period_end_age_mos": None,
        "base_savings": 25000,
    }
    form = SavingsInputsForm(data=form_data)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["base_savings"] is None


# "during" mode should clean base_savings to None even when a value is provided.
def test_savings_form_during_mode_clears_base_savings():
    form_data = _valid_form_data() | {
        "time_period_mode": "during",
        "base_savings": 25000,
    }
    form = SavingsInputsForm(data=form_data)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["base_savings"] is None


# "all time periods" mode (use_time_period=False) requires base_savings.
def test_savings_form_all_mode_requires_base_savings():
    form_data = _valid_form_data() | {"use_time_period": False, "base_savings": ""}
    form = SavingsInputsForm(data=form_data)
    assert not form.is_valid()
    assert "base_savings" in form.errors


# "until" mode requires base_savings since it starts at the beginning.
def test_savings_form_until_mode_requires_base_savings():
    form_data = _valid_form_data() | {
        "time_period_mode": "until",
        "period_start_age_yrs": None,
        "period_start_age_mos": None,
        "period_end_age_yrs": 62,
        "period_end_age_mos": 0,
        "base_savings": "",
    }
    form = SavingsInputsForm(data=form_data)
    assert not form.is_valid()
    assert "base_savings" in form.errors


# "from" form edit page should render base_savings field wrapper with d-none class.
def test_savings_edit_from_hides_base_savings_field(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-from-hide", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="from",
        period_start_age_yrs=50,
        period_start_age_mos=0,
        base_savings=None,
        base_saved_per_mo=600,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "d-none" in _field_wrapper_classes(html, "base-savings-field")


# "during" form edit page should render base_savings field wrapper with d-none class.
def test_savings_edit_during_hides_base_savings_field(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-during-hide", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="during",
        period_start_age_yrs=45,
        period_start_age_mos=0,
        period_end_age_yrs=60,
        period_end_age_mos=0,
        base_savings=None,
        base_saved_per_mo=600,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "d-none" in _field_wrapper_classes(html, "base-savings-field")


# "until" form edit page should show base_savings field (it applies from the start).
def test_savings_edit_until_shows_base_savings_field(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="savings-until-show", password="pass1234"
    )
    savings = SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="until",
        period_end_age_yrs=62,
        period_end_age_mos=0,
        base_savings=20000,
        base_saved_per_mo=600,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get(f"/savings/{savings.pk}/edit/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "d-none" not in _field_wrapper_classes(html, "base-savings-field")


# Dashboard card should not show "Current savings account" for "from" scenarios.
def test_savings_dashboard_hides_base_savings_for_from_scenario(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-from-card", password="pass1234"
    )
    SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="from",
        period_start_age_yrs=50,
        period_start_age_mos=0,
        base_savings=None,
        base_saved_per_mo=700,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get("/savings/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Current savings account" not in html


# Dashboard card should not show "Current savings account" for "during" scenarios.
def test_savings_dashboard_hides_base_savings_for_during_scenario(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-during-card", password="pass1234"
    )
    SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="during",
        period_start_age_yrs=45,
        period_start_age_mos=0,
        period_end_age_yrs=60,
        period_end_age_mos=0,
        base_savings=None,
        base_saved_per_mo=700,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get("/savings/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Current savings account" not in html


# Dashboard card should show "Current savings account" for "until" scenarios.
def test_savings_dashboard_shows_base_savings_for_until_scenario(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-until-card", password="pass1234"
    )
    SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=True,
        time_period_mode="until",
        period_end_age_yrs=62,
        period_end_age_mos=0,
        base_savings=20000,
        base_saved_per_mo=700,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get("/savings/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Current savings account" in html


# Dashboard card should show "Current savings account" for all-time scenarios.
def test_savings_dashboard_shows_base_savings_for_all_time_scenario(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="savings-all-card", password="pass1234"
    )
    SavingsInputsModel.objects.create(
        created_by=user,
        is_active=True,
        use_time_period=False,
        base_savings=15000,
        base_saved_per_mo=700,
        base_savings_per_yr_increase=2,
        savings_lower_limit=1000,
        base_monthly_bills=2500,
    )
    client.force_login(user)

    response = client.get("/savings/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Current savings account" in html


# A "from" period should not reset savings; it should inherit the running balance.
def test_from_period_savings_is_continuous_across_transition():
    base_assumptions = {
        "birthdate": date(1990, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0,
        "base_savings": 10000.0,
        "base_saved_per_mo": 500.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "payment_items": [],
        "retirement_accounts": [],
        "ss_incl": False,
        "base_rf_interest_per_yr": 0.0,
        "base_mkt_interest_per_yr": 7.0,
        "base_inflation_per_yr": 0.0,
    }
    baseline_scenario = BaseScenario(assumptions=base_assumptions)
    start_age_yrs = baseline_scenario.age_by_year_list[0]
    start_age_mos = baseline_scenario.age_by_month_list[0]
    transition_age_yrs = start_age_yrs + (1 if start_age_mos == 11 else 0)
    transition_age_mos = (start_age_mos + 1) % 12

    assumptions = base_assumptions | {
        "savings_time_periods": [
            {
                "base_saved_per_mo": 800.0,
                "base_monthly_bills": 0.0,
                "start_age_yrs": transition_age_yrs,
                "start_age_mos": transition_age_mos,
            }
        ],
    }
    scenario = BaseScenario(assumptions=assumptions)
    savings_list = scenario.savings_retirement_account_list[0]

    # Find the index where age transitions to the first future month.
    transition_index = next(
        i
        for i, (y, m) in enumerate(
            zip(scenario.age_by_year_list, scenario.age_by_month_list)
        )
        if y == transition_age_yrs and m == transition_age_mos
    )

    before = savings_list[transition_index - 1]
    at_transition = savings_list[transition_index]

    # Savings must not drop or jump discontinuously; the "from" period picks up
    # from whatever balance accumulated, not from a stored base_savings value.
    assert at_transition >= before or abs(at_transition - before) < 1.0
