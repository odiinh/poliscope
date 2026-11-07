"""Shared paths, constants and I/O for the model stage."""

import json
import logging
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "contracts/fixtures"
INGEST = ROOT / "data/interim/ingest"
EXTRACT = ROOT / "data/interim/extract"
BUILD = Path(__file__).resolve().parent / "build"
PUBLIC = ROOT / "data/public"

DIMS = [d["id"] for d in json.loads((ROOT / "contracts/dimensions.json").read_text())]
METRICS = ("gdp_pc_rel", "debt_pc_rel")
SLICE_YEAR = 2007

log = logging.getLogger("model")
logging.basicConfig(
    stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s"
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_build(name, data):
    BUILD.mkdir(exist_ok=True)
    (BUILD / f"{name}.json").write_text(
        json.dumps(data, indent=1) + "\n", encoding="utf-8"
    )


def read_build(name):
    path = BUILD / f"{name}.json"
    if not path.exists():
        sys.exit(f"{path} missing: run python -m pipeline.model.outcomes first")
    return read_json(path)


def load_profiles():
    """B's profiles if present, otherwise the contract fixtures."""
    real = EXTRACT / "profiles.json"
    if real.exists():
        return read_json(real), True
    log.warning("using fixture profiles: %s not found", real)
    return read_json(FIXTURES / "profiles.json"), False


def stance_matrix(profiles):
    """Stances (NaN = null) and confidences as two (n, 10) arrays in DIMS order."""
    stances = np.array(
        [
            [
                np.nan if p["dims"][d]["stance"] is None else p["dims"][d]["stance"]
                for d in DIMS
            ]
            for p in profiles
        ],
        dtype=float,
    ).reshape(len(profiles), len(DIMS))
    conf = np.array(
        [[p["dims"][d]["confidence"] for d in DIMS] for p in profiles], dtype=float
    ).reshape(len(profiles), len(DIMS))
    return stances, conf


def slice_arg():
    return "--slice30" in sys.argv[1:]
