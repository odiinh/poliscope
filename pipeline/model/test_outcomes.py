import numpy as np
import pandas as pd
import pytest

from pipeline.model.outcomes import build_baseline, build_outcomes

DEBT_RATES = {"AA": 0.01, "BB": 0.02, "CC": 0.05}
GDP_RATES = {"AA": 0.01, "BB": 0.02, "CC": 0.03}


def gdp_pc(state, year):
    return 50_000 * np.exp(GDP_RATES[state] * (year - 1992))


def make_panel():
    rows = []
    for state, debt_rate in DEBT_RATES.items():
        for year in range(1992, 2026):
            pop = 1_000_000
            rows.append(
                {
                    "state": state,
                    "year": year,
                    "rgdp_musd2017": gdp_pc(state, year) * pop / 1e6
                    if year >= 1997
                    else np.nan,
                    "pop": pop,
                    "gdp_pc": gdp_pc(state, year) if year >= 1997 else np.nan,
                    "debt_pc": 1_000 * np.exp(debt_rate * (year - 1992))
                    if year <= 2018
                    else np.nan,
                }
            )
    return pd.DataFrame(rows)


def test_outcomes_are_relative_to_benchmark_and_skip_missing_years():
    terms = pd.DataFrame(
        [
            {"term_id": "cc-2007", "state": "CC", "t0": 2007},
            {"term_id": "aa-2007", "state": "AA", "t0": 2007},
            {
                "term_id": "aa-1999",
                "state": "AA",
                "t0": 1999,
            },  # GDP prior starts 1994: no data
        ]
    )
    rows, coefs, _ = build_outcomes(terms, make_panel())
    got = {(r["term_id"], r["metric"]): r for r in rows}
    assert ("aa-1999", "gdp_pc_rel") not in got
    assert got[("cc-2007", "debt_pc_rel")]["actual"] == pytest.approx(0.03)
    assert got[("aa-2007", "debt_pc_rel")]["prior"] == pytest.approx(-0.01)
    # equal populations, so US GDP per capita is the mean of the states'
    us = {y: np.mean([gdp_pc(s, y) for s in GDP_RATES]) for y in (2006, 2010)}
    expected = 0.03 - (np.log(us[2010]) - np.log(us[2006])) / 4
    assert got[("cc-2007", "gdp_pc_rel")]["actual"] == pytest.approx(expected)
    assert got[("cc-2007", "debt_pc_rel")]["window"] == [2006, 2010]
    for r in rows:
        assert r["residual"] == pytest.approx(r["actual"] - r["baseline"])
    assert coefs["debt_pc_rel"]["n"] == 3


def test_debt_ending_2018_gives_null_latest_prior():
    panel = make_panel()
    terms = pd.DataFrame(
        [
            {"term_id": "aa-2007", "state": "AA", "t0": 2007},
            {"term_id": "cc-2007", "state": "CC", "t0": 2007},
        ]
    )
    _, coefs, rel = build_outcomes(terms, panel)
    baseline = build_baseline(panel, coefs, rel)
    assert baseline["latest_window"] == {
        "gdp_pc_rel": [2021, 2025],
        "debt_pc_rel": [2014, 2018],
    }
    assert baseline["latest_prior"]["AA"]["debt_pc_rel"] is None
    assert (
        baseline["latest_prior"]["CC"]["gdp_pc_rel"]
        > 0
        > baseline["latest_prior"]["AA"]["gdp_pc_rel"]
    )
