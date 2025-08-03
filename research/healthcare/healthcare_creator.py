from datetime import date
from pathlib import Path

import pandas as pd


def main():
    """
    Generates projected healthcare costs over time based on assumptions and saves the
    results to a CSV file.
    Reads healthcare cost assumptions from a CSV file, calculates monthly projected costs
    for each age band,
    and outputs the results in a long-format CSV file.
    """
    assumptions_path = Path("./research/healthcare/healthcare_assumptions.csv")
    output_path = Path("./research/healthcare/healthcare_inputs.csv")
    base_date = date(2024, 1, 1)

    df = pd.read_csv(assumptions_path).rename(columns={"cost_2024": base_date})

    date_range = pd.date_range(start="2024-02-01", end="2174-12-01", freq="MS")

    for diff, col in enumerate(date_range):
        df[col.date()] = df[base_date] * (1 + df["mo_increase_rate"]) ** (
            (diff + 1) / 12
        )

    output_df = (
        pd.melt(
            df,
            id_vars=["age_band"],
            value_vars=[col.date() for col in date_range],
            var_name="month",
            value_name="healthcare_cost",
        )
        .sort_values(["age_band", "month"])
        .assign(
            month=lambda d: pd.to_datetime(d["month"]).dt.date,
            age_band=lambda d: d["age_band"].astype("string"),
        )
    )

    output_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
