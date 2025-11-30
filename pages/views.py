import logging

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from . import stochastic_finances_func
from .forms import (
    GeneralInputsForm,
    PaymentsInputsForm,
    RatesInputsForm,
    RetirementInputsForm,
    SavingsInputsForm,
)
from .full_descriptions import var_descriptions
from .models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)
from .utils import model_to_dict

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AlertsPageView(TemplateView):
    template_name = "pages/alerts.html"


class ButtonsPageView(TemplateView):
    template_name = "pages/buttons.html"


class BlankPageView(TemplateView):
    template_name = "pages/blank.html"


@login_required
def general_inputs_dashboard(request):
    general_inputs_models = GeneralInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "pages/general_inputs.html",
        {"general_inputs": general_inputs_models},
    )


@login_required
def general_inputs_create(request):
    """This will validate/create a new general inputs item"""
    logger.debug("Creating general inputs")
    if request.method == "POST":
        logger.debug("POST request")
        # print(f"{request.POST =}")
        form = GeneralInputsForm(request.POST)
        # for field in form:
        # print(field)

        if form.is_valid():
            # print("Valid form")
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/general/")

        else:
            # print("Not a valid form")
            # for field in form:
            # print(field)
            return render(
                request,
                "pages/inputs_create.html",
                {
                    "form": form,
                    "descriptions": var_descriptions,
                    "title": "Create New General Inputs",
                },
            )

    else:
        logger.debug("GET request")
        form = GeneralInputsForm()
        # print(form)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Create New General Inputs",
        },
    )


@login_required
def general_inputs_edit(request, pk):
    """This will edit a general inputs item"""
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = GeneralInputsForm(request.POST, instance=general_inputs)

        if form.is_valid():
            form.save()

            return redirect("general_inputs_dashboard")
    else:
        form = GeneralInputsForm(instance=general_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit General Inputs",
        },
    )


@login_required
def general_inputs_delete(request, pk):
    general_inputs = get_object_or_404(
        GeneralInputsModel, pk=pk, created_by=request.user
    )
    general_inputs.delete()

    return redirect("general_inputs_dashboard")


@login_required
def savings_inputs_dashboard(request):
    savings_inputs_models = SavingsInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "pages/savings_inputs.html",
        {"savings_inputs": savings_inputs_models},
    )


@login_required
def savings_inputs_create(request):
    """This will validate/create a new savings inputs item"""
    if request.method == "POST":
        form = SavingsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/savings/")
    else:
        form = SavingsInputsForm()

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "New Savings Inputs",
        },
    )


@login_required
def savings_inputs_edit(request, pk):
    """This will edit a savings inputs item"""
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = SavingsInputsForm(request.POST, instance=savings_inputs)

        if form.is_valid():
            form.save()

            return redirect("/savings/")
    else:
        form = SavingsInputsForm(instance=savings_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit Savings Inputs",
        },
    )


@login_required
def savings_inputs_delete(request, pk):
    savings_inputs = get_object_or_404(
        SavingsInputsModel, pk=pk, created_by=request.user
    )
    savings_inputs.delete()

    return redirect("savings_inputs_dashboard")


@login_required
def payments_inputs_dashboard(request):
    payments_inputs_models = PaymentsInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "pages/payments_inputs.html",
        {"payments_inputs": payments_inputs_models},
    )


@login_required
def payments_inputs_create(request):
    """This will validate/create a new payments inputs item"""
    if request.method == "POST":
        form = PaymentsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/payments/")
    else:
        form = PaymentsInputsForm()

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "New Payments Inputs",
        },
    )


@login_required
def payments_inputs_edit(request, pk):
    """This will edit a payments inputs item"""
    payments_inputs = get_object_or_404(
        PaymentsInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = PaymentsInputsForm(request.POST, instance=payments_inputs)

        if form.is_valid():
            form.save()

            return redirect("/payments/")
    else:
        form = PaymentsInputsForm(instance=payments_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit payments Inputs",
        },
    )


@login_required
def payments_inputs_delete(request, pk):
    payments_inputs = get_object_or_404(
        PaymentsInputsModel, pk=pk, created_by=request.user
    )
    payments_inputs.delete()

    return redirect("payments_inputs_dashboard")


@login_required
def retirement_inputs_dashboard(request):
    retirement_inputs_models = RetirementInputsModel.objects.filter(
        created_by=request.user
    )

    return render(
        request,
        "pages/retirement_inputs.html",
        {"retirement_inputs": retirement_inputs_models},
    )


