"""Keep only evidence quotes that are exact substrings of the source text."""

import re

TRANSLATE = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",
        "′": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "″": '"',
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "―": "-",
        "−": "-",
    }
)
EMPTY = {"stance": None, "salience": 0.0, "confidence": 0.0, "evidence": []}


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(TRANSLATE)).strip()


def verify_dims(dims: dict, source: str) -> tuple[dict, int, int]:
    """Return (dims with only verified quotes, quotes kept, quotes given)."""
    haystack = normalise(source)
    out, kept, given = {}, 0, 0
    for dim_id, score in dims.items():
        quotes = [q.strip() for q in score.get("evidence") or [] if q.strip()]
        given += len(quotes)
        good = [q for q in quotes if len(q.split()) <= 40 and normalise(q) in haystack]
        good = good[:3]
        kept += len(good)
        if score.get("stance") is None or not good:
            out[dim_id] = dict(EMPTY, evidence=[])
        else:
            out[dim_id] = {
                "stance": max(-1.0, min(1.0, float(score["stance"]))),
                "salience": max(0.0, min(1.0, float(score["salience"]))),
                "confidence": max(0.0, min(1.0, float(score["confidence"]))),
                "evidence": good,
            }
    return out, kept, given
