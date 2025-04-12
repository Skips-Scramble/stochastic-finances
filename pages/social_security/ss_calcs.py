from datetime import date


def ss_fra(birthdate: date) -> tuple:
    """
    Calculate the full retirement age (FRA) based on the birthdate.

    Args:
        birthdate (datetime.date): The birthdate of the individual.

    Returns:
        tuple: A tuple containing the full retirement age in years and months.
    """
    # Define the full retirement age based on birth year
    if birthdate.year < 1938:
        ss_fra_yrs = 65
        ss_fra_mos = 0
    elif 1938 <= birthdate.year < 1955:
        ss_fra_yrs = 66
        ss_fra_mos = 0
    elif 1955 <= birthdate.year < 1960:
        ss_fra_yrs = 66
        ss_fra_mos = (birthdate.year - 1954) * 2
    else:
        ss_fra_yrs = 67
        ss_fra_mos = 0

    return ss_fra_yrs, ss_fra_mos


def ss_amt_by_date(
    birthdate: date,
    ss_bene_fra: float,
    ss_withdraw_age_yrs: float,
    ss_withdraw_age_mos: float,
    *,
    stop_working_age_yrs: int,
    stop_working_age_mos: int,
    recent_income: float,
) -> float:
    """
    Need to write docstring
    """
    # Convert full retirement age (FRA) and current age to months
    fra_total_months = (ss_fra(birthdate)[0] * 12) + ss_fra(birthdate)[1]
    withdraw_age_total_months = (ss_withdraw_age_yrs * 12) + ss_withdraw_age_mos

    # Calculate the difference in months between FRA and current age
    months_difference = age_total_months - fra_total_months

    # Adjust the benefit based on early or delayed claiming
    if months_difference <= 0:  # Claiming early
        reduction_per_month = 5 / 9 / 100 if months_difference >= -36 else 5 / 12 / 100
        ss_benefit_change = 1 - months_difference * reduction_per_month
    else:
        increase_per_month = 2 / 3 / 100
        ss_benefit_change = ss_bene_fra * (1 + months_difference * increase_per_month)

    # Include recent income in the calculation if applicable
    if recent_income > 0:
        ss_benefit += (
            recent_income * 0.1
        )  # Example: Add 10% of recent income to the benefit

    # Return the calculated benefit as a dictionary
    return round(ss_benefit, 2)