@login_required
def retirement_inputs_create(request):
    """This will validate/create a new retirement inputs item"""
    if request.method == "POST":
        form = RetirementInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/retirement/")
    else:
        form = RetirementInputsForm()

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "New Retirement Inputs",
        },
    )


@login_required
def retirement_inputs_edit(request, pk):
    """This will edit a retirement inputs item"""
    retirement_inputs = get_object_or_404(
        RetirementInputsModel, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        form = RetirementInputsForm(request.POST, instance=retirement_inputs)

        if form.is_valid():
            form.save()

            return redirect("/retirement/")
    else:
        form = RetirementInputsForm(instance=retirement_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit retirement Inputs",
        },
    )


@login_required
def retirement_inputs_delete(request, pk):
    retirement_inputs = get_object_or_404(
        RetirementInputsModel, pk=pk, created_by=request.user
    )
    retirement_inputs.delete()

    return redirect("retirement_inputs_dashboard")


@login_required
def rates_inputs_dashboard(request):
    rates_inputs_models = RatesInputsModel.objects.filter(created_by=request.user)

    return render(
        request,
        "pages/rates_inputs.html",
        {"rates_inputs": rates_inputs_models},
    )


@login_required
def rates_inputs_create(request):
    """This will validate/create a new rates inputs item"""
    if request.method == "POST":
        form = RatesInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return redirect("/rates/")
    else:
        form = RatesInputsForm()

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "New rates Inputs",
        },
    )


@login_required
def rates_inputs_edit(request, pk):
    """This will edit a rates inputs item"""
    rates_inputs = get_object_or_404(RatesInputsModel, pk=pk, created_by=request.user)

    if request.method == "POST":
        form = RatesInputsForm(request.POST, instance=rates_inputs)

        if form.is_valid():
            form.save()

            return redirect("/rates/")
    else:
        form = RatesInputsForm(instance=rates_inputs)

    return render(
        request,
        "pages/inputs_create.html",
        {
            "form": form,
            "descriptions": var_descriptions,
            "title": "Edit rates Inputs",
        },
    )


@login_required
def rates_inputs_delete(request, pk):
    rates_inputs = get_object_or_404(RatesInputsModel, pk=pk, created_by=request.user)
    rates_inputs.delete()

    return redirect("rates_inputs_dashboard")


