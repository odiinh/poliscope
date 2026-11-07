import numpy as np
import pytest

from pipeline.model import knn
from pipeline.model.common import FIXTURES, read_json, stance_matrix


def test_distance_uses_only_shared_dims_weighted_by_min_confidence():
    q = np.array([1.0, 0.0, 0.0, 0.0, 0.0, np.nan, 0, 0, 0, 0])
    qc = np.full(10, 1.0)
    rows = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0, 0, 0, 0]])
    rc = np.array([[0.5] + [1.0] * 9])
    # dim 0 differs by 1 with weight 0.5; 8 other shared dims agree with weight 1
    assert knn.distances(q, qc, rows, rc)[0] == pytest.approx(np.sqrt(0.5 / 8.5))


def test_pairs_with_fewer_than_five_shared_dims_are_skipped():
    q = np.array([0.0] * 4 + [np.nan] * 6)
    assert np.isnan(
        knn.distances(q, np.ones(10), np.zeros((1, 10)), np.ones((1, 10)))[0]
    )


def test_weighted_quantile_takes_first_value_reaching_q():
    values = np.array([3.0, 1.0, 2.0])
    weights = [0.5, 0.05, 0.45]
    assert knn.weighted_quantile(values, weights, 0.1) == 2.0
    assert knn.weighted_quantile(values, weights, 0.05) == 1.0


def test_ties_break_by_id_and_too_few_neighbours_returns_none():
    ids = [f"x{i}" for i in range(8)][::-1]
    out = knn.forecast(0.0, np.zeros(8), ids, np.arange(8.0))
    assert [n["id"] for n in out["neighbours"]] == [f"x{i}" for i in range(7)]
    assert (
        knn.forecast(0.0, np.array([0.1] * 6 + [np.nan] * 2), ids, np.zeros(8)) is None
    )


def test_matches_bootstrap_fixture_forecast():
    profiles = read_json(FIXTURES / "profiles.json")
    outcomes = read_json(FIXTURES / "outcomes.json")
    for expected in read_json(FIXTURES / "forecasts.json"):
        resid = {
            o["term_id"]: o["residual"]
            for o in outcomes
            if o["metric"] == expected["metric"]
        }
        hist = [p for p in profiles if p["id"] in resid]
        query = next(p for p in profiles if p["id"] == expected["subject_id"])
        s, c = stance_matrix(hist)
        qs, qc = stance_matrix([query])
        got = knn.forecast(
            expected["baseline"],
            knn.distances(qs[0], qc[0], s, c),
            [p["id"] for p in hist],
            [resid[p["id"]] for p in hist],
        )
        assert [n["id"] for n in got["neighbours"]] == [
            n["id"] for n in expected["neighbours"]
        ]
        for key in ("forecast", "p10", "p90", "p_above"):
            assert got[key] == pytest.approx(expected[key], abs=1e-9)
