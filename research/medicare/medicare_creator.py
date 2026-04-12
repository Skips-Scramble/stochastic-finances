from datetime import date
from pathlib import Path

import pandas as pd


def main():
    """
    Generates projected Medicare costs over time based on assumptions and saves the
    results to a CSV file.
    Reads Medicare cost assumptions from a CSV file, calculates monthly projected costs
    for each (cost_type, age_band) combination, and outputs the results in a long-format
    CSV file.

    cost_type values:
        - part_b_premium: Medicare Part B monthly premium
        - part_d_premium: Medicare Part D monthly premium (national average)
        - part_b_deductible: Medicare Part B annual deductible amortized monthly
        - part_d_deductible: Medicare Part D annual deductible amortized monthly

    These apply only to months where the simulated person is age 65 or older.
    The growth rate for each (cost_type, age_band) matches the corresponding age band
    rate used in healthcare_assumptions.csv to keep all Medicare-era inflation consistent.
    """
    assumptions_path = Path("./research/medicare/medicare_assumptions.csv")
    output_path = Path("./research/medicare/medicare_inputs.csv")
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
            id_vars=["cost_type", "age_band"],
            value_vars=[col.date() for col in date_range],
            var_name="month",
            value_name="medicare_cost",
        )
        .sort_values(["cost_type", "age_band", "month"])
        .assign(
            month=lambda d: pd.to_datetime(d["month"]).dt.date,
            age_band=lambda d: d["age_band"].astype("string"),
            cost_type=lambda d: d["cost_type"].astype("string"),
        )
    )

    output_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
