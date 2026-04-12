# Healthcare Assumptions in This Project

This folder contains the assumptions and generated lookup data used to model healthcare costs in the stochastic finances simulation.

## Overview

At a high level, this module converts a small set of age-based healthcare assumptions into a month-by-month cost series that the financial simulator can use automatically.

What is happening:
- A baseline 2024 healthcare cost is defined for each age band.
- Those baseline values are grown over time using an assumed annual increase rate.
- The resulting monthly lookup table is joined into each simulation timeline by age band and month.
- The model then applies that value as part of monthly cash-flow math when healthcare is enabled.

Why this exists:
- The simulator needs a consistent way to represent healthcare expenses over long horizons.
- A deterministic lookup keeps scenario behavior transparent and reproducible.
- The approach gives realistic age-patterned cost pressure without requiring a full claims or insurance-plan model.

How to interpret outputs:
- `healthcare_cost` should be read as an aggregate planning assumption.
- It is intended to support long-term financial planning tradeoffs, not detailed benefit design decisions.

## Clear Summary: What These Healthcare Costs Represent

`healthcare_cost` is a single monthly, age-banded expense estimate used for planning in this simulator.

In plain terms, it represents:
- A modeled all-in healthcare spending proxy for a person in a given age band at a given month.
- A deterministic planning input that applies the same lookup logic each run when healthcare is enabled.

It does not represent:
- A claims-level breakdown of spending categories.
- A Medicare benefit component split (Part A, Part B, Part D).
- A separated premium versus deductible/copay/coinsurance accounting.
- A personalized medical underwriting or plan-design estimate.

Bottom line:
- Use it as a practical long-horizon healthcare expense assumption for scenario comparison.
- Do not use it as a literal insurance quote or policy-level benefit estimate.

Audience and intent:
- This document is written for technical readers with healthcare familiarity.
- The goal is to explain where the assumptions come from, how they are constructed, and what they do or do not represent in the application.

## Files and Their Roles

- `healthcare_assumptions.csv`
  - Source assumptions by age band.
  - Columns:
    - `age_band`: age category used in lookups
    - `mo_increase_rate`: annual growth parameter applied monthly via compounding
    - `cost_2024`: baseline monthly healthcare cost at 2024-01-01 for that age band

- `healthcare_creator.py`
  - Generates projected monthly healthcare costs from assumptions.
  - Reads `healthcare_assumptions.csv` and writes `healthcare_inputs.csv`.

- `healthcare_inputs.csv`
  - Generated monthly lookup table used by the simulator.
  - Columns:
    - `age_band`
    - `month`
    - `healthcare_cost`

- `sources.txt` and `Age and Sex/source.txt`
  - Upstream source references used for assumptions research.

## Assumption Construction Method

For each age band, costs are projected forward from the 2024 baseline using monthly compounding:

$projected\_cost_{t} = cost\_2024 \times (1 + mo\_increase\_rate)^{t/12}$

Where:
- $t$ is months after 2024-01-01
- `mo_increase_rate` is the annual growth parameter in the assumptions table

The generator produces month-by-month values from 2024-02 through 2174-12.

## What This Model Represents

In this project, `healthcare_cost` is an age-banded aggregate monthly healthcare cost stream used as an expense term in cash-flow calculations.

Interpretation:
- It is best treated as a modeled all-in healthcare expense proxy by age and month.
- It is not represented as a benefit design model or claims adjudication model.

## Scope Boundaries: Included vs Not Explicitly Modeled

Included:
- Age-based healthcare cost levels
- Time growth via compounding
- Deterministic monthly lookup for simulation

Not explicitly modeled (important):
- Medicare Part A vs Part B vs Part D as separate components
- Separate payer channels (Medicare vs Medicaid vs private insurance) inside the runtime model
- Premiums vs deductibles/copays/coinsurance as distinct variables
- Individual risk factors, diagnoses, utilization patterns, or plan design details

Direct answers to common questions:
- Medicare costs: partially and implicitly, only as part of aggregate assumptions; not separated into A/B/D.
- Parts A and B only, or also Part D: not explicitly separated; no per-part modeling.
- Premiums only, or also out-of-pocket: not split; the model uses a single aggregate cost value.
- All healthcare costs: modeled as an aggregate proxy, not a full accounting decomposition.

## How the Assumptions Are Used in the Application

1. User input toggle:
- The `add_healthcare` boolean controls whether healthcare costs are included.
- If false, `healthcare_cost` is a zero series.

2. Age-band matching:
- Runtime age is bucketed into fixed bands: `0-18`, `19-44`, `45-64`, `65-84`, `85+`.
- The model merges `age_band` and `month` against `healthcare_inputs.csv`.

3. Cash-flow impact:
- Pre-retirement: healthcare costs reduce monthly savings flow.
- Post-retirement: healthcare costs are added into monthly expense burden paid from savings.

4. Outputs:
- `healthcare_cost` is included as a column in scenario dataframes and written to scenario output files.
- In stochastic runs, `healthcare_cost` remains deterministic (same age/month lookup), while other variables may vary.

## Operational Notes for Maintainers

When to regenerate `healthcare_inputs.csv`:
- After any edit to `healthcare_assumptions.csv`
- After changing projection logic in `healthcare_creator.py`

How to regenerate:
- Run `python research/healthcare/healthcare_creator.py` from repo root so relative paths resolve correctly.

Sanity checks after regeneration:
- File writes successfully to `research/healthcare/healthcare_inputs.csv`
- No missing `age_band` or `month` rows expected by runtime merges
- Sample months and age bands produce plausible monotonic growth relative to assumptions

## Known Limitations and Future Extensions

Current limitations:
- No component-level decomposition (premium, out-of-pocket, payer, Medicare part)
- No state/region-specific or plan-specific variation
- No morbidity-driven heterogeneity

Potential extensions:
- Add separate series for premiums and out-of-pocket costs
- Add Medicare Part A/B/D decomposition for retirement ages
- Add payer-specific series and blending logic
- Add uncertainty model for healthcare cost inflation by age band

## Caution for Interpretation

Use `healthcare_cost` as a planning assumption, not as a literal benefits estimate or actuarial quote. If policy or plan-level decisions depend on component detail, this model should be extended with explicit decomposition fields and data sources.
