import numpy as np


def calc_base_added_savings(assumptions: dict, tot_months: int) -> list:
    """Function to create list of savings when taking into account added
    savings per month and interest using variable amounts based on a
    distribution
    """
    var_interest_yrly_list = np.random.normal(
        assumptions["base_interest_per_yr"],
        assumptions["base_interest_per_yr"] * (1.5),
        tot_months,
    )

    print(f"var_interest_yrly_list is: {var_interest_yrly_list}")

    var_interest_monthly_list = [
        float(((1 + (x / 100)) ** (1 / 12) - 1)) for x in var_interest_yrly_list
    ]

    print(f"var_interest_monthly_lis is: {var_interest_monthly_list}")

    var_added_savings = np.random.normal(
        assumptions["base_saved_per_month"],
        assumptions["base_saved_per_month"] * (0.5),
        tot_months,
    )

    print(f"var_added_savings is: {var_added_savings}")

    var_savings_list = []
    for i in range(tot_months):
        if i == 0:
            prev_savings = round(float(assumptions["current_savings"]), 2)
            var_savings_list.append(prev_savings)
        else:
            prev_savings = float(
                round(
                    prev_savings * (1 + var_interest_monthly_list[i])
                    + var_added_savings[i],
                    2,
                )
            )
            var_savings_list.append(prev_savings)
    return (
        [float(x) for x in var_interest_yrly_list],
        var_interest_monthly_list,
        [float(x) for x in var_added_savings],
        var_savings_list,
    )
