"""Fetch raw sources into data/raw/, skipping files already present."""

import io
import json
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from pipeline.ingest.env import env

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SOTS_ZIP = "https://codeload.github.com/leops95/sots/zip/refs/heads/master"
DEBT_URL = (
    "https://raw.githubusercontent.com/jacobkap/government_finances/master/"
    "data/government_finances_1992_2018.csv"
)
# fredgraph.csv drops non-browser clients, so use the official API (free key).
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]
FRED_IDS_PATH = Path(__file__).with_name("fred_ids.json")


def get(url):
    r = requests.get(url, timeout=120, headers={"User-Agent": "poliscope-ingest"})
    r.raise_for_status()
    return r.content


def fred_ids():
    overrides = json.loads(FRED_IDS_PATH.read_text()) if FRED_IDS_PATH.exists() else {}
    ids = {f"{s}_{k}": f"{s}{k}" for s in STATES for k in ("RGSP", "POP")}
    return ids | overrides


def fetch_fred(item):
    key, series = item
    path = RAW / "fred" / f"{key}.csv"
    if path.exists():
        return None
    params = {"series_id": series, "api_key": env("FRED_API_KEY"), "file_type": "json"}
    try:
        r = requests.get(FRED_API, params=params, timeout=60)
        r.raise_for_status()
        obs = r.json()["observations"]
    except (requests.RequestException, KeyError, ValueError) as e:
        return f"{key} ({series}): {str(e).split('api_key=')[0]}"
    rows = [f"{o['date']},{'' if o['value'] == '.' else o['value']}" for o in obs]
    path.write_text("\n".join([f"observation_date,{series}", *rows]) + "\n")
    return None


def main():
    (RAW / "fred").mkdir(parents=True, exist_ok=True)
    sots = RAW / "sots"
    if not sots.exists():
        with zipfile.ZipFile(io.BytesIO(get(SOTS_ZIP))) as z:
            z.extractall(RAW / "_sots_tmp")
        shutil.move(next((RAW / "_sots_tmp").iterdir()), sots)
        (RAW / "_sots_tmp").rmdir()
    debt = RAW / "government_finances_1992_2018.csv"
    if not debt.exists():
        debt.write_bytes(get(DEBT_URL))
    if not env("FRED_API_KEY"):
        print(
            "FRED_API_KEY missing: add it to .env.local (free at fredaccount.stlouisfed.org)"
        )
        return 1
    with ThreadPoolExecutor(2) as pool:  # API limit is 120 requests a minute
        failures = [f for f in pool.map(fetch_fred, fred_ids().items()) if f]
    for f in failures:
        print("FRED failed:", f)
    print(f"raw data in {RAW}; {len(failures)} FRED failures")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
