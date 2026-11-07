"""Write data/interim/ingest/panel.csv: one row per state (50 + DC) and year, 1992-2025."""

import argparse

import pandas as pd

from pipeline.ingest.download import RAW, ROOT, STATES

OUT = ROOT / "data" / "interim" / "ingest" / "panel.csv"
YEARS = range(1992, 2026)


def fred(key):
    df = pd.read_csv(RAW / "fred" / f"{key}.csv")
    year = pd.to_datetime(df.iloc[:, 0]).dt.year
    return pd.Series(df.iloc[:, 1].to_numpy(), index=year).dropna()


def build():
    frames = []
    for st in STATES:
        f = pd.DataFrame(index=pd.Index(YEARS, name="year"))
        f["state"] = st
        f["rgdp_musd2017"] = fred(f"{st}_RGSP")
        f["pop"] = fred(f"{st}_POP") * 1000  # FRED gives thousands of persons
        frames.append(f.reset_index())
    panel = pd.concat(frames)

    debt = pd.read_csv(RAW / "government_finances_1992_2018.csv", low_memory=False)
    # Mississippi 2017 has no state_abb; recover it from the state name.
    abb = debt.dropna(subset=["state_abb"]).groupby("state").state_abb.first()
    debt = debt.assign(state=debt.state.map(abb).str.upper())
    debt = debt[debt.state.notna()]
    debt = debt[debt.state != "US"][["state", "year", "debt_at_end_of_fiscal_year"]]
    assert not debt.duplicated(["state", "year"]).any()
    panel = panel.merge(
        debt.rename(columns={"debt_at_end_of_fiscal_year": "debt_kusd"}),
        on=["state", "year"],
        how="left",
    )
    panel["gdp_pc"] = panel.rgdp_musd2017 * 1e6 / panel["pop"]
    panel["debt_pc"] = panel.debt_kusd * 1000 / panel["pop"]
    cols = ["state", "year", "rgdp_musd2017", "pop", "gdp_pc", "debt_kusd", "debt_pc"]
    return panel[cols].sort_values(["state", "year"]).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice30", action="store_true")  # accepted; panel is always whole
    ap.parse_args()
    panel = build()
    assert len(panel) == 51 * len(YEARS) and panel.state.nunique() == 51
    al = panel.query("state == 'AL' and year == 2018").debt_kusd.item()
    assert al == 9_856_082, al
    OUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT, index=False)
    print(f"wrote {len(panel)} rows to {OUT.relative_to(ROOT)}")
    print(
        panel.drop(columns=["state", "year"])
        .notna()
        .groupby(panel.year)
        .sum()
        .iloc[[0, 5, 26, 33]]
    )


if __name__ == "__main__":
    main()
