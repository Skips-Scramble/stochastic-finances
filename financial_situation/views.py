import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

import stochastic_finances_func

from .forms import EditFinancialSituation, NewFinancialSituation, NewTestCalcForm
from .models import FinancialInputs


def test_new_form(request):
    """Hello World!"""
    print("starting to run")
    if request.method == "POST":
        print("post method")
        form = NewTestCalcForm(request.POST)
        print("form defined as post")

        if form.is_valid():
            item = form.save(commit=False)
            item.next_year = item.current_savings_account * (
                1 + item.current_interest / 100
            )
            item.save()

            print("post form is valid")
            print(f"{form =}")
            print(
                f"next year's savings is {item.current_savings_account * (1+item.current_interest/100)}"
            )
            return render(
                request,
                "financial_situation/results.html",
                {
                    "title": "Test Page",
                    "results": f"next year's savings is {item.current_savings_account * (1+item.current_interest/100)}",
                },
            )
    else:
        form = NewTestCalcForm()
        print("form defined as get")

    print("now returning")

    return render(
        request,
        "financial_situation/form.html",
        {
            "form": form,
            "title": "New test item",
        },
    )


@login_required
def add_financial_situation(request):
    """Create a new financial situation"""
    if request.method == "POST":
        form = NewFinancialSituation(request.POST)
        if form.is_valid():
            input_dict_new = form.cleaned_data
            print(input_dict_new)
            FinancialInputs.objects.create(
                **form.cleaned_data,
                **{"input_dict": form.cleaned_data},
                **{"created_by": request.user, "created_at": datetime.now()},
            )
            input_dict_new["payment_items"] = [
                {
                    "item_name": input_dict_new["payment_1_item_name"],
                    "item_pmt_start_age_yrs": input_dict_new[
                        "payment_1_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": input_dict_new[
                        "payment_1_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": input_dict_new[
                        "payment_1_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": input_dict_new["payment_1_item_down_pmt"],
                    "item_monthly_pmt": input_dict_new["payment_1_item_monthly_pmt"],
                },
            ]
            print(f"input_dict new = {json.dumps(input_dict_new, indent=2)}")
            # del input_dict_new["created_by"]
            # del input_dict_new["created_at"]
            (total_savings_df, total_retirement_df) = stochastic_finances_func.main(
                input_dict_new
            )
            results_dict = {}
            for age in range(60, 100, 5):
                savings_at_age = total_savings_df.loc[
                    lambda df: (df.age_yrs == age) & (df.age_mos == 0)
                ]["average"].iat[0]

                retirement_at_age = total_retirement_df.loc[
                    lambda df: (df.age_yrs == age) & (df.age_mos == 0)
                ]["average"].iat[0]

                results_dict[age] = [
                    f"Average savings at age {age} is ${savings_at_age:,.0f}",
                    f"Average retirement at age {age} is ${retirement_at_age:,.0f}",
                ]

            print(val for val in results_dict.values())

            # item = form.save(commit=False)
            # item.created_by = request.user
            # item.save()

            return render(
                request,
                "financial_situation/results.html",
                {
                    "title": "Financial Results",
                    "results": results_dict,
                },
            )

    else:
        form = NewFinancialSituation()
    return render(
        request,
        "financial_situation/form.html",
        {
            "form": form,
            "title": "New Financial Situation",
        },
    )


@login_required
def edit(request, pk):
    financial_inputs = get_object_or_404(
        FinancialInputs, pk=pk, created_by=request.user
    )

    if request.method == "POST":
        print(f"The request.POST is: {request.POST}")
        form = EditFinancialSituation(
            request.POST, request.FILES, instance=financial_inputs
        )

        if form.is_valid():
            input_dict_new = form.cleaned_data
            print(input_dict_new)
            FinancialInputs.objects.create(
                **form.cleaned_data,
                **{"input_dict": form.cleaned_data},
                **{"created_by": request.user, "created_at": datetime.now()},
            )
            input_dict_new["payment_items"] = [
                {
                    "item_name": input_dict_new["payment_1_item_name"],
                    "item_pmt_start_age_yrs": input_dict_new[
                        "payment_1_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": input_dict_new[
                        "payment_1_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": input_dict_new[
                        "payment_1_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": input_dict_new["payment_1_item_down_pmt"],
                    "item_monthly_pmt": input_dict_new["payment_1_item_monthly_pmt"],
                },
            ]
            print(f"input_dict new = {json.dumps(input_dict_new, indent=2)}")
            # del input_dict_new["created_by"]
            # del input_dict_new["created_at"]
            (total_savings_df, total_retirement_df) = stochastic_finances_func.main(
                input_dict_new
            )
            results_dict = {}
            for age in range(60, 100, 5):
                savings_at_age = total_savings_df.loc[
                    lambda df: (df.age_yrs == age) & (df.age_mos == 0)
                ]["average"].iat[0]

                retirement_at_age = total_retirement_df.loc[
                    lambda df: (df.age_yrs == age) & (df.age_mos == 0)
                ]["average"].iat[0]

                results_dict[age] = [
                    f"Average savings at age {age} is ${savings_at_age:,.0f}",
                    f"Average retirement at age {age} is ${retirement_at_age:,.0f}",
                ]

            print(val for val in results_dict.values())

            # item = form.save(commit=False)
            # item.created_by = request.user
            # item.save()

            return render(
                request,
                "financial_situation/results.html",
                {
                    "title": "Financial Results",
                    "results": results_dict,
                },
            )
    else:
        form = EditFinancialSituation(instance=financial_inputs)

    return render(
        request,
        "financial_situation/form.html",
        {
            "form": form,
            "title": "Edit Financial Situation",
        },
    )
