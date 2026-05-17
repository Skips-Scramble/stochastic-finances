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


def _age_to_months(age_yrs: int, age_mos: int) -> int:
    return (int(age_yrs or 0) * 12) + int(age_mos or 0)


def _period_bounds(item: typing.Any) -> tuple[int | None, int | None]:
    start = None
    end = None
    if (
        getattr(item, "period_start_age_yrs", None) is not None
        or getattr(item, "period_start_age_mos", None) is not None
    ):
        start = _age_to_months(
            getattr(item, "period_start_age_yrs", 0),
            getattr(item, "period_start_age_mos", 0),
        )
    if (
        getattr(item, "period_end_age_yrs", None) is not None
        or getattr(item, "period_end_age_mos", None) is not None
    ):
        end = _age_to_months(
            getattr(item, "period_end_age_yrs", 0),
            getattr(item, "period_end_age_mos", 0),
        )
    return start, end


def _scoped_rows_cover_all_ages(scoped_inputs: list[typing.Any]) -> bool:
    if not scoped_inputs:
        return False

    intervals: list[tuple[int | None, int | None]] = []
    for item in scoped_inputs:
        start, end = _period_bounds(item)
        if start is not None and end is not None and end <= start:
            return False
        intervals.append((start, end))

    intervals.sort(
        key=lambda interval: (
            interval[0] is not None,
            interval[0] if interval[0] is not None else -1,
            interval[1] is None,
            interval[1] if interval[1] is not None else 0,
        )
    )

    first_start, first_end = intervals[0]
    if first_start is not None:
        return False

    covered_until = first_end
    for start, end in intervals[1:]:
        if covered_until is None:
            return True

        effective_start = -1 if start is None else start
        if effective_start > covered_until:
            return False

        if end is None or (covered_until is not None and end > covered_until):
            covered_until = end

    return covered_until is None


def _scoped_anchor_row(scoped_inputs: list[typing.Any]) -> typing.Any | None:
    if not _scoped_rows_cover_all_ages(scoped_inputs):
        return None

    sorted_rows = sorted(
        scoped_inputs,
        key=lambda item: (
            getattr(item, "period_start_age_yrs", None) is not None
            or getattr(item, "period_start_age_mos", None) is not None,
            _age_to_months(
                getattr(item, "period_start_age_yrs", 0),
                getattr(item, "period_start_age_mos", 0),
            ),
        ),
    )
    anchor = sorted_rows[0]

    if getattr(anchor, "base_savings", None) is None:
        return None

    return anchor


def build_savings_inputs_dict(
    active_savings_inputs: typing.Iterable[typing.Any],
) -> tuple[dict[str, typing.Any] | None, list[typing.Any]]:
    """Build savings assumptions with optional period overrides.

    Returns (savings_inputs_dict, base_inputs).

    A valid payload is either:
    - Exactly one non-time-period active savings input, or
    - Fully covering time-scoped rows (no age gaps) with an anchor row that
      provides ``base_savings`` for initial balance.
    """
    active_inputs_list = list(active_savings_inputs)
    base_inputs = [
        item
        for item in active_inputs_list
        if not getattr(item, "use_time_period", False)
    ]
    scoped_inputs = [
        item for item in active_inputs_list if getattr(item, "use_time_period", False)
    ]

    if len(base_inputs) > 1:
        return None, base_inputs

    effective_base_inputs = base_inputs
    if len(base_inputs) == 0:
        anchor_row = _scoped_anchor_row(scoped_inputs)
        if anchor_row is None:
            return None, base_inputs
        effective_base_inputs = [anchor_row]

    savings_inputs_dict = {
        field_name: getattr(effective_base_inputs[0], field_name)
        for field_name in inputs_by_model_dict["savings"]
    }
    savings_inputs_dict["use_time_period"] = False
    savings_inputs_dict["time_period_mode"] = None
    savings_inputs_dict["period_start_age_yrs"] = None
    savings_inputs_dict["period_start_age_mos"] = None
    savings_inputs_dict["period_end_age_yrs"] = None
    savings_inputs_dict["period_end_age_mos"] = None
    savings_inputs_dict["savings_time_periods"] = []

    for item in scoped_inputs:
        time_period_dict: dict[str, typing.Any] = {
            "base_saved_per_mo": item.base_saved_per_mo,
            "base_monthly_bills": item.base_monthly_bills,
        }
        if (
            item.period_start_age_yrs is not None
            or item.period_start_age_mos is not None
        ):
            time_period_dict["start_age_yrs"] = int(item.period_start_age_yrs or 0)
            time_period_dict["start_age_mos"] = int(item.period_start_age_mos or 0)
        if item.period_end_age_yrs is not None or item.period_end_age_mos is not None:
            time_period_dict["end_age_yrs"] = int(item.period_end_age_yrs or 0)
            time_period_dict["end_age_mos"] = int(item.period_end_age_mos or 0)

        savings_inputs_dict["savings_time_periods"].append(time_period_dict)

    return savings_inputs_dict, effective_base_inputs
