import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

import stochastic_finances_func
from utils.get_field_values import model_to_dict

from .forms import (
    EditFinancialSituation,
    GeneralInputsForm,
    NewFinancialSituation,
    NewTestCalcForm,
    PaymentsInputsForm,
    RatesInputsForm,
    RetirementInputsForm,
    SavingsInputsForm,
)
from .models import (
    FinancialInputs,
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)


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


@login_required
def general_inputs_view(request):
    """This will validate/create a new general inputs item"""
    if request.method == "POST":
        form = GeneralInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return render(
                request,
                "core/index.html",
            )
    else:
        form = GeneralInputsForm()

    return render(
        request,
        "financial_situation/general_inputs.html",
        {
            "form": form,
            "title": "New General Inputs",
        },
    )


@login_required
def savings_inputs_view(request):
    """This will validate/create a new savings inputs item"""
    if request.method == "POST":
        form = SavingsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return render(
                request,
                "core/index.html",
            )
    else:
        form = SavingsInputsForm()

    return render(
        request,
        "financial_situation/savings_inputs.html",
        {
            "form": form,
            "title": "New Savings Inputs",
        },
    )


@login_required
def payments_inputs_view(request):
    """This will validate/create a new payments inputs item"""
    if request.method == "POST":
        form = PaymentsInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return render(
                request,
                "core/index.html",
            )
    else:
        form = PaymentsInputsForm()

    return render(
        request,
        "financial_situation/payments_inputs.html",
        {
            "form": form,
            "title": "New Payments Inputs",
        },
    )


@login_required
def retirement_inputs_view(request):
    """This will validate/create a new payments inputs item"""
    if request.method == "POST":
        form = RetirementInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return render(
                request,
                "core/index.html",
            )
    else:
        form = RetirementInputsForm()

    return render(
        request,
        "financial_situation/retirement_inputs.html",
        {
            "form": form,
            "title": "New Retirement Inputs",
        },
    )


@login_required
def rates_inputs_view(request):
    """This will validate/create a new payments inputs item"""
    if request.method == "POST":
        form = RatesInputsForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()

            return render(
                request,
                "core/index.html",
            )
    else:
        form = RatesInputsForm()

    return render(
        request,
        "financial_situation/rates_inputs.html",
        {
            "form": form,
            "title": "New Rates Inputs",
        },
    )


@login_required
def calculation(request):
    """This will run the financial calculations"""
    if request.method == "POST":
        print("Post request")

    else:
        print("Get request")
        general_inputs_model = GeneralInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        print(f"{general_inputs_model=}")
        print(f"length of query set is: {len(general_inputs_model)}")
        for item in general_inputs_model:
            general_inputs_dict = model_to_dict(item)
            del general_inputs_dict["id"]
            del general_inputs_dict["is_active"]
            del general_inputs_dict["created_by"]
            del general_inputs_dict["modified_at"]
        print(general_inputs_dict)

        savings_inputs_model = SavingsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        print(f"{savings_inputs_model=}")
        print(f"length of query set is: {len(savings_inputs_model)}")
        for item in savings_inputs_model:
            savings_inputs_dict = model_to_dict(item)
            del savings_inputs_dict["id"]
            del savings_inputs_dict["is_active"]
            del savings_inputs_dict["created_by"]
            del savings_inputs_dict["modified_at"]
        print(savings_inputs_dict)

        payments_inputs_model = PaymentsInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        print(f"{payments_inputs_model=}")
        print(f"length of query set is: {len(payments_inputs_model)}")
        for item in payments_inputs_model:
            payments_inputs_dict = model_to_dict(item)
            del payments_inputs_dict["id"]
            del payments_inputs_dict["is_active"]
            del payments_inputs_dict["created_by"]
            del payments_inputs_dict["modified_at"]
        print(f"payments dict: {payments_inputs_dict}")
        base_monthly_bills_dict = {
            "base_monthly_bills": payments_inputs_dict["base_monthly_bills"]
        }
        payment_dict_list = {
            "payment_items": [
                {
                    "item_name": payments_inputs_dict["payment_1_item_name"],
                    "item_pmt_start_age_yrs": payments_inputs_dict[
                        "payment_1_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": payments_inputs_dict[
                        "payment_1_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": payments_inputs_dict[
                        "payment_1_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": payments_inputs_dict["payment_1_item_down_pmt"],
                    "item_monthly_pmt": payments_inputs_dict[
                        "payment_1_item_monthly_pmt"
                    ],
                }
            ]
        }

        retirement_inputs_model = RetirementInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        print(f"{retirement_inputs_model=}")
        print(f"length of query set is: {len(retirement_inputs_model)}")
        for item in retirement_inputs_model:
            retirement_inputs_dict = model_to_dict(item)
            del retirement_inputs_dict["id"]
            del retirement_inputs_dict["is_active"]
            del retirement_inputs_dict["created_by"]
            del retirement_inputs_dict["modified_at"]
        print(retirement_inputs_dict)

        rates_inputs_model = RatesInputsModel.objects.filter(
            created_by=request.user, is_active=True
        )
        print(f"{rates_inputs_model=}")
        print(f"length of query set is: {len(rates_inputs_model)}")
        for item in rates_inputs_model:
            rates_inputs_dict = model_to_dict(item)
            del rates_inputs_dict["id"]
            del rates_inputs_dict["is_active"]
            del rates_inputs_dict["created_by"]
            del rates_inputs_dict["modified_at"]
        print(rates_inputs_dict)

    full_dict = {
        **{"name": "Test Scenario"},
        **general_inputs_dict,
        **savings_inputs_dict,
        **base_monthly_bills_dict,
        **payment_dict_list,
        **retirement_inputs_dict,
        **rates_inputs_dict,
    }

    print(f"full_dict is {full_dict}")
    # print(f'base_bills is {full_dict['base_monthly_bills']}')

    (total_savings_df, total_retirement_df) = stochastic_finances_func.main(full_dict)
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

    return render(
        request,
        "core/index.html",
    )
