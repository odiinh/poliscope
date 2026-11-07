"""Brief C step 4: walk-forward backtest by election cohort. Writes build/signal.json.

Models per test term: baseline, baseline + same-party mean residual, kNN, ridge on stances, and
kNN on shuffled training profiles (permutation test). The baseline is refit per cohort.
"""

import numpy as np
from sklearn.linear_model import Ridge

from pipeline.model import knn
from pipeline.model.common import (
    METRICS,
    load_profiles,
    log,
    read_build,
    stance_matrix,
    write_build,
)
from pipeline.model.outcomes import fit

MIN_TEST = 8
MIN_TRAIN = 30
N_PERMUTATIONS = 200
N_BOOTSTRAP = 1000
BOOTSTRAP_SEED = 42
RIDGE_ALPHA = 1.0
CALIBRATION_BINS = 5


def cohorts(rows):
    """Yield (year, train, test) where train windows ended before year: t0 + 3 <= year - 1."""
    for year in sorted({r["t0"] for r in rows}):
        test = [r for r in rows if r["t0"] == year]
        train = [r for r in rows if r["t0"] + 3 <= year - 1]
        if len(test) >= MIN_TEST and len(train) >= MIN_TRAIN:
            yield year, train, test


def score_cohort(train, test):
    """Predictions for each test term (None for terms kNN cannot score), plus shuffled-kNN MAE parts."""
    coef = fit(train)
    resid = np.array([r["actual"] - coef["a"] - coef["b"] * r["prior"] for r in train])
    ids = [r["term_id"] for r in train]
    s_tr, c_tr = stance_matrix([r["profile"] for r in train])
    s_te, c_te = stance_matrix([r["profile"] for r in test])
    dist = np.array(
        [knn.distances(s_te[i], c_te[i], s_tr, c_tr) for i in range(len(test))]
    )
    party_mean = {
        p: resid[[r["party"] == p for r in train]].mean()
        for p in {r["party"] for r in train}
    }
    ridge = Ridge(alpha=RIDGE_ALPHA).fit(np.nan_to_num(s_tr), resid)
    ridge_pred = ridge.predict(np.nan_to_num(s_te))

    scored = []
    for i, r in enumerate(test):
        b = coef["a"] + coef["b"] * r["prior"]
        f = knn.forecast(b, dist[i], ids, resid)
        if f is None:
            log.info("backtest skip %s: fewer than %d precedents", r["term_id"], knn.K)
            continue
        scored.append(
            {
                "i": i,
                "actual": r["actual"],
                "baseline": b,
                "party": b + party_mean.get(r["party"], 0.0),
                "knn": f["forecast"],
                "ridge": b + ridge_pred[i],
                "p_knn": f["p_above"],
                "p_base": float(np.mean(b + resid > 0)),
            }
        )
    return scored, (dist, ids, resid)


def shuffled_errors(cohort_parts, n_perm):
    """Absolute errors per permutation run, pooled over cohorts in order; seed s drives run s."""
    errors = np.zeros((n_perm, sum(len(scored) for scored, _ in cohort_parts)))
    for seed in range(n_perm):
        rng = np.random.default_rng(seed)
        col = 0
        for scored, (dist, ids, resid) in cohort_parts:
            perm = rng.permutation(len(ids))
            # shuffling profiles among training terms = permuting distance columns against fixed residuals
            for s in scored:
                f = knn.forecast(s["baseline"], dist[s["i"]][perm], ids, resid)
                pred = s["baseline"] if f is None else f["forecast"]
                errors[seed, col] = abs(pred - s["actual"])
                col += 1
    return errors


def calibration(p, y):
    edges = np.linspace(0, 1, CALIBRATION_BINS + 1)
    bins = np.clip(np.digitize(p, edges) - 1, 0, CALIBRATION_BINS - 1)
    return [
        {
            "bin_mid": float((edges[b] + edges[b + 1]) / 2),
            "predicted": float(p[bins == b].mean()),
            "observed": float(y[bins == b].mean()),
            "n": int((bins == b).sum()),
        }
        for b in range(CALIBRATION_BINS)
        if (bins == b).any()
    ]


def signal_for(metric, rows, n_perm=N_PERMUTATIONS):
    parts = []
    years = []
    for year, train, test in cohorts(rows):
        scored, ctx = score_cohort(train, test)
        parts.append((scored, ctx))
        years.append(year)
    scored = [s for part, _ in parts for s in part]
    if not scored:
        log.warning(
            "%s: no cohort has %d test and %d training terms",
            metric,
            MIN_TEST,
            MIN_TRAIN,
        )
        return None
    col = {k: np.array([s[k] for s in scored]) for k in scored[0]}
    actual = col["actual"]
    err = {m: np.abs(col[m] - actual) for m in ("baseline", "party", "knn", "ridge")}
    mae = {m: float(e.mean()) for m, e in err.items()}

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.integers(0, len(actual), size=(N_BOOTSTRAP, len(actual)))
    boot = 1 - err["knn"][draws].mean(axis=1) / err["baseline"][draws].mean(axis=1)
    shuffled_mae = shuffled_errors(parts, n_perm).mean(axis=1)
    above = (actual > 0).astype(float)
    return {
        "metric": metric,
        "n_test": len(scored),
        "cohorts": years,
        "mae": mae,
        "skill": 1 - mae["knn"] / mae["baseline"],
        "skill_ci95": [
            float(np.percentile(boot, 2.5)),
            float(np.percentile(boot, 97.5)),
        ],
        "skill_vs_party": 1 - mae["knn"] / mae["party"],
        "permutation_p": (1 + int((shuffled_mae <= mae["knn"]).sum())) / (n_perm + 1),
        "brier": {
            "baseline": float(np.mean((col["p_base"] - above) ** 2)),
            "knn": float(np.mean((col["p_knn"] - above) ** 2)),
        },
        "calibration": calibration(col["p_knn"], above),
    }


def joined_rows(profiles, outcomes, metric):
    by_id = {p["id"]: p for p in profiles if p["kind"] == "historical"}
    return [
        {
            **o,
            "t0": by_id[o["term_id"]]["term_start"],
            "party": by_id[o["term_id"]]["party"],
            "profile": by_id[o["term_id"]],
        }
        for o in outcomes
        if o["metric"] == metric and o["term_id"] in by_id
    ]


def main():
    profiles, _ = load_profiles()
    outcomes = read_build("outcomes")
    signals = []
    for metric in METRICS:
        s = signal_for(metric, joined_rows(profiles, outcomes, metric))
        if s:
            signals.append(s)
            log.info(
                "%s: n=%d cohorts=%s skill=%.3f ci=[%.3f, %.3f] vs_party=%.3f p=%.3f",
                metric,
                s["n_test"],
                s["cohorts"],
                s["skill"],
                *s["skill_ci95"],
                s["skill_vs_party"],
                s["permutation_p"],
            )
    write_build("signal", signals)


if __name__ == "__main__":
    main()
