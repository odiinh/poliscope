"""Write data/interim/ingest/terms.csv: one row per first-of-term speech."""

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOTS = ROOT / "data" / "raw" / "sots"
OUT = ROOT / "data" / "interim" / "ingest" / "terms.csv"
OVERRIDES = json.loads(Path(__file__).with_name("name_overrides.json").read_text())
PARTY = {1: "R", 2: "D", 3: "I"}
SUFFIXES = {"Jr.", "Sr.", "II", "III", "IV"}


def display_name(speaker):
    if speaker in OVERRIDES:
        return OVERRIDES[speaker]
    last, *rest = speaker.split("_")
    given = [t for t in rest if t not in SUFFIXES]
    suffix = [t for t in rest if t in SUFFIXES]
    return " ".join([*given, last, *suffix])


def build(meta):
    m = meta[(meta.type != "sotu") & ~meta.st_id.isin(["NH", "VT"])]
    m = m.sort_values(["st_id", "year"])
    prev = m.groupby("st_id").shift()
    t = m[(prev.elec_year == 1) & (prev.year == m.year - 1)]
    paths = [f"data/raw/sots/speeches_raw/{f}" for f in t.filename]
    return pd.DataFrame(
        {
            "term_id": t.st_id.str.lower() + "-" + t.year.astype(str),
            "state": t.st_id,
            "t0": t.year,
            "name": t.speaker.map(display_name),
            "party": t.party.map(PARTY),
            "speech_path": paths,
            "speech_type": t.type,
            "quality": t.quality,
            "source_url": t.source,
            "n_chars": [len((ROOT / p).read_text(encoding="utf-8")) for p in paths],
        }
    ).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice30", action="store_true")
    ap.parse_args()
    terms = build(pd.read_csv(SOTS / "metadata.csv"))
    assert len(terms) == 259, len(terms)
    assert terms.state.nunique() == 45
    assert terms.term_id.is_unique
    assert (terms.t0 == 2007).sum() == 30
    assert terms.party.notna().all() and (terms.n_chars > 0).all()
    assert display_name("Brown_Edmund_G._'Jerry'_Jr.") == "Edmund G. 'Jerry' Brown Jr."
    # --slice30 is accepted for `make data ARGS=--slice30`; B and C filter t0 == 2007 themselves.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    terms.to_csv(OUT, index=False)
    print(f"wrote {len(terms)} terms to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
