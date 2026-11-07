# Member A status
- 22:17 step 1 download: partial (sots + debt ok; FRED requests hang, blocked); step 2 terms: done, 259 rows, 45 states, 30 at t0=2007, R145 D110 I4
- 22:29 step 1 download: done via FRED API (fredgraph.csv drops scripts; needs FRED_API_KEY in .env.local), 102/102 series; step 3 panel: done, 1734 rows (51 x 1992-2025), GDP 1997-2025, debt 1992-2018 (no DC); joinable terms gdp 218, debt 204
- 22:33 step 4 platforms: done, 5 called open-seat winners (fetch_platforms.py, campaign sites, retrieved 2026-11-07): al-2027 Tuberville R 984w, ia-2027 Sand D 10519w, mi-2027 Benson D 2231w, ok-2027 Mazzei R 3304w, sc-2027 Wilson R 1011w. AL/SC under the 1500-word aim (their sites publish no more). Skipped FL/TN (close, possibly uncalled), OH Acton + CO Weiser (sites return 403 to scripts), WY Barlow (310w)
- 22:50 step 6 coverage report: done (below). Step 5 below.
- 23:05 step 5 recent debt: done, rejected. Census API govsstatefin item SF0455 (debt at end of FY, $1,000; must request CATEGORY or the row is dropped; AGG_DESC predicates return nothing; needs CENSUS_API_KEY) gives 50 states x 2012-2024, but only 232/350 state-years in 2012-2018 match the CSV exactly and 54 differ by >1% (max 45%, AR 2017; AZ 2018 13.70M vs 9.44M), i.e. Census revised figures. Per plan, not merged: debt still ends in 2018, candidate debt forecasts stay precedent-only.

## Coverage report

### Speeches to terms (`build_terms`)

| Stage | Kept | Dropped | Why |
| --- | --- | --- | --- |
| leops95/sots metadata | 1,296 speeches | | |
| Drop `type == sotu` | 1,268 | 28 | US presidential State of the Union rows (`st_id` US) |
| Drop NH and VT | 1,216 | 52 | Two-year terms |
| Previous speech in the state was in an election year | 295 | 921 | Not a term start |
| ...and exactly one year earlier | **259 terms, 45 states** | 36 | Gap year in the archive. MT, NC and TX speak only in odd years (biennial sessions), so they never qualify |

259 terms: t0 from 1997 to 2022, 30 at t0 = 2007; party R 145, D 110, I 4; type sots 229, inaug 17, budg 12, other 1; quality "as prepared" 255, ocr 4. Six speaker names are hand-fixed in `pipeline/ingest/name_overrides.json`.

### Terms to outcome windows (`build_panel`; a window needs t0-5, t0-1 and t0+3)

| Metric | Terms with full data | Dropped | Why |
| --- | --- | --- | --- |
| GDP per capita | 218 | 41 | BEA state series starts in 1997 (t0 < 2002) or ends in 2025 (t0 > 2022) |
| Debt per capita | 204 | 55 | Debt file covers 1992-2018 (t0 > 2015), plus no DC rows |

`panel.csv`: 1,734 rows (50 states + DC, 1992-2025). GDP 1997-2025 for all 51; population 1992-2025 for all 51; debt 1992-2018 for the 50 states, none for DC. One Mississippi 2017 debt row had no `state_abb` and is recovered from the state name. Spot check: Alabama 2018 debt is 9,856,082 thousand dollars.

### Governor-elect platforms (`fetch_platforms`, retrieved 2026-11-07)

| candidate_id | Name | Party | Words | Source |
| --- | --- | --- | --- | --- |
| al-2027 | Tommy Tuberville | R | 984 | https://www.coachforgovernor.com/issues |
| ia-2027 | Rob Sand | D | 10,519 | https://robsand.com/priorities (+7 issue pages) |
| mi-2027 | Jocelyn Benson | D | 2,231 | https://www.jocelynbenson.com/issues (+8 issue pages) |
| ok-2027 | Mike Mazzei | R | 3,304 | https://mikeforok.com/the-plan |
| sc-2027 | Alan Wilson | R | 1,011 | https://wilsonforsc.com/priorities |

All five are open seats whose results Ballotpedia reported as decided on 6 Nov 2026. Passed over: FL and TN (close margins; two races were still uncalled), OH (Amy Acton) and CO (Phil Weiser), whose sites return 403 to scripts, and WY (Eric Barlow), whose site has 310 words.

### Sources and licences (for the README)

| Source | URL | Licence or terms |
| --- | --- | --- |
| State of the State speeches | https://github.com/leops95/sots | CC0 1.0 |
| State government finances (debt) | https://github.com/jacobkap/government_finances (from US Census Bureau Annual Survey of State Government Finances) | Repo declares no licence; underlying Census data is public domain, so cite the Census Bureau |
| Real GDP by state (`<ST>RGSP`), BEA via FRED | https://fred.stlouisfed.org/data/USGOVSLRGSP | BEA data is public domain; fetched with the FRED API under its terms of use |
| State population (`<ST>POP`), Census via FRED | https://fred.stlouisfed.org | Census data is public domain; FRED API terms of use |
| 2026 results | https://ballotpedia.org/Gubernatorial_elections,_2026 | Cited, not redistributed |
| Platform texts | Campaign sites above | Copyright of each campaign; used for analysis, app shows only short quotes |
- 23:24 panel budget columns (D approved B's proposal): added tax_kusd/tax_pc (revenue_total_taxes), spend_kusd/spend_pc (total_general_expenditure, excludes insurance-trust payouts), educ_kusd/educ_pc (expenditure_education); nominal thousands, 1992-2018, 50 states, no DC; 204 terms each, same as debt; original 7 columns unchanged
