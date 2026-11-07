"""Write reliability.json: verify rate, test-retest r and party AUC.

python -m pipeline.extract.reliability
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from jsonschema import Draft7Validator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict

from pipeline.extract.run_batch import (
    DIM_IDS,
    MAX_CHARS,
    OUT,
    ROOT,
    extract,
    load_env,
    subjects,
)
from pipeline.extract.verify import verify_dims


def stance_pairs(first: dict, second: dict) -> list[tuple[float, float]]:
    """Stance pairs on the dimensions both runs scored."""
    pairs = [(first[d]["stance"], second[d]["stance"]) for d in DIM_IDS]
    return [(a, b) for a, b in pairs if a is not None and b is not None]


def retest(profile: dict, path: str, model: str) -> list[tuple[float, float]]:
    text = (ROOT / path).read_text()
    dims, _, _ = verify_dims(
        extract(text, model, use_cache=False)["dims"], text[:MAX_CHARS]
    )
    return stance_pairs(profile["dims"], dims)


def main():
    load_env()
    model = os.environ.get("LLM_MODEL_BATCH") or "haiku"
    profiles = json.loads((OUT / "profiles.json").read_text())
    hist = [p for p in profiles if p["kind"] == "historical"]

    log = pd.read_csv(OUT / "extract_log.csv")
    log = log[(log.status != "error") & log.id.isin([p["id"] for p in profiles])]
    log = log.drop_duplicates("id", keep="last")
    verify_rate = log.kept.sum() / max(log.given.sum(), 1)

    paths = {s["id"]: s["path"] for s in subjects("all")}
    sample = pd.Series([p for p in hist if p["id"] in paths]).sample(
        n=min(30, len(hist)), random_state=7
    )
    workers = int(os.environ.get("LLM_CONCURRENCY") or 8)
    with ThreadPoolExecutor(workers) as pool:
        runs = pool.map(lambda p: retest(p, paths[p["id"]], model), sample)
    pairs = np.array([pair for run in runs for pair in run])
    test_retest_r = float(np.corrcoef(pairs[:, 0], pairs[:, 1])[0, 1])

    # nulls as 0 for this check only, as the plan says
    two_party = [p for p in hist if p["party"] in ("D", "R")]
    x = np.array([[p["dims"][d]["stance"] or 0.0 for d in DIM_IDS] for p in two_party])
    y = np.array([p["party"] == "R" for p in two_party])
    proba = cross_val_predict(LogisticRegression(), x, y, cv=5, method="predict_proba")
    party_auc = float(roc_auc_score(y, proba[:, 1]))

    out = {
        "n_profiles": len(profiles),
        "verify_rate": round(float(verify_rate), 4),
        "test_retest_r": round(test_retest_r, 4),
        "party_auc": round(party_auc, 4),
    }
    schema = json.loads(
        (ROOT / "contracts/schemas/reliability.schema.json").read_text()
    )
    Draft7Validator(schema).validate(out)
    (OUT / "reliability.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out, f"retest pairs {len(pairs)}", file=sys.stderr)


if __name__ == "__main__":
    main()
