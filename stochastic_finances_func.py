import json

# from assumption_validations import apply_validations

from scenarios.base_scenario import BaseScenario
from scenarios.random_scenario import RandomScenario


def main(assumptions) -> None:
    # with open("input_assumptions.json") as json_data:
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

    return total_savings_df, total_retirement_df
