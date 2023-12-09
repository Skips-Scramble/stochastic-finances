from .forms import (
    NewTestCalcForm,
    NewFinancialSituation,
    JobForm,
    JobFormSet,
    PersonForm,
)
from .models import FinancialInputs, Person, Job

import json

import stochastic_finances_func

from django.shortcuts import render, redirect


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


def add_financial_situation(request):
    """Create a new financial situation"""
    if request.method == "POST":
        form = NewFinancialSituation(request.POST)
        if form.is_valid():
            input_dict_new = form.cleaned_data
            FinancialInputs.objects.create(
                **form.cleaned_data,
                **{"input_dict": form.cleaned_data},
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
                {
                    "item_name": input_dict_new["payment_2_item_name"],
                    "item_pmt_start_age_yrs": input_dict_new[
                        "payment_2_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": input_dict_new[
                        "payment_2_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": input_dict_new[
                        "payment_2_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": input_dict_new["payment_2_item_down_pmt"],
                    "item_monthly_pmt": input_dict_new["payment_2_item_monthly_pmt"],
                },
                {
                    "item_name": input_dict_new["payment_3_item_name"],
                    "item_pmt_start_age_yrs": input_dict_new[
                        "payment_3_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": input_dict_new[
                        "payment_3_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": input_dict_new[
                        "payment_3_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": input_dict_new["payment_3_item_down_pmt"],
                    "item_monthly_pmt": input_dict_new["payment_3_item_monthly_pmt"],
                },
            ]
            print(f"input_dict new = {json.dumps(input_dict_new, indent=2)}")

            (total_savings_df, total_retirement_df) = stochastic_finances_func.main(
                input_dict_new
            )
            for age in range(60, 100, 5):
                print(
                    f"Average savings at age {age} is {total_savings_df.loc[lambda df: (df.age_yrs == age) & (df.age_mos == 0)]['average'].iat[0]:,.0f}"
                )
                print(
                    f"Average retirement at age {age} is {total_retirement_df.loc[lambda df: (df.age_yrs == age) & (df.age_mos == 0)]['average'].iat[0]:,.0f}"
                )
                print("")
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


def add_person(request):
    if request.method == "POST":
        person_form = PersonForm(request.POST)
        job_formset = JobFormSet(request.POST, prefix="job")
        if person_form.is_valid() and job_formset.is_valid():
            person = person_form.save()
            for job_form in job_formset:
                job = job_form.save(commit=False)
                job.person = person
                job.save()
            return redirect("success")  # Redirect to a success page or another view
    else:
        person_form = PersonForm()
        job_formset = JobFormSet(prefix="job")
    return render(
        request,
        "add_person.html",
        {"person_form": person_form, "job_formset": job_formset},
    )
