import typing

inputs_by_model_dict = {
    "general": [
        "birthdate",
        "retirement_age_yrs",
        "retirement_age_mos",
        "add_healthcare",
        "include_pre_medicare_insurance",
        "add_medical_bills",
        "monthly_medical_bills",
        "retirement_extra_expenses",
    ],
    "savings": [
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
    ],
    "payments": [
        "pmt_name",
        "pmt_start_age_yrs",
        "pmt_start_age_mos",
        "pmt_length_yrs",
        "pmt_length_mos",
        "down_pmt",
        "reg_pmt_amt",
        "pmt_freq_mos",
        "recurring_purchase",
        "recurring_purchase_inf_adj",
        "recurring_timeframe",
        "recurring_length",
    ],
    "retirement": [
        "retirement_type",
        "base_retirement",
        "base_retirement_per_mo",
        "base_retirement_per_yr_increase",
        "use_conservative_rates",
    ],
    "rates": [
        "base_rf_interest_per_yr",
        "base_mkt_interest_per_yr",
        "base_inflation_per_yr",
    ],
}


def model_to_dict(active_inputs: typing.Any, model: str) -> dict[str, typing.Any]:
    """Convert a Django model instance to a dictionary"""
    model_dict: dict[str, typing.Any] = {}
    # print("~~~~~~~~~~~~~~~~~~")
    # print("let's get down to business")
    # print("~~~~~~~~~~~~~~~~~~~~~~~~")
    for field in active_inputs._meta.fields:
        # print(f"{field = }")
        # print(f"{field.name = }")
        if field.name in inputs_by_model_dict[model]:
            field_name = field.name
            field_value = getattr(active_inputs, field_name)
            model_dict[field_name] = field_value
    return model_dict


def ensure_active_inputs(active_inputs: typing.Any, expected_active: int) -> bool:
    """Functtion to ensure inputs are acceptable"""
    return len(active_inputs) == expected_active


def build_savings_inputs_dict(
    active_savings_inputs: typing.Iterable[typing.Any],
) -> tuple[dict[str, typing.Any] | None, list[typing.Any]]:
    """Build savings assumptions with optional period overrides.

    Returns (savings_inputs_dict, base_inputs). A valid payload requires exactly
    one non-time-period active savings input in ``base_inputs``.
    """
    active_inputs_list = list(active_savings_inputs)
    base_inputs = [
        item for item in active_inputs_list if not getattr(item, "use_time_period", False)
    ]
    if len(base_inputs) != 1:
        return None, base_inputs

    savings_inputs_dict = {
        field_name: getattr(base_inputs[0], field_name)
        for field_name in inputs_by_model_dict["savings"]
    }
    savings_inputs_dict["savings_time_periods"] = []

    for item in active_inputs_list:
        if not getattr(item, "use_time_period", False):
            continue

        time_period_dict: dict[str, typing.Any] = {
            "base_saved_per_mo": item.base_saved_per_mo,
            "base_monthly_bills": item.base_monthly_bills,
        }
        if item.period_start_age_yrs is not None or item.period_start_age_mos is not None:
            time_period_dict["start_age_yrs"] = int(item.period_start_age_yrs or 0)
            time_period_dict["start_age_mos"] = int(item.period_start_age_mos or 0)
        if item.period_end_age_yrs is not None or item.period_end_age_mos is not None:
            time_period_dict["end_age_yrs"] = int(item.period_end_age_yrs or 0)
            time_period_dict["end_age_mos"] = int(item.period_end_age_mos or 0)

        savings_inputs_dict["savings_time_periods"].append(time_period_dict)

    return savings_inputs_dict, base_inputs
