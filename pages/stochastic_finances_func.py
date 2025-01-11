import pandas as pd
import plotly.express as px

from pages.base_scenario import BaseScenario
from pages.random_scenario import RandomScenario

# from assumption_validations import apply_validations


def main(assumptions) -> None:
    # with open("input_assumptions_full.json") as json_data:
    #     assumptions = json.load(json_data)

    # apply_validations(assumptions)

    base_scenario = BaseScenario(assumptions)

    base_age_df = base_scenario.create_base_df()[
        ["count", "age_yrs", "age_mos", "savings_account", "retirement_account"]
    ].rename(
        columns={
            "savings_account": "savings_account_0",
            "retirement_account": "retirement_account_0",
        }
    )

    for i in range(100):
        new_scenario = RandomScenario(base_scenario)
        new_scenario.create_full_df().to_csv(f"./outputs/scen_{i+1}.csv", index=False)

        base_age_df = base_age_df.merge(
            new_scenario.create_full_df()[
                ["count", "var_savings_account", "var_retirement_account"]
            ].rename(
                columns={
                    "var_savings_account": f"savings_account_{i+1}",
                    "var_retirement_account": f"retirement_account_{i+1}",
                }
            ),
            on="count",
            how="left",
        )

    total_savings_df = (
        base_age_df.filter(regex="^savings_account|^age").rename(
            columns=lambda x: (
                x.replace("savings_", "") if x.startswith("savings_") else x
            )
        )
    ).assign(
        avg=lambda df: df.filter(regex="^account").mean(axis=1),
        account_type="savings",
    )

    total_retirement_df = (
        base_age_df.filter(regex="^retirement_account|^age").rename(
            columns=lambda x: (
                x.replace("retirement_", "") if x.startswith("retirement_") else x
            )
        )
    ).assign(
        avg=lambda df: df.filter(regex="^account").mean(axis=1),
        account_type="retirement",
    )

    total_total_df_prep = (
        total_savings_df.drop(["age_yrs", "age_mos", "account_type"], axis=1)
        + total_retirement_df.drop(["age_yrs", "age_mos", "account_type"], axis=1)
    ).assign(account_type="total")

    total_total_df = pd.concat(
        [total_savings_df[["age_yrs", "age_mos"]], total_total_df_prep], axis=1
    )

    total_outputs_df = (
        pd.concat([total_savings_df, total_retirement_df, total_total_df])
        .sort_values(["age_yrs", "age_mos"])
        .loc[lambda df: df.age_mos == 0]
    )

    savings_retirement_fig = px.line(
        total_outputs_df, x="age_yrs", y="avg", color="account_type"
    )
    savings_retirement_fig.update_xaxes(title_text="Age (years)", dtick=5)
    savings_retirement_fig.update_yaxes(title_text="Amount")
    # savings_retirement_fig.show()

    return total_savings_df, total_retirement_df, total_outputs_df
