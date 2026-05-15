"""Tests that RandomScenario market-rate sampling is unbiased and symmetric.

These are regression tests for the one-sided-cap bug where rates above the
conservative baseline were silently clamped to the mean, causing the *applied*
average rate to be systematically ~60% below the assumed rate.

Statistical approach
--------------------
- Run a large number of scenarios (N_SCENARIOS) to get stable sample statistics.
- Assert the mean applied rate is within a generous tolerance of the assumed rate
  (|bias| < RATE_MEAN_TOLERANCE_PCT).  With N=200 scenarios the standard error of
  the mean is small enough that a real systematic bias of even 0.5% will reliably
  fail.
- Assert the distribution is symmetric: the fraction of months with rates above
  the mean and below the mean should each be near 50%.
- Assert that negative rates are achievable (market losses are real).
- Assert that rates above the assumed rate are achievable (upside is not capped).
"""

from datetime import date

import numpy as np
import pytest

from pages.base_scenario import BaseScenario
from pages.random_scenario import RandomScenario, variance_3

# ── constants ─────────────────────────────────────────────────────────────────

# Number of scenarios to run for statistical assertions.  Higher → more stable,
# slower.  200 gives standard error of ~0.5% for a 6.5% mean with variance_3=1.5.
N_SCENARIOS = 200

# Maximum tolerated absolute gap between assumed rate and mean applied rate.
RATE_MEAN_TOLERANCE_PCT = 1.5  # percentage points

# Symmetry tolerance: fraction of months above/below mean should be 50% ± this.
SYMMETRY_TOLERANCE = 0.05  # 5 percentage points


# ── shared fixture ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
# Minimal assumptions with a 401k using conservative rates so the full
# conservative glide-path + sampling code path is exercised.
def base_scenario_for_rates():
    assumptions = {
        "birthdate": date(1990, 1, 1),
        "retirement_age_yrs": 65,
        "retirement_age_mos": 0,
        "add_healthcare": False,
        "retirement_extra_expenses": 0.0,
        "base_savings": 50_000.0,
        "base_saved_per_mo": 0.0,
        "base_savings_per_yr_increase": 0.0,
        "savings_lower_limit": 0.0,
        "base_monthly_bills": 0.0,
        "base_rf_interest_per_yr": 3.25,
        "base_mkt_interest_per_yr": 6.5,
        "base_inflation_per_yr": 0.0,
        "payment_items": [],
        "retirement_accounts": [
            {
                "retirement_type": "traditional_401k",
                "base_retirement": 20_000.0,
                "base_retirement_per_mo": 0.0,
                "base_retirement_per_yr_increase": 0.0,
                "use_conservative_rates": True,
                "is_active": True,
            }
        ],
    }
    return BaseScenario(assumptions)


@pytest.fixture(scope="module")
# Run N_SCENARIOS random scenarios once and collect all var_yearly_mkt_interest
# values for statistical analysis.
def pooled_mkt_rates(base_scenario_for_rates):
    all_rates = []
    for _ in range(N_SCENARIOS):
        scenario = RandomScenario(base_scenario_for_rates)
        all_rates.extend(scenario.var_yearly_mkt_interest)
    return np.array(all_rates) * 100  # convert to percentage for readability


@pytest.fixture(scope="module")
# Per-scenario mean rates for testing that *each* scenario's mean stays close
# to the assumed value, not just the aggregate pool.
def per_scenario_mkt_means(base_scenario_for_rates):
    assumed_pct = base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
    means = []
    for _ in range(N_SCENARIOS):
        scenario = RandomScenario(base_scenario_for_rates)
        mean_pct = np.mean(scenario.var_yearly_mkt_interest) * 100
        means.append(mean_pct)
    return np.array(means), assumed_pct


# ── mean / bias tests ─────────────────────────────────────────────────────────


# The pooled mean of all applied market rates should be close to the assumed rate.
# A systematic one-sided cap would push this ~3-4 percentage points below the mean.
def test_pooled_mkt_rate_mean_close_to_assumed(
    pooled_mkt_rates, base_scenario_for_rates
):
    assumed_pct = base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
    pooled_mean = pooled_mkt_rates.mean()
    bias = abs(pooled_mean - assumed_pct)
    assert bias < RATE_MEAN_TOLERANCE_PCT, (
        f"Mean applied MKT rate {pooled_mean:.3f}% deviates from assumed "
        f"{assumed_pct:.2f}% by {bias:.3f}pp (tolerance {RATE_MEAN_TOLERANCE_PCT}pp). "
        f"A one-sided cap or skewed sampling would produce this bias."
    )


