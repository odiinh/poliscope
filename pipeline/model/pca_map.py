"""Brief C step 5: 2-D PCA map of stances. Writes build/map.json.

Nulls become the historical dimension mean, for the map only. The app projects pasted text as
(stances with nulls -> mean - mean) @ components.T.
"""

import numpy as np

from pipeline.model.common import load_profiles, log, stance_matrix, write_build


def build(profiles):
    hist = [p for p in profiles if p["kind"] == "historical"]
    stances, _ = stance_matrix(hist)
    mean = np.nanmean(stances, axis=0)
    assert not np.isnan(mean).any(), "a dimension has no historical stance"
    centred = np.where(np.isnan(stances), mean, stances) - mean
    _, sv, vt = np.linalg.svd(centred, full_matrices=False)
    components = (
        vt[:2] * np.where(vt[:2].sum(axis=1) < 0, -1, 1)[:, None]
    )  # +x leans to the +1 anchors
    explained = sv[:2] ** 2 / (sv**2).sum()

    all_stances, _ = stance_matrix(profiles)
    xy = (np.where(np.isnan(all_stances), mean, all_stances) - mean) @ components.T
    return {
        "mean": mean.tolist(),
        "components": components.tolist(),
        "explained": explained.tolist(),
        "points": [
            {"id": p["id"], "x": float(x), "y": float(y)}
            for p, (x, y) in zip(profiles, xy)
        ],
    }


def main():
    profiles, _ = load_profiles()
    data = build(profiles)
    write_build("map", data)
    log.info(
        "map: %d points, explained=%s",
        len(data["points"]),
        [round(e, 3) for e in data["explained"]],
    )


if __name__ == "__main__":
    main()
