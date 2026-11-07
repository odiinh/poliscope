"""Brief C steps 1-2: per-term outcomes, the prior-trend baseline, and each state's latest prior.

Writes build/outcomes.json and build/baseline.json. Falls back to the fixtures until A's panel lands.
"""

import numpy as np
import pandas as pd

from pipeline.model.common import (
    FIXTURES,
    INGEST,
    METRICS,
    SLICE_YEAR,
    load_profiles,
    log,
    read_json,
    slice_arg,
    write_build,
)

SPAN = 4
GDP_LATEST_WINDOW = (2021, 2025)
# Debt data ending here or earlier is too old to give a 2027 candidate a baseline.
STALE_DEBT_YEAR = 2018


def growth(series, start, end):
    """Annualised log growth of a year-indexed Series; NaN if either end is missing."""
    a, b = series.get(start, np.nan), series.get(end, np.nan)
    return (np.log(b) - np.log(a)) / (end - start)


def relative_growth(panel):
    """Return f(metric, state, start, end) -> state growth minus its benchmark, or NaN."""
    us = panel.groupby("year").apply(
        lambda g: (
            g.rgdp_musd2017.sum() * 1e6 / g["pop"].sum()
            if g.rgdp_musd2017.notna().all() and g["pop"].notna().all()
            else np.nan
        ),
        include_groups=False,
    )
    by_state = {
        metric: panel.pivot(index="year", columns="state", values=col)
        for metric, col in (("gdp_pc_rel", "gdp_pc"), ("debt_pc_rel", "debt_pc"))
    }

    def rel(metric, state, start, end):
        wide = by_state[metric]
        if state not in wide or start not in wide.index or end not in wide.index:
            return np.nan
        own = growth(wide[state], start, end)
        if metric == "gdp_pc_rel":
            return own - growth(us, start, end)
        others = (np.log(wide.loc[end]) - np.log(wide.loc[start])) / (end - start)
        return own - others.dropna().median()

    return rel


def fit(rows):
    x = np.array([r["prior"] for r in rows])
    y = np.array([r["actual"] for r in rows])
    b, a = np.polyfit(x, y, 1)
    return {"a": float(a), "b": float(b), "n": len(rows)}


def build_outcomes(terms, panel):
    rel = relative_growth(panel)
    rows = []
    for t in terms.itertuples():
        for metric in METRICS:
            actual = rel(metric, t.state, t.t0 - 1, t.t0 + 3)
            prior = rel(metric, t.state, t.t0 - 5, t.t0 - 1)
            if np.isnan(actual) or np.isnan(prior):
                log.info(
                    "skip %s %s: missing panel year in %d-%d",
                    t.term_id,
                    metric,
                    t.t0 - 5,
                    t.t0 + 3,
                )
                continue
            rows.append(
                {
                    "term_id": t.term_id,
                    "metric": metric,
                    "window": [t.t0 - 1, t.t0 + 3],
                    "actual": float(actual),
                    "prior": float(prior),
                }
            )
    coefs = {m: fit([r for r in rows if r["metric"] == m]) for m in METRICS}
    for r in rows:
        c = coefs[r["metric"]]
        r["baseline"] = c["a"] + c["b"] * r["prior"]
        r["residual"] = r["actual"] - r["baseline"]
    return rows, coefs, rel


def build_baseline(panel, coefs, rel):
    debt_years = panel.loc[panel.debt_pc.notna(), "year"]
    debt_end = int(debt_years.max())
    windows = {
        "gdp_pc_rel": GDP_LATEST_WINDOW,
        "debt_pc_rel": (debt_end - SPAN, debt_end),
    }
    latest = {}
    for state in sorted(panel.state.unique()):
        latest[state] = {}
        for metric, (start, end) in windows.items():
            value = rel(metric, state, start, end)
            stale = metric == "debt_pc_rel" and end <= STALE_DEBT_YEAR
            latest[state][metric] = None if stale or np.isnan(value) else float(value)
    return {
        "coefs": coefs,
        "latest_prior": latest,
        "latest_window": {m: list(w) for m, w in windows.items()},
    }


def load_terms():
    path = INGEST / "terms.csv"
    if path.exists():
        return pd.read_csv(path, usecols=["term_id", "state", "t0"])
    profiles, _ = load_profiles()
    log.warning("using profile ids as terms: %s not found", path)
    return pd.DataFrame(
        [
            {"term_id": p["id"], "state": p["state"], "t0": p["term_start"]}
            for p in profiles
            if p["kind"] == "historical"
        ]
    )


def main():
    panel_path = INGEST / "panel.csv"
    if not panel_path.exists():
        log.warning("using fixture outcomes and baseline: %s not found", panel_path)
        write_build("outcomes", read_json(FIXTURES / "outcomes.json"))
        write_build("baseline", read_json(FIXTURES / "baseline.json"))
        return
    terms = load_terms()
    if slice_arg():
        terms = terms[terms.t0 == SLICE_YEAR]
    panel = pd.read_csv(panel_path)
    rows, coefs, rel = build_outcomes(terms, panel)
    write_build("outcomes", rows)
    write_build("baseline", build_baseline(panel, coefs, rel))
    for m in METRICS:
        log.info(
            "%s: n=%d a=%.5f b=%.3f", m, coefs[m]["n"], coefs[m]["a"], coefs[m]["b"]
        )


if __name__ == "__main__":
    main()