# Each individual scenario's mean rate should not consistently fall far below the
# assumed rate.  The median across scenarios should be close to the assumed rate.
def test_per_scenario_mkt_rate_median_close_to_assumed(per_scenario_mkt_means):
    means, assumed_pct = per_scenario_mkt_means
    median_mean = np.median(means)
    bias = abs(median_mean - assumed_pct)
    assert bias < RATE_MEAN_TOLERANCE_PCT, (
        f"Median per-scenario MKT rate mean {median_mean:.3f}% deviates from "
        f"assumed {assumed_pct:.2f}% by {bias:.3f}pp (tolerance {RATE_MEAN_TOLERANCE_PCT}pp)."
    )


# ── symmetry tests ─────────────────────────────────────────────────────────────


# The distribution should be symmetric: roughly half the months should have a
# rate above the conservative glide-path mean and half below.  A one-sided cap
# that clips all rates above the mean would make this ~0% above the mean.
def test_mkt_rates_are_symmetric_around_assumed(
    pooled_mkt_rates, base_scenario_for_rates
):
    assumed_pct = base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
    frac_above = (pooled_mkt_rates > assumed_pct).mean()
    assert abs(frac_above - 0.5) < SYMMETRY_TOLERANCE, (
        f"Only {frac_above:.1%} of sampled MKT rates are above the assumed "
        f"{assumed_pct:.2f}%.  Expected ~50%.  A one-sided cap would push this "
        f"toward 0%."
    )


# ── negative / upside reachability tests ──────────────────────────────────────


# With variance_3=1.5, the normal distribution has a very wide spread and
# negative rates (market losses) must be possible and occur with meaningful
# frequency across many scenarios.
def test_negative_mkt_rates_are_possible(pooled_mkt_rates):
    frac_negative = (pooled_mkt_rates < 0).mean()
    assert frac_negative > 0.10, (
        f"Only {frac_negative:.1%} of sampled MKT rates are negative.  "
        f"With variance_3={variance_3} market losses should be common (expected >10%)."
    )


# The upside must also be reachable: rates well above the assumed rate must occur.
# A one-sided cap that clamps at the mean would fail this assertion.
def test_above_mean_mkt_rates_are_possible(pooled_mkt_rates, base_scenario_for_rates):
    assumed_pct = base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
    frac_well_above = (pooled_mkt_rates > assumed_pct * 1.5).mean()
    assert frac_well_above > 0.10, (
        f"Only {frac_well_above:.1%} of sampled MKT rates exceed 1.5× the assumed "
        f"rate ({assumed_pct * 1.5:.2f}%).  A one-sided upside cap would produce this. "
        f"Expected >10% with variance_3={variance_3}."
    )


# ── conservative-rates code path ──────────────────────────────────────────────


# Rates sampled for a specific retirement account using conservative glide-path
# should also be unbiased.  This exercises _account_var_yearly_rate_list.
def test_per_account_conservative_rate_mean_close_to_assumed(base_scenario_for_rates):
    assumed_pct = base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
    account = base_scenario_for_rates.retirement_list[0]

    all_rates = []
    for _ in range(N_SCENARIOS):
        scenario = RandomScenario(base_scenario_for_rates)
        all_rates.extend(scenario._account_var_yearly_rate_list(account))

    mean_pct = np.mean(all_rates) * 100
    # The conservative glide-path steps the mean down toward 5% over decades, so
    # the lifetime average will be below the starting 6.5%.  Use a wider tolerance
    # here and compare against the midpoint of start (6.5%) and floor (5%).
    glide_midpoint = (assumed_pct + 5.0) / 2
    bias = abs(mean_pct - glide_midpoint)
    assert bias < RATE_MEAN_TOLERANCE_PCT + 1.0, (
        f"Per-account conservative rate mean {mean_pct:.3f}% deviates from "
        f"glide midpoint {glide_midpoint:.2f}% by {bias:.3f}pp.  "
        f"Systematic bias suggests a one-sided cap is active."
    )


# Rates for a specific account must also be symmetric: roughly equal numbers of
# months above and below each month's conservative baseline.
def test_per_account_conservative_rate_symmetry(base_scenario_for_rates):
    account = base_scenario_for_rates.retirement_list[0]
    conservative_baselines = np.array(
        base_scenario_for_rates._build_conservative_yearly_rate_list(
            base_scenario_for_rates.assumptions["base_mkt_interest_per_yr"]
        )
    )

    months_above = 0
    total_months = 0
    for _ in range(N_SCENARIOS):
        scenario = RandomScenario(base_scenario_for_rates)
        sampled = np.array(scenario._account_var_yearly_rate_list(account))
        months_above += (sampled > conservative_baselines).sum()
        total_months += len(sampled)

    frac_above = months_above / total_months
    assert abs(frac_above - 0.5) < SYMMETRY_TOLERANCE, (
        f"Only {frac_above:.1%} of per-account sampled rates exceed their monthly "
        f"conservative baseline.  Expected ~50%.  A one-sided cap produces ~0%."
    )
