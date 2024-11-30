from datetime import date

import pandas as pd

base_healthcare_inputs = pd.read_csv(
    r"./research/healthcare/healthcare_assumptions.csv"
).rename(columns={"cost_2024": date(2024, 1, 1)})

date_range = pd.date_range(start="2024-02-01", end="2174-12-01", freq="MS")

for diff, col in enumerate(date_range):
    base_healthcare_inputs[col.date()] = base_healthcare_inputs[date(2024, 1, 1)] * (
        1 + base_healthcare_inputs["avg"]
    ) ** ((diff + 1) / 12)

output_df = (
    pd.melt(
        base_healthcare_inputs,
        id_vars=["age_band"],  # Columns to keep
        value_vars=[
            col.date() for col in date_range
        ],  # Dynamically identified date columns
        var_name="month",  # New column for date column names
        value_name="healthcare_cost",  # New column for the values
    )
    .sort_values(["age_band"])
    .assign(
        month=lambda df: pd.to_datetime(df["month"]).dt.date,
        age_band=lambda df: df["age_band"].astype("string"),
    )
)

output_df.to_csv("./research/healthcare/healthcare_inputs.csv", index=False)
