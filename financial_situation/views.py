from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import stochastic_finances_func
from inputs.models import (
    GeneralInputsModel,
    PaymentsInputsModel,
    RatesInputsModel,
    RetirementInputsModel,
    SavingsInputsModel,
)
from utils.get_field_values import model_to_dict


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
        payment_item_list = []
        for item in payments_inputs_model:
            payments_inputs_dict = model_to_dict(item)
            del payments_inputs_dict["id"]
            del payments_inputs_dict["is_active"]
            del payments_inputs_dict["created_by"]
            del payments_inputs_dict["modified_at"]
            payment_item_list.append(
                {
                    "item_name": payments_inputs_dict["payment_item_name"],
                    "item_pmt_start_age_yrs": payments_inputs_dict[
                        "payment_item_pmt_start_age_yrs"
                    ],
                    "item_pmt_start_age_mos": payments_inputs_dict[
                        "payment_item_pmt_start_age_mos"
                    ],
                    "item_pmt_length_yrs": payments_inputs_dict[
                        "payment_item_pmt_length_yrs"
                    ],
                    "item_down_pmt": payments_inputs_dict["payment_item_down_pmt"],
                    "item_monthly_pmt": payments_inputs_dict[
                        "payment_item_monthly_pmt"
                    ],
                }
            )
            print(f"payments dict: {payments_inputs_dict}")
        print(f"payment_item_list is {payment_item_list}")
        base_monthly_bills_dict = {
            "base_monthly_bills": payments_inputs_dict["base_monthly_bills"]
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
        **{"payment_items": payment_item_list},
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
