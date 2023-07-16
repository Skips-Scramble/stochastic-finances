def calc_variable_savings(
    tot_months: int, savings: float, interest_rate: float
) -> list:
    var_interest_list = np.random.normal(interest_rate, 1, tot_months)
    var_savings_list = []
    for i in range(tot_months):
        if i == 0:
            var_savings_list.append(round(float(savings), 2))
            prev_savings = round(float(savings), 2)
        else:
            monthly_interest = float(
                round((1 + (var_interest_list[i] / 100)) ** (1 / 12) - 1, 4)
            )
            # print(f'monthly_interest is {monthly_interest}')
            prev_savings = float(round(prev_savings * (1 + monthly_interest), 2))
            # print(f'prev_savings is {prev_savings}')
            var_savings_list.append(prev_savings)
    return var_savings_list