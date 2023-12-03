from .forms import NewTestCalcForm, NewFinancialSituation
from .models import FinancialInputs

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
            # item = form.save(commit=False)
            input_dict_new = form.cleaned_data
            print(input_dict_new)
            FinancialInputs.objects.create(
                **input_dict_new,
                **{"input_dict": form.cleaned_data},
            )
            input_dict_new['payment_items'] = []
            input_dict_new['birthday'] = "12/22/1986"
            print(input_dict_new)
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
