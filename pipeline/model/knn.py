"""Model spec steps 3 and 4: profile distance and the 7-nearest-precedent forecast.

D's TypeScript port (app/src/lib/knn.ts) must mirror this exactly; knn_parity.json checks it.
"""

import numpy as np

K = 7
DISTANCE_FLOOR = 0.05
MIN_SHARED = 5
BAND = (0.1, 0.9)


def distances(q_stance, q_conf, stances, conf):
    """Distance from one profile to each row; NaN where fewer than MIN_SHARED dims are shared."""
    shared = ~np.isnan(q_stance) & ~np.isnan(stances)
    w = np.where(shared, np.minimum(q_conf, conf), 0.0)
    sq = np.where(shared, (q_stance - stances) ** 2, 0.0)
    wsum = w.sum(axis=1)
    ok = (shared.sum(axis=1) >= MIN_SHARED) & (wsum > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(ok, np.sqrt((w * sq).sum(axis=1) / wsum), np.nan)


def weighted_quantile(values, weights, q):
    """Sort ascending; first value whose cumulative normalised weight reaches q."""
    total = 0.0
    for i in np.argsort(values, kind="stable"):
        total += weights[i]
        if total >= q:
            return float(values[i])
    return float(values[np.argmax(values)])


def forecast(baseline, dist, ids, residuals):
    """Forecast dict from distances to candidate neighbours, or None if fewer than K are eligible.

    dist/ids/residuals are aligned arrays; NaN distances are ineligible. Ties break by id.
    """
    eligible = [i for i in range(len(ids)) if not np.isnan(dist[i])]
    if len(eligible) < K:
        return None
    nearest = sorted(eligible, key=lambda i: (dist[i], ids[i]))[:K]
    inv = [1.0 / (dist[i] + DISTANCE_FLOOR) for i in nearest]
    inv_sum = sum(inv)
    weights = [x / inv_sum for x in inv]
    res = [float(residuals[i]) for i in nearest]
    values = np.array([baseline + r for r in res])
    return {
        "baseline": baseline,
        "forecast": baseline + sum(w * r for w, r in zip(weights, res)),
        "p10": weighted_quantile(values, weights, BAND[0]),
        "p90": weighted_quantile(values, weights, BAND[1]),
        "p_above": sum(w for w, v in zip(weights, values) if v > 0),
        "neighbours": [
            {"id": ids[i], "distance": float(dist[i]), "weight": w, "residual": r}
            for i, w, r in zip(nearest, weights, res)
        ],
    }
