import numpy as np
from jsonschema import Draft7Validator

from pipeline.model import backtest, forecasts, pca_map
from pipeline.model.common import DIMS, ROOT, read_json

STATES = [f"{a}{b}" for a in "abcdefg" for b in "abcdefg"][:45]
COHORTS = (2003, 2007, 2011, 2015, 2019)


def synthetic(signal_strength, seed=0):
    """45 states x 5 cohorts; the outcome residual follows the tax stance when signal_strength > 0."""
    rng = np.random.default_rng(seed)
    profiles, outcomes = [], []
    for t0 in COHORTS:
        for state in STATES:
            stances = rng.uniform(-1, 1, len(DIMS))
            stances[rng.random(len(DIMS)) < 0.2] = np.nan
            stances[0] = rng.uniform(-1, 1)
            tid = f"{state}-{t0}"
            profiles.append(
                {
                    "id": tid,
                    "kind": "historical",
                    "name": tid,
                    "state": state.upper(),
                    "party": "DR"[int(stances[0] > 0)],
                    "term_start": t0,
                    "source": {"type": "test", "year": t0, "url": "", "sha1": ""},
                    "dims": {
                        d: {
                            "stance": None if np.isnan(s) else float(s),
                            "salience": 0.5,
                            "confidence": 0.8,
                            "evidence": [],
                        }
                        for d, s in zip(DIMS, stances)
                    },
                    "extractor": {"model": "test", "prompt_version": "v1"},
                }
            )
            prior = rng.normal(0, 0.01)
            actual = 0.5 * prior + signal_strength * stances[0] + rng.normal(0, 0.005)
            outcomes.append(
                {
                    "term_id": tid,
                    "metric": "gdp_pc_rel",
                    "window": [t0 - 1, t0 + 3],
                    "actual": actual,
                    "prior": prior,
                    "baseline": 0.5 * prior,
                    "residual": actual - 0.5 * prior,
                }
            )
    return profiles, outcomes


def validate(name, data):
    Draft7Validator(read_json(ROOT / f"contracts/schemas/{name}.schema.json")).validate(
        data
    )


def test_backtest_finds_planted_signal_and_respects_walk_forward():
    profiles, outcomes = synthetic(signal_strength=0.01)
    rows = backtest.joined_rows(profiles, outcomes, "gdp_pc_rel")
    for year, train, test in backtest.cohorts(rows):
        assert max(r["t0"] for r in train) + 3 <= year - 1
    s = backtest.signal_for("gdp_pc_rel", rows, n_perm=19)
    validate("signal", [s])
    assert s["cohorts"] == [2007, 2011, 2015, 2019]  # 2003 has no ended training terms
    assert s["skill"] > 0.2 and s["skill_ci95"][0] > 0
    assert s["permutation_p"] == 1 / 20
    assert s["brier"]["knn"] < s["brier"]["baseline"]


def test_backtest_on_noise_is_not_significant():
    profiles, outcomes = synthetic(signal_strength=0.0, seed=1)
    s = backtest.signal_for(
        "gdp_pc_rel", backtest.joined_rows(profiles, outcomes, "gdp_pc_rel"), n_perm=19
    )
    assert s["skill_ci95"][0] < 0 < s["skill_ci95"][1] or s["skill"] < 0
    assert s["permutation_p"] > 0.05


def test_forecasts_parity_and_map_validate_against_contracts():
    profiles, outcomes = synthetic(signal_strength=0.01)
    candidate = {
        **profiles[0],
        "id": "zz-2027",
        "kind": "candidate",
        "state": "ZZ",
        "term_start": 2027,
    }
    profiles = profiles + [candidate]
    baseline = {
        "coefs": {
            m: {"a": 0.0, "b": 0.5, "n": 1} for m in ("gdp_pc_rel", "debt_pc_rel")
        },
        "latest_prior": {"ZZ": {"gdp_pc_rel": 0.002, "debt_pc_rel": None}},
        "latest_window": {"gdp_pc_rel": [2021, 2025], "debt_pc_rel": [2014, 2018]},
    }
    fc, parity = forecasts.build(profiles, outcomes, baseline)
    validate("forecasts", fc)
    validate("knn_parity", parity)
    validate("map", pca_map.build(profiles))
    assert (
        fc[0]["baseline"] == 0.001 and fc[0]["neighbours"][0]["id"] == profiles[0]["id"]
    )
    assert len(parity["cases"]) == 5
    assert all(
        c["query"]["id"] != n["id"]
        for c in parity["cases"]
        for n in c["expected"]["neighbours"]
    )
