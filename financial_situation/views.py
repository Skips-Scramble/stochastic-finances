import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import stochastic_finances_func
from financial_situation.utils import ensure_active_inputs, model_to_dict
from inputs.models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)


@login_required
def calculation(request):
    """This will run the financial calculations"""
    if request.method == "POST":
        print("Post request")

    else:
        print("Get request")
        bad_active_list = []
        general_inputs_model = GeneralInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if ensure_active_inputs(general_inputs_model, 1):
            general_inputs_dict = model_to_dict(general_inputs_model[0], "general")
            print(f"{general_inputs_dict =}")
        else:
            bad_active_list.append("General")

        savings_inputs_model = SavingsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )

        if ensure_active_inputs(savings_inputs_model, 1):
            savings_inputs_dict = model_to_dict(savings_inputs_model[0], "savings")
            print(f"{savings_inputs_dict =}")
        else:
            bad_active_list.append("Savings")

        payments_inputs_model = PaymentsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        payments_list = []
        for payment in payments_inputs_model:
            print(model_to_dict(payment, "payments"))
            payments_list.append(model_to_dict(payment, "payments"))
        print(f"{payments_list = }")

        retirement_inputs_model = RetirementInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        if ensure_active_inputs(retirement_inputs_model, 1):
            retirement_inputs_dict = model_to_dict(
                retirement_inputs_model[0], "retirement"
            )
            print(f"{retirement_inputs_dict =}")
        else:
            bad_active_list.append("Retirement")

        rates_inputs_model = RatesInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        if ensure_active_inputs(rates_inputs_model, 1):
            rates_inputs_dict = model_to_dict(rates_inputs_model[0], "rates")
            print(f"{rates_inputs_dict =}")
        else:
            bad_active_list.append("Rates")
        if bad_active_list:
            return render(
                request,
                "financial_situation/non_active.html",
                {
                    "errors": bad_active_list,
                },
            )

    full_dict = {
        **{"name": "Test Scenario"},
        **general_inputs_dict,
        **savings_inputs_dict,
        **{"payment_items": payments_list},
        **retirement_inputs_dict,
        **rates_inputs_dict,
    }

    print(f"full_dict is {full_dict}")
    # print(f'base_bills is {full_dict['base_monthly_bills']}')

    (total_savings_df, total_retirement_df, total_outputs_df) = (
        stochastic_finances_func.main(full_dict)
    )

    results_dict = {}
    for age in range(40, 105, 5):
        savings_at_age = total_savings_df.loc[
            lambda df: (df.age_yrs == age) & (df.age_mos == 0)
        ]["avg"].iat[0]

        retirement_at_age = total_retirement_df.loc[
            lambda df: (df.age_yrs == age) & (df.age_mos == 0)
        ]["avg"].iat[0]

        results_dict[age] = [
            f"Average savings at age {age} is ${savings_at_age:,.0f}",
            f"Average retirement at age {age} is ${retirement_at_age:,.0f}",
        ]
    print(f"{results_dict = }")
    print(val for val in results_dict.values())

    savings_retirement_fig = px.line(
        total_outputs_df, x="age_yrs", y="avg", color="account_type", height=600
    )
    savings_retirement_fig.update_xaxes(title_text="Age (years)", dtick=5)
    savings_retirement_fig.update_yaxes(title_text="Amount")
    savings_retirement_fig_html = savings_retirement_fig.to_html()

    table_view = (
        total_outputs_df[["age_yrs", "account_type", "avg"]]
        .pivot(index="age_yrs", columns="account_type", values="avg")
        .reset_index()
        # .to_html(
        #     classes="table table-hover table-primary table-striped table-bordered",
        #     columns=["age_yrs", "savings", "retirement", "total"],
        #     index=False,
        #     index_names=False,
        # )
    )

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(table_view.columns),
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[
                        table_view.age_yrs,
                        table_view.savings,
                        table_view.retirement,
                        table_view.total,
                    ],
                    fill_color="lavender",
                    align="left",
                ),
            )
        ],
    )

    # fig.show()

    return render(
        request,
        "financial_situation/calculations.html",
        {
            "chart": savings_retirement_fig_html,
            "table": fig.to_html(),
        },
    )
