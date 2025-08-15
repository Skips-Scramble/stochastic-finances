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