@login_required
def calculations(request):
    """This will run the financial calculations"""
    if request.method == "POST":
        print("Post request")

    else:
        print("Get request")
        bad_active_dict = {}
        general_inputs_model = GeneralInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if len(general_inputs_model) == 1:
            general_inputs_dict = model_to_dict(general_inputs_model[0], "general")
            # print(f"{general_inputs_dict =}")
        else:
            bad_active_dict["General"] = len(general_inputs_model)

        # print(f"{general_inputs_dict = }")

        savings_inputs_model = SavingsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if len(savings_inputs_model) == 1:
            savings_inputs_dict = model_to_dict(savings_inputs_model[0], "savings")
            # print(f"{savings_inputs_dict =}")
        else:
            bad_active_dict["Savings"] = len(savings_inputs_model)

        # Non-base bills
        payments_inputs_model = PaymentsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        payments_list = []
        for payment in payments_inputs_model:
            print(f'Payment: {model_to_dict(payment, "payments")}')
            payments_list.append(model_to_dict(payment, "payments"))

        print("")
        print(f"{payments_list = }")

        # Retirement
        retirement_inputs_model = RetirementInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        retirement_accts_list = []
        # if len(retirement_inputs_model) == 1:
        #     retirement_inputs_dict = model_to_dict(
        #         retirement_inputs_model[0], "retirement"
        #     )
        #     print(f"{retirement_inputs_dict =}")

        for retirement in retirement_inputs_model:
            print(f'Retirement: {model_to_dict(retirement, "retirement")}')
            retirement_accts_list.append(model_to_dict(retirement, "retirement"))

        print("")
        print(f"{retirement_accts_list = }")
        # else:
        #     bad_active_dict["Retirement"] = len(retirement_inputs_model)

        rates_inputs_model = RatesInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        if len(rates_inputs_model) == 1:
            rates_inputs_dict = model_to_dict(rates_inputs_model[0], "rates")
            # print(f"{rates_inputs_dict =}")
        else:
            bad_active_dict["Rates"] = len(rates_inputs_model)
        if bad_active_dict:
            print("There were some bad active inputs")
            # Separate the errors into two categories
            missing_scenarios = {k: v for k, v in bad_active_dict.items() if v == 0}
            multiple_scenarios = {k: v for k, v in bad_active_dict.items() if v > 1}

            return render(
                request,
                "pages/non_active.html",
                {
                    "missing_scenarios": missing_scenarios,
                    "multiple_scenarios": multiple_scenarios,
                },
            )

    full_dict = {
        **{"name": "Test Scenario"},
        **general_inputs_dict,
        **savings_inputs_dict,
        **{"payment_items": payments_list},
        **{"retirement_accounts": retirement_accts_list},
        **rates_inputs_dict,
    }

    print(f"full_dict is {full_dict}")
    # print(f'base_bills is {full_dict['base_monthly_bills']}')

    (total_savings_df, total_retirement_df) = stochastic_finances_func.main(full_dict)

    # Generate values for cards

    ####
    # Build list of avg retirement columns that exist (used throughout)
    ####

    avg_retirement_columns = [
        col for col in total_retirement_df.columns if col.startswith("avg_")
    ]

    ####
    # Probability of having enough money through death
    ####

    # print("Total_savings_df:")
    # print(total_savings_df.tail())

    death_age = 110
    death_months = 0

    # Build list of columns to drop for death calculation
    death_cols_to_drop = ["avg", "account_type", "account_0"]
    death_cols_to_drop.extend(avg_retirement_columns)

    total_all_at_death = (
        pd.concat(
            [
                total_savings_df.loc[
                    lambda df: (df.age_yrs == death_age) & (df.age_mos == death_months)
                ],
                total_retirement_df.loc[
                    lambda df: (df.age_yrs == death_age) & (df.age_mos == death_months)
                ],
            ]
        )
        .drop(
            columns=death_cols_to_drop
        )  # Don't want to include base account - not stochastic
        .groupby(["age_yrs", "age_mos"])
        .sum()
    )

    print("total_all_at_death")
    print(total_all_at_death.head())

    negative_count = (
        (total_all_at_death.reset_index().drop(columns=["age_yrs", "age_mos"]) < 0)
        .sum(axis=1)
        .iat[0]
    )

    print(f"{negative_count = }")

    total_scenarios_count = (
        total_all_at_death.reset_index().drop(columns=["age_yrs", "age_mos"]).shape[1]
    )

    print(f"total scenarios is {total_scenarios_count}")

    ####
    # Average savings at retirement
    ####

    avg_savings_at_retirement = total_savings_df.loc[
        lambda df: (df.age_yrs == 65)  # general_inputs_dict["retirement_age_yrs"])
        & (df.age_mos == 0)  # general_inputs_dict["retirement_age_mos"])
    ]["avg"].iat[0]

    avg_savings_at_retirement_fmt = f"${float(avg_savings_at_retirement):,.0f}"

    ####
    # Average retirement at retirement
    ####

    retirement_at_retirement_row = total_retirement_df.loc[
        lambda df: (df.age_yrs == 65)  # general_inputs_dict["retirement_age_yrs"])
        & (df.age_mos == 0)  # general_inputs_dict["retirement_age_mos"])
    ]

    avg_retirement_at_retirement = sum(
        retirement_at_retirement_row[col].iat[0] for col in avg_retirement_columns
    )

    avg_retirement_at_retirement_fmt = f"${float(avg_retirement_at_retirement):,.0f}"

    print(f"{avg_retirement_at_retirement_fmt = }")

    ####
    # Get data for chart
    ####

    ages_for_chart = total_savings_df.loc[
        lambda df: (df.age_yrs % 5 == 0) & (df.age_mos == 0)
    ]["age_yrs"].to_list()

    print(f"{ages_for_chart = }")

    savings_for_chart = (
        total_savings_df.loc[lambda df: (df.age_yrs % 5 == 0) & (df.age_mos == 0)][
            "avg"
        ]
        .round()
        .to_list()
    )

    print(f"{savings_for_chart = }")

    # Create separate chart data for each retirement account type that exists
    chart_df = total_retirement_df.loc[
        lambda df: (df.age_yrs % 5 == 0) & (df.age_mos == 0)
    ]

    # Only create chart lists for columns that actually exist
    retirement_chart_data = {}

    if "avg_traditional_401k" in chart_df.columns:
        retirement_chart_data["traditional_401k_by_age"] = (
            chart_df["avg_traditional_401k"].round().to_list()
        )
        print(
            f"traditional_401k_for_chart = {retirement_chart_data['traditional_401k_by_age']}"
        )

    if "avg_traditional_ira" in chart_df.columns:
        retirement_chart_data["traditional_ira_by_age"] = (
            chart_df["avg_traditional_ira"].round().to_list()
        )
        print(
            f"traditional_ira_for_chart = {retirement_chart_data['traditional_ira_by_age']}"
        )

    if "avg_roth_401k" in chart_df.columns:
        retirement_chart_data["roth_401k_by_age"] = (
            chart_df["avg_roth_401k"].round().to_list()
        )
        print(f"roth_401k_for_chart = {retirement_chart_data['roth_401k_by_age']}")

    if "avg_roth_ira" in chart_df.columns:
        retirement_chart_data["roth_ira_by_age"] = (
            chart_df["avg_roth_ira"].round().to_list()
        )
        print(f"roth_ira_for_chart = {retirement_chart_data['roth_ira_by_age']}")

    ####
    # Get data for table
    ####

    savings_metrics_by_age_df = total_savings_df.loc[lambda df: df.age_mos == 0].assign(
        pct_15_savings=lambda df: df.drop(
            columns=["age_yrs", "age_mos", "avg", "account_type"]
        ).quantile(0.15, axis=1),
        pct_85_savings=lambda df: df.drop(
            columns=["age_yrs", "age_mos", "avg", "account_type"]
        ).quantile(0.85, axis=1),
        avg_savings=lambda df: df.avg,
    )[["age_yrs", "age_mos", "avg_savings", "pct_15_savings", "pct_85_savings"]]

    # Build list of columns to drop for retirement quantile calculations
    retirement_cols_to_drop = ["age_yrs", "age_mos", "account_type"]
    retirement_cols_to_drop.extend(
        [col for col in avg_retirement_columns if col in total_retirement_df.columns]
    )

    # Build list of avg columns to sum for avg_retirement
    retirement_avg_cols_to_sum = [
        col for col in avg_retirement_columns if col in total_retirement_df.columns
    ]

    retirement_metrics_by_age_df = total_retirement_df.loc[
        lambda df: df.age_mos == 0
    ].assign(
        pct_15_retirement=lambda df: df.drop(columns=retirement_cols_to_drop).quantile(
            0.15, axis=1
        ),
        pct_85_retirement=lambda df: df.drop(columns=retirement_cols_to_drop).quantile(
            0.85, axis=1
        ),
        avg_retirement=lambda df: df[retirement_avg_cols_to_sum].sum(axis=1)
        if retirement_avg_cols_to_sum
        else 0,
    )[
        [
            "age_yrs",
            "age_mos",
            "avg_retirement",
            "pct_15_retirement",
            "pct_85_retirement",
        ]
    ]

    # Build list of columns to drop for total metrics calculations
    total_cols_to_drop = ["avg", "account_type"]
    total_cols_to_drop.extend(
        [col for col in avg_retirement_columns if col in total_retirement_df.columns]
    )

    total_metrics_by_age_df = (
        (
            pd.concat(
                [
                    total_savings_df.loc[lambda df: df.age_mos == 0],
                    total_retirement_df.loc[lambda df: df.age_mos == 0],
                ]
            )
            .groupby(["age_yrs", "age_mos"])
            .sum()
        )
        .assign(
            pct_15_tot=lambda df: df.drop(columns=total_cols_to_drop).quantile(
                0.15, axis=1
            ),
            pct_85_tot=lambda df: df.drop(columns=total_cols_to_drop).quantile(
                0.85, axis=1
            ),
            avg_tot=lambda df: df.drop(columns=total_cols_to_drop).mean(axis=1),
        )
        .reset_index()
    )[["age_yrs", "age_mos", "avg_tot", "pct_15_tot", "pct_85_tot"]]

    print("Total metrics by age")
    print(total_metrics_by_age_df.head())

    all_metrics_combined_df = total_metrics_by_age_df.merge(
        savings_metrics_by_age_df, on=["age_yrs", "age_mos"], how="left"
    ).merge(retirement_metrics_by_age_df, on=["age_yrs", "age_mos"], how="left")

    print(all_metrics_combined_df.head())

    table_data = all_metrics_combined_df.to_dict(orient="records")

    # print(f"{table_data = }")

    # Build the context dictionary with only the retirement accounts that exist
    context = {
        "prob_of_positive": round(
            (1 - (negative_count / total_scenarios_count)) * 100, 0
        ),
        "avg_savings_at_retirement": avg_savings_at_retirement_fmt,
        "avg_retirement_at_retirement": avg_retirement_at_retirement_fmt,
        "age_labels": ages_for_chart,
        "savings_by_age": savings_for_chart,
        "y_axis_range": [x for x in range(0, 3_000_000, 250_000)],
        "table_data": table_data,
    }

    # Add retirement chart data only for accounts that exist
    context.update(retirement_chart_data)

    return render(
        request,
        "pages/calculations.html",
        context,
    )
