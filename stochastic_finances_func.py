import json

import pandas as pd
import plotly.express as px

from scenarios.base_scenario import BaseScenario
from scenarios.random_scenario import RandomScenario

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

    total_savings_df = base_age_df.filter(regex="^savings_account|^age").assign(
        average=lambda df: df.filter(regex="^savings_account").mean(axis=1)
    )

    total_retirement_df = base_age_df.filter(regex="^retirement_account|^age").assign(
        average=lambda df: df.filter(regex="^retirement_account").mean(axis=1)
    )

    total_outputs = (
        total_savings_df[["age_yrs", "age_mos", "average"]]
        .assign(savings=lambda df: df.average.round().astype(int))
        .loc[lambda df: df.age_mos == 0]
        .merge(
            total_retirement_df[["age_yrs", "age_mos", "average"]]
            .assign(retirement=lambda df: df.average.round().astype(int))
            .loc[lambda df: df.age_mos == 0],
            on=["age_yrs", "age_mos"],
            how="left",
        )
        .assign(
            total=lambda df: df.savings + df.retirement,
        )
    )[["age_yrs", "savings", "retirement", "total"]]

    total_for_graph = pd.melt(
        total_outputs,
        id_vars=["age_yrs"],
        value_vars=["savings", "retirement", "total"],
    )

    savings_retirement_fig = px.line(
        total_for_graph, x="age_yrs", y="value", color="variable"
    )
    savings_retirement_fig.update_xaxes(title_text="Age (years)", dtick=5)
    savings_retirement_fig.update_yaxes(title_text="Amount")
    # savings_retirement_fig.show()

    return total_savings_df, total_retirement_df
