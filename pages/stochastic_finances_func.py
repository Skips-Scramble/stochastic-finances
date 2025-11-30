import json
import pandas as pd


from pages.random_scenario import BaseScenario
from pages.random_scenario import RandomScenario

# from assumption_validations import apply_validations


def main(assumptions) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Main function to calculate the core dfs"""
    with open("input_assumptions_full.json") as json_data:
        assumptions = json.load(json_data)

    # apply_validations(assumptions)

    base_scenario = BaseScenario(assumptions)

    # Get retirement account names from retirement_list
    retirement_cols = [
        ret_account.name for ret_account in base_scenario.retirement_list
    ]

    # Build column selection list
    select_cols = ["count", "age_yrs", "age_mos", "savings_account"] + retirement_cols

    # Build rename dictionary
    rename_dict = {"savings_account": "savings_account_0"}
    for col in retirement_cols:
        rename_dict[col] = f"{col}_0"

    base_age_df = base_scenario.create_base_df()[select_cols].rename(
        columns=rename_dict
    )

    for i in range(100):  # Number of scenarios to generate
        new_scenario = RandomScenario(base_scenario)
        new_scenario.create_full_df().to_csv(f"./outputs/scen_{i+1}.csv", index=False)

        # Build column selection and rename for merge dynamically
        merge_cols = ["count", "var_savings_account"]
        merge_rename = {"var_savings_account": f"savings_account_{i+1}"}

        for col in retirement_cols:
            var_col = f"var_{col}"
            merge_cols.append(var_col)
            merge_rename[var_col] = f"{col}_{i+1}"

        base_age_df = base_age_df.merge(
            new_scenario.create_full_df()[merge_cols].rename(columns=merge_rename),
            on="count",
            how="left",
        )

    total_savings_df = (
        base_age_df.filter(regex="savings_account|^age").rename(
            columns=lambda x: (
                x.replace("savings_", "") if x.startswith("savings_") else x
            )
        )
    ).assign(
        avg=lambda df: df.filter(regex="^account").mean(axis=1),
        account_type="savings",
    )

    total_retirement_df = (
        base_age_df.filter(
            regex="traditional_401k|traditional_ira|roth_401k|roth_ira|^age"
        ).rename(
            columns=lambda x: (
                x.replace("retirement_", "") if x.startswith("retirement_") else x
            )
        )
    ).assign(
        avg_traditional_401k=lambda df: df.filter(regex="^traditional_401k").mean(
            axis=1
        ),
        avg_traditional_ira=lambda df: df.filter(regex="^traditional_ira").mean(axis=1),
        avg_roth_401k=lambda df: df.filter(regex="^roth_401k").mean(axis=1),
        avg_roth_ira=lambda df: df.filter(regex="^roth_ira").mean(axis=1),
        account_type="retirement",
    )

    # Sort columns: age columns first, then grouped by account type, then aggregates
    age_cols = [col for col in total_retirement_df.columns if col.startswith("age_")]
    trad_401k_cols = sorted(
        [
            col
            for col in total_retirement_df.columns
            if col.startswith("traditional_401k_")
        ]
    )
    roth_401k_cols = sorted(
        [col for col in total_retirement_df.columns if col.startswith("roth_401k_")]
    )
    trad_ira_cols = sorted(
        [
            col
            for col in total_retirement_df.columns
            if col.startswith("traditional_ira_")
        ]
    )
    roth_ira_cols = sorted(
        [col for col in total_retirement_df.columns if col.startswith("roth_ira_")]
    )
    avg_cols = [
        "avg_traditional_401k",
        "avg_traditional_ira",
        "avg_roth_401k",
        "avg_roth_ira",
    ]
    other_cols = ["account_type"]

    column_order = (
        age_cols
        + trad_401k_cols
        + roth_401k_cols
        + trad_ira_cols
        + roth_ira_cols
        + avg_cols
        + other_cols
    )
    total_retirement_df = total_retirement_df[column_order]

    return total_savings_df, total_retirement_df
