"""Brief C steps 6-7: candidate forecasts and the kNN parity fixture for D's TypeScript port.

Reads build/outcomes.json and build/baseline.json; writes build/forecasts.json and build/knn_parity.json.
"""

from pipeline.model import knn
from pipeline.model.common import (
    METRICS,
    load_profiles,
    log,
    read_build,
    stance_matrix,
    write_build,
)

N_PARITY_CANDIDATES = 3
N_PARITY = 5


def forecaster(profiles, outcomes):
    """Return f(query_profile, metric, baseline) -> Forecast or None, against historical precedents."""
    pools = {}
    for metric in METRICS:
        resid = {o["term_id"]: o["residual"] for o in outcomes if o["metric"] == metric}
        hist = [p for p in profiles if p["kind"] == "historical" and p["id"] in resid]
        stances, conf = stance_matrix(hist)
        pools[metric] = (
            [p["id"] for p in hist],
            [resid[p["id"]] for p in hist],
            stances,
            conf,
        )

    def run(query, metric, baseline, note=None):
        ids, resid, stances, conf = pools[metric]
        qs, qc = stance_matrix([query])
        dist = knn.distances(qs[0], qc[0], stances, conf)
        dist[[i == query["id"] for i in ids]] = float("nan")  # never its own precedent
        out = knn.forecast(baseline, dist, ids, resid)
        if out is None:
            log.warning(
                "skip %s %s: fewer than %d eligible precedents",
                query["id"],
                metric,
                knn.K,
            )
            return None
        return {"subject_id": query["id"], "metric": metric, **out, "note": note}

    return run


def candidate_baseline(baseline, state, metric):
    prior = baseline["latest_prior"].get(state, {}).get(metric)
    if prior is None:
        data = "debt" if metric == "debt_pc_rel" else "GDP"
        return 0.0, f"precedent-only: no recent {data} data"
    c = baseline["coefs"][metric]
    return c["a"] + c["b"] * prior, None


def build(profiles, outcomes, baseline):
    run = forecaster(profiles, outcomes)
    candidates = [p for p in profiles if p["kind"] == "candidate"]
    forecasts = []
    for p in candidates:
        for metric in METRICS:
            f = run(p, metric, *candidate_baseline(baseline, p["state"], metric))
            if f:
                forecasts.append(f)

    # Parity: candidates plus historical terms with the most nulls, to exercise the shared-dim rule.
    by_id = {p["id"]: p for p in profiles}
    hist_rows = sorted(
        (o for o in outcomes if o["term_id"] in by_id),
        key=lambda o: (
            -sum(d["stance"] is None for d in by_id[o["term_id"]]["dims"].values()),
            o["term_id"],
            o["metric"],
        ),
    )
    by_key = {(f["subject_id"], f["metric"]): f for f in forecasts}
    cases = []
    for i, p in enumerate(candidates[:N_PARITY_CANDIDATES]):
        f = by_key.get((p["id"], METRICS[i % 2]))
        if f:
            cases.append(
                {
                    "query": p,
                    "metric": f["metric"],
                    "baseline": f["baseline"],
                    "expected": f,
                }
            )
    seen = set()
    for o in hist_rows:
        if len(cases) >= N_PARITY or o["term_id"] in seen:
            continue
        f = run(by_id[o["term_id"]], o["metric"], o["baseline"])
        if f:
            seen.add(o["term_id"])
            cases.append(
                {
                    "query": by_id[o["term_id"]],
                    "metric": o["metric"],
                    "baseline": o["baseline"],
                    "expected": f,
                }
            )
    return forecasts, {"cases": cases}


def main():
    profiles, _ = load_profiles()
    forecasts, parity = build(profiles, read_build("outcomes"), read_build("baseline"))
    write_build("forecasts", forecasts)
    write_build("knn_parity", parity)
    log.info("forecasts=%d parity_cases=%d", len(forecasts), len(parity["cases"]))


if __name__ == "__main__":
    main()
