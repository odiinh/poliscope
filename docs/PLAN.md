# HackTheBurgh XIII — Team Build Plan

Nov 7, 2026 · @Heechan

## Current handoff

Reviewed 7 November 2026, 23:16 GMT. Read this section before resuming a numbered brief. The repository copy of this plan is the shared source for the team.

### Public state

- The public demo is [poliscope.hydroxide.uk](https://poliscope.hydroxide.uk). It runs on Grimnir in Docker, behind the existing Cloudflare Tunnel. All five candidate pages, both metric views, evidence disclosures, the map, calibration, and a phone-sized browser layout have been checked.
- The shared export has 259 historical profiles, 5 candidates, 218 GDP outcomes, 204 debt outcomes, 10 candidate forecasts, and 5 Python/TypeScript parity cases. The last check passed 13 Python tests and 14 Vitest tests, plus schema validation, ruff, TypeScript, ESLint, and ownership checks.
- Candidates are Tommy Tuberville (AL, R), Rob Sand (IA, D), Jocelyn Benson (MI, D), Mike Mazzei (OK, R), and Alan Wilson (SC, R).
- Extraction reliability is 98.7% quote verification, 0.9591 test–retest correlation, and 0.9036 party AUC. Quote verification measures text matching. A person still needs to check whether the evidence supports the stance.
- Public live extraction is disabled. The home page explains this and `POST /api/extract` returns 503. Local extraction uses an authenticated `claude` CLI. The public container has no authenticated extraction backend.
- The source and outcome pipeline has run on the 30-term slice and the full historical set. Evidence review and demo preparation are the immediate work before G1 at 01:00 on 8 November.

### Results to present

Skill measures the reduction in mean absolute forecast error relative to the comparator.

| Metric | Test terms | Skill vs prior trend | 95% interval | Skill vs party | Permutation p |
| --- | --- | --- | --- | --- | --- |
| GDP per capita relative to US | 129 | −15.7% | −23.6% to −8.7% | −16.1% | 0.995 |
| Debt per capita relative to median state | 128 | −9.3% | −21.7% to 1.6% | −5.2% | 0.398 |

The GDP model increased error in the walk-forward test. Debt's interval includes zero. The pitch should explain the baseline's stronger forecasting performance and show the fingerprints as a way to explore historical commitments. Use `docs/pitch_numbers.md` and `docs/pitch.md`. Keep the registered dimensions, k, distance floor, and backtest constants fixed.

### Changes since the initial plan

| Area | Current implementation and consequence |
| --- | --- |
| Hosting | The user chose Grimnir, Docker, and Cloudflare instead of Vercel. D owns deployment. Pushing to `main` updates the shared code. D then pulls and rebuilds the server image to publish application or data changes. |
| Development versions | Use Python 3.11, Node.js 24, uv, and pnpm 10.34.9. The pnpm version and lockfile are pinned in `app/`. |
| Extraction provider | B implemented `claude-cli` with Haiku for batch and Sonnet for live requests. `LLM_PROVIDER=claude-cli` and a local CLI login are required. An API key alone does not enable the current route. |
| Batch size limit | The current batch approximates 16k tokens with a 64,000-character limit. Live requests accept up to 60,000 characters. B owns any tokenizer change. |
| FRED ingestion | A uses the FRED observations API because the CSV endpoint failed for scripts. A fresh raw-data download needs `FRED_API_KEY` in the root `.env.local`. The committed interim tables let B and C continue without downloading everything. |
| Recent debt | A tested the Census extension and rejected it under the plan's 1% overlap rule. Debt ends in 2018. All five candidate debt forecasts are labelled precedent-only and use a zero baseline. |
| Platform coverage | AL and SC supplied fewer than the target 1,500 words. Their available texts were retained with missing policy dimensions explicit. See A's coverage report. |
| Evidence UI | Evidence opens in a native disclosure under each fingerprint dimension. Historical subject pages show labelled retrospective estimates. The preloaded candidate pages are the stage demo path. |
| App data | `make sync` copies each public file, falling back to its fixture when missing. A generated provenance list prevents fixture outcomes or scores being displayed with real profiles. |
| Live deployment switch | Docker sets `POLISCOPE_LIVE_EXTRACTION_ENABLED=false` during build and runtime. D owns `Dockerfile`, `compose.yaml`, the home-page switch, and `app/src/proxy.ts`. Enabling live analysis requires B's backend, D's image/runtime changes, and a rebuild. |
| Presentation | The two pitch endings, video script, Devpost draft, and real result numbers are in `docs/pitch.md`. Recording, submission, rehearsal, and the two-laptop backup still need completion. |

### Next actions by member

| Member | Next action | Handoff and acceptance |
| --- | --- | --- |
| A · Data | Audit the five demo source pages and historical source links used in neighbour tables. Confirm retrieval metadata and provide a reachable transcript fallback where an original link fails. | Track [issue #3](https://github.com/odiinh/poliscope/issues/3). Record findings in `docs/status/a.md`. Changed text or source metadata goes to B, then through C's export before D deploys it. The recent-debt experiment is complete and rejected. |
| B · Extraction | Review all 37 evidence quotes shorter than five words, including MI's “bringing Rx Kids statewide”, and the five low-coverage historical profiles. Inspect meaning in the source before changing a score. | Track [issue #2](https://github.com/odiinh/poliscope/issues/2). Record corrections or accepted cases in `docs/status/b.md`. Refresh affected profiles and reliability in B-owned folders. Ask C to export revised inputs. A substring match alone cannot establish semantic accuracy. |
| B · Extraction | Implement an authenticated HTTP provider for hosted extraction if credentials are available. Preserve the request, Profile response, quote verifier, and input limits. | Track [issue #1](https://github.com/odiinh/poliscope/issues/1). A valid 2,000-word request must return a schema-valid Profile within 60 seconds on Grimnir. D wires the prompt into the image, passes runtime secrets, rebuilds with live enabled, and checks the browser path. |
| C · Model | Independently check walk-forward cohort boundaries, omitted terms, the baseline/party comparators, and exported numbers. Document the hub-precedent finding without tuning against held-out results. | Keep `docs/pitch_numbers.md` aligned with `signal.json`. After B's evidence changes, run `make export`, regenerate pitch numbers, and push the export plus parity cases. |
| D · App and integration | Clarify the forecast plot's two dot colours and calibration axes, then check the evidence-to-source path after A/B corrections. | Track [issue #4](https://github.com/odiinh/poliscope/issues/4). Keep the current cached demo available. Application or export changes need a checked rebuild and public smoke test. |
| D with the team | Capture the four submission screenshots, record and upload the two-minute demo, rehearse both endings, and finish Devpost with all four members. | Confirm sponsor-entry rules with organisers, test on an actual phone, and place the production build and video on two laptops. Feature freeze remains 09:30 and target submission remains 11:15 on 8 November. |

### Shared development and release procedure

1. Pull `main`, read this handoff and your status file, then use your `a/`, `b/`, `c/`, or `d/` task branch. Keep folder ownership.
2. For local setup, follow `README.md` and copy `.env.example` to root `.env.local`. Local live extraction needs a signed-in Claude CLI. The public site uses the cached candidate path while the hosted backend is pending.
3. A/B update their owned inputs. C is the sole writer of `data/public/` through `make export`. C also runs `python -m pipeline.model.pitch_numbers` when the backtest changes.
4. D runs `make sync && make check`, reviews the UI, and integrates checked commits on `main`. Generated app files are copied inputs and are ignored by Git.
5. D publishes an agreed commit with the following command, then checks the homepage, both metrics, and candidate routes over public HTTPS.

```sh
ssh grimnir 'cd ~/poliscope && git pull --ff-only && docker compose up -d --build && docker compose ps'
```

The service is `poliscope-app-1`, bound to `127.0.0.1:3101`. Cloudflare maps `poliscope.hydroxide.uk` to `http://localhost:3101` on tunnel `1ace05f9-f8ec-4fda-9c8a-343296d15058`. Application updates use that existing route. Use `docker compose logs --tail=100 app` for diagnostics.


## Run this plan with a coding agent

**Each member opens a coding agent such as Claude Code at the repo root and types one line: "I am team member N." The agent maps N to a role, reads that role's brief in Agent briefs near the end of this doc, and works through it without further instructions.** Member 4 goes first and pushes the repo skeleton by 21:30; members 1–3 clone it, then start.

| Member | Role | Brief to follow | Branch prefix |
| --- | --- | --- | --- |
| 1 | A · Data | Member 1 · Data | `a/` |
| 2 | B · Extraction | Member 2 · Extraction | `b/` |
| 3 | C · Model | Member 3 · Model | `c/` |
| 4 | D · App and integration | Member 4 · App and integration | `d/` |

**Setup is complete.** Clone the shared repository and follow the README. D updates this plan through Git after the 21:30 freeze, and every member pulls the updated plan before starting a step.

**Every member, every session.** Paste this line with your own number:

```text
Read AGENTS.md and docs/PLAN.md in full. I am team member N. Work through my brief from the first unfinished step.
```

The agent logs progress in `docs/status/<letter>.md` and resumes from it, so the same line works after a crash, a new session or a sleep shift.

**What the agent will still ask you for:** API keys and logins (LLM provider, GitHub, Cloudflare or Grimnir), a browser task its tools can't do, and any change to `contracts/`. Everything else it decides alone, from the briefs, the contracts and the fallbacks in Risks.

## Verdict

**Keep PoliScope, cut it in half, and change what it predicts.** The idea is distinctive: it turns political text nobody measures into a tested signal, which fits both G-Research and HRT. But the current brief is three projects in one, targets the outcome governors influence least, and gives HRT no decision to judge.

| # | Problem in the current brief | Change |
| --- | --- | --- |
| 1 | Scope: 20 dimensions, 5 outcomes, live analysis, radar, map, explorer and backtest | 10 dimensions, 2 outcomes, 3 screens. Everything else is a stretch goal. |
| 2 | GDP per capita only. It moves mostly with the national cycle and a state's industry mix, so any governor signal will be faint. | Two outcomes, both measured relative to the US: real GDP per capita growth (the hard case) and state debt per capita (a lever governors control). The contrast between the two is the finding. |
| 3 | Look-ahead bias. State of the State speeches come after the election and reflect the economy the governor inherited. | Use only the first speech of each term, start the outcome clock at that speech, and put the state's prior trend in the baseline. |
| 4 | No decision. HRT's brief is predictions *and* decisions. | Output a probability (will this state beat the US this term?) and score it out of sample: skill vs baseline, Brier score, permutation test. |
| 5 | A null result would sink the demo. | A Signal panel shows the backtest honestly. A faint GDP signal is a result, not a failure, and quant judges reward that honesty. |
| 6 | Next.js plus FastAPI means two deploys and an integration seam at 4 am. | Python runs offline and writes JSON. One Next.js app serves it, with one live route for pasted text. |
| 7 | Four people's coding agents with no shared rules produce four styles. | One contracts folder, one shared agent instructions file, folder ownership and mock fixtures from minute one. |

Don't pivot. The idea already fits two tracks and the data is public. What's left is execution risk, and the rest of this plan is built to remove it.

## Track strategy

**Enter G-Research and HRT with one product and two pitch endings. Skip the other five tracks.** G-Research's brief asks three questions this project answers directly. HRT's brief rewards turning alternative data into tested predictions and decisions, which the backtest delivers.

| Track | First prize | Fit | Decision and what their judges need to see |
| --- | --- | --- | --- |
| G-Research: Make the invisible visible | Nintendo Switch 2s | Strong | **Go.** Their slide asks: what data is hidden, how can we find it, what can we do with it. Answer each in one sentence: governors' real commitments; LLM extraction with verified quotes from 259 speeches; precedents and forecasts for any candidate. |
| HRT: Best use of data for predictions and decision making | PlayStation 5s | Good, if rigorous | **Go.** Their slide stresses diverse inputs and statistical models that turn signals into decisions. Show alt data to features to a probability, scored walk-forward against baselines, with a permutation test. |
| Wordsmith: agentic browser-use workflow | AirPods Max | Weak | No. Judged on workflow complexity, then tokens, model and time. A bolt-on agent loses to dedicated entries. |
| Bank of Scotland: Smart cost of living | £150 gift card each | None | No. |
| JetBrains: Help the developer | €350 each | None | No. |
| InstaLILY: adaptive coding agent | Fast-tracked interview + headphones | None | No. |
| Viridien: lithological interval detection | AirPods 5 + £100 of fossils | None | No. |

Two questions for the organisers on Discord tonight: can one project enter two sponsor challenges, and are sponsor demos separate from main judging? The event page also lists Major League Hacking as a sponsor, so check its prize list and claim any that our stack already qualifies for in under 30 minutes.

## The product

**PoliScope turns a governor's words into a 10-number policy fingerprint, finds the past governors who said the same things, and shows what happened to their states, with an honest score for how much that tells you.** Tagline: *Every promise has a precedent.*

The hook is timely. On 3 November 2026, 36 states elected governors, and 19 of those races had no incumbent on the ballot ([Ballotpedia](https://ballotpedia.org/Gubernatorial_elections,_2026)). Their platforms are the newest unmeasured data in American politics.

| Screen | What the judge sees | Wins |
| --- | --- | --- |
| Fingerprint | Pick a governor-elect (preloaded). Local development also supports pasted text. Ten stances from −1 to +1, faded by confidence. Click one to see the exact sentence it came from. | G-Research |
| Precedents | A map of 259 governor terms since 1997 (PCA of the ten stances). The candidate is a star, and its 7 nearest precedents light up, coloured by what happened to their states. Click a dot for name, state, years and outcome. | G-Research |
| Forecast and Signal | For the chosen state and outcome: baseline, precedent-adjusted forecast, 80% band, and the probability the state lands above its benchmark. Beside it, the out-of-sample record: skill vs baseline and vs party, permutation p-value, calibration. | HRT |

Scope, in priority order. Change a dropdown only by team agreement, and never after the 09:30 freeze.

| Item | Priority |
| --- | --- |
| 259 first-of-term speeches turned into profiles with verified quotes | Must |
| Two outcomes, both relative: real GDP per capita (vs US) and state debt per capita (vs median state) | Must |
| Baseline plus 7-nearest-precedent forecast with an 80% band | Must |
| Walk-forward backtest: skill vs baseline and vs party, Brier score, permutation test | Must |
| The three screens above, on real data | Must |
| Five governors-elect preloaded and cached, at least two from each party | Must |
| One methodology panel: sources, caveats, reliability numbers | Must |
| Live extraction of pasted text | Should |
| Ridge-regression comparator and calibration plot | Should |
| Compare two candidates side by side | Should |
| Payrolls as a third outcome (only as the fallback if debt data fails) | Won't |
| More than 10 dimensions, UMAP, any causal claim | Won't |
| Browser agent, user accounts, mobile layout | Won't |

## Architecture and shared contracts

**Python does all the heavy work offline and writes schema-checked JSON. The Next.js app only reads that JSON, plus one live route for pasted text.** Every hand-off between two people is a file with a fixed shape, so nobody ever edits someone else's code.

&#91;embedded content: PoliScope architecture · 4 owners, one JSON hand-off\]

The JSON files in `data/public/` are the only hand-off between pipeline and app. The dashed live path reuses the batch prompt and the same kNN, so pasted text is scored exactly like the preloaded candidates.

### Data sources and gotchas

| Source | Gives us | Gotcha |
| --- | --- | --- |
| [leops95/sots](https://github.com/leops95/sots) (CC0 licence) | 1,296 speech texts with metadata, 1995–2022; median speech is about 6k tokens | The README says `elec_lastyear`, but the CSV column is `elec_year`, which is 1 when the speech year is itself an election year. A term's first speech is the following year's. That gives 259 term-start speeches in 45 states once New Hampshire and Vermont (two-year terms) are dropped. |
| BEA real GDP by state, via [FRED](https://fred.stlouisfed.org/data/USGOVSLRGSP), plus state population | Real GDP per capita, chained 2017 dollars, 1997–2025 | BEA's state series breaks in 1997 ([EIA note](https://www.eia.gov/state/seds/sep_use/notes/use_gdp.pdf)), so never splice older years. With a 4-year prior trend, 218 terms (starting 2002–2022) qualify. Use the sum of states as the US benchmark: it differs from national GDP by overseas federal activity. |
| [jacobkap/government\_finances](https://github.com/jacobkap/government_finances) | `debt_at_end_of_fiscal_year` by state, 1992–2018, one ready CSV in `data/` | Ends in 2018, so debt outcomes cover terms starting 1997–2015: 204 terms. |
| [Ballotpedia](https://ballotpedia.org/Gubernatorial_elections,_2026) and campaign websites | 2026 governor-elect platforms for the demo | Save the URL and retrieval date with every text. |

### The 10 dimensions

D turns this table into `contracts/dimensions.json` at 21:30; after that it is frozen. On every dimension the conventionally progressive position is −1 and the conventionally conservative one is +1, so the map's first axis is readable. The UI shows only the two anchors, never "left" or "right".

| id | Dimension | −1 means | +1 means |
| --- | --- | --- | --- |
| `tax` | Taxes | Raise taxes or make them more progressive | Cut rates or narrow the base |
| `spending` | Public spending | Expand programmes and budgets | Cut or cap spending |
| `borrowing` | Debt and reserves | Borrow or issue bonds to invest | Pay down debt, build rainy-day funds |
| `regulation` | Business regulation | Add rules on business | Deregulate, cut red tape |
| `labour` | Work and wages | Raise minimum wages, strengthen unions | Right-to-work, employer flexibility |
| `health` | Health care | Expand public coverage such as Medicaid | Market-based, limit public coverage |
| `education` | Schools | Invest in public schools | Expand school choice and vouchers |
| `justice` | Crime and justice | Rehabilitation, sentencing reform | Tougher enforcement and sentencing |
| `energy` | Energy and environment | Climate rules and renewables | Fossil fuel development, fewer rules |
| `infrastructure` | Infrastructure | Large public investment programmes | Limit public investment, private delivery |

Per dimension, a profile holds a stance from −1 to +1 or null (not mentioned, never 0), salience and confidence from 0 to 1, and 1–3 verbatim quotes of at most 40 words. Code checks each quote is an exact substring of the source after whitespace normalisation and drops it if not. A stance with no surviving quote becomes null.

### Files that cross between people

| File | Written by | Read by | Notes |
| --- | --- | --- | --- |
| `contracts/dimensions.json` | D, at bootstrap | everyone | From the dimension table; frozen at 21:30 |
| `contracts/schemas/*.schema.json` | D, at bootstrap | everyone | One JSON Schema per contract type below |
| `contracts/fixtures/*.json` | D, at bootstrap | everyone, until real files land | Valid fake data for every type: 12 historical profiles and 1 candidate |
| `contracts/prompt/extract_v1.md` | B | B (batch and live route) | One prompt for both paths |
| `data/interim/ingest/terms.csv` | A, by 22:30 | B, C | One row per term-start speech |
| `data/interim/ingest/panel.csv` | A | C | State-year panel |
| `data/interim/ingest/platforms.csv` and `platforms/*.txt` | A | B | Governor-elect texts |
| `data/interim/extract/profiles.json` and `reliability.json` | B | C | Profile\[\] and Reliability |
| `data/public/*.json` | C, only via `make export` | D, via `make sync` | profiles, outcomes, baseline, forecasts, signal, map, reliability, knn\_parity |
| `app/src/generated/*` | D, only via `make sync` | app code | Copies of dimensions, prompt and `data/public/`, falling back to fixtures for any missing file |

### Contract types

These types are canonical. D generates the JSON Schemas from them at bootstrap, and every stage validates against those schemas.

```ts
type DimId = "tax" | "spending" | "borrowing" | "regulation" | "labour"
  | "health" | "education" | "justice" | "energy" | "infrastructure"; // this order everywhere
type Metric = "gdp_pc_rel" | "debt_pc_rel";
type Party = "D" | "R" | "I";

// CSV files: UTF-8, header row, empty cell = missing
// data/interim/ingest/terms.csv     term_id, state, t0, name, party, speech_path,
//                                   speech_type, quality, source_url, n_chars  (259 rows)
// data/interim/ingest/panel.csv     state, year, rgdp_musd2017, pop, gdp_pc, debt_kusd,
//                                   debt_pc  (50 states + DC, 1992-2025)
// data/interim/ingest/platforms.csv candidate_id, name, state, party, url, retrieved_at,
//                                   text_path, n_chars  (5 rows)

interface DimScore {
  stance: number | null;    // -1..1, null = not mentioned
  salience: number;         // 0..1
  confidence: number;       // 0..1
  evidence: string[];       // 0-3 verbatim quotes, each <= 40 words
}
interface Profile {         // profiles.json: Profile[], sorted by id
  id: string;               // term_id like "oh-2011", or candidate_id like "az-2027"
  kind: "historical" | "candidate";
  name: string; state: string; party: Party; term_start: number;
  source: { type: string; year: number; url: string; sha1: string };
  dims: Record<DimId, DimScore>;
  extractor: { model: string; prompt_version: string };
}
interface Outcome {         // outcomes.json: Outcome[]
  term_id: string; metric: Metric;
  window: [number, number]; // [t0 - 1, t0 + 3]
  actual: number; prior: number;  // annualised log growth minus benchmark
  baseline: number; residual: number;
}
interface Baseline {        // baseline.json
  coefs: Record<Metric, { a: number; b: number; n: number }>;
  latest_prior: Record<string, Record<Metric, number | null>>; // keyed by state code
  latest_window: Record<Metric, [number, number]>;
}
interface Neighbour { id: string; distance: number; weight: number; residual: number }
interface Forecast {        // forecasts.json: Forecast[]
  subject_id: string; metric: Metric;
  baseline: number; forecast: number; p10: number; p90: number; p_above: number;
  neighbours: Neighbour[];  // 7, nearest first
  note: string | null;      // e.g. "precedent-only: no recent debt data"
}
interface Signal {          // signal.json: Signal[], one per metric
  metric: Metric; n_test: number; cohorts: number[];
  mae: { baseline: number; party: number; knn: number; ridge: number | null };
  skill: number; skill_ci95: [number, number];   // kNN vs baseline
  skill_vs_party: number; permutation_p: number;
  brier: { baseline: number; knn: number };
  calibration: { bin_mid: number; predicted: number; observed: number; n: number }[];
}
interface MapData {         // map.json
  mean: number[]; components: [number[], number[]]; explained: [number, number];
  points: { id: string; x: number; y: number }[];
}
interface Reliability {     // reliability.json
  n_profiles: number; verify_rate: number; test_retest_r: number; party_auc: number;
}
interface KnnParity {       // knn_parity.json
  cases: { query: Profile; metric: Metric; baseline: number; expected: Forecast }[];
}
```

- **Slice:** the 30-term slice is every term with t0 = 2007, exactly 30 terms. Every stage accepts `--slice30`.
- **Constants:** k = 7; distance floor 0.05; at least 5 shared dimensions; band quantiles 0.1 and 0.9; distance ties broken by id; 200 permutations (seeds 0–199); 1,000 bootstrap draws (seed 42); test–retest sample of 30 (seed 7).
- **Weighted quantile q:** sort values ascending and take the first whose cumulative normalised weight reaches q.

Profile (placeholder values; `kind` is historical or candidate, `party` is D, R or I):

```json
{
  "id": "oh-2011",
  "kind": "historical",
  "name": "Firstname Surname",
  "state": "OH",
  "party": "R",
  "term_start": 2011,
  "source": {"type": "sots", "year": 2011, "url": "https://...", "sha1": "..."},
  "dims": {
    "tax": {"stance": 0.6, "salience": 0.8, "confidence": 0.9,
            "evidence": ["Exact sentence copied from the speech."]},
    "health": {"stance": null, "salience": 0.0, "confidence": 0.0, "evidence": []}
  },
  "extractor": {"model": "...", "prompt_version": "v1"}
}
```

Forecast (placeholder values; metric is `gdp_pc_rel` or `debt_pc_rel`):

```json
{
  "subject_id": "az-2027",
  "metric": "debt_pc_rel",
  "baseline": -0.002,
  "forecast": 0.006,
  "p10": -0.011,
  "p90": 0.019,
  "p_above": 0.62,
  "neighbours": [
    {"id": "oh-2011", "distance": 0.21, "weight": 0.31, "residual": 0.009}
  ],
  "note": null
}
```

### Model spec

C builds every step in Python. D mirrors steps 3 and 4 in TypeScript for pasted text, and a parity fixture from C proves both give the same neighbours.

1. **Outcome.** Annualised log growth from year t0−1 to t0+3, where t0 is the year of the term's first speech, minus the US (GDP per capita) or minus the median state (debt per capita). 0.004 means 0.4 percentage points a year.
2. **Baseline.** Regress the outcome on the same measure over the 4 years before t0, fitted only on terms whose window had already ended.
3. **Distance** between profiles A and B, over dimensions both mention (at least 5, otherwise skip the pair):

```latex
d(A,B)=\sqrt{\frac{\sum_i w_i\,(s_{A,i}-s_{B,i})^2}{\sum_i w_i}},\qquad w_i=\min(c_{A,i},\,c_{B,i})
```

4. **Forecast.** Baseline plus the weighted mean residual of the 7 nearest precedents. k = 7 and the 0.05 floor are fixed now, before anyone sees results. The 80% band is the weighted 10th–90th percentile of baseline plus residual, and p\_above is the weighted share above zero.

```latex
\hat y_A=\hat y^{\,base}_A+\sum_{j\in N_7(A)}\omega_j\,r_j,\qquad \omega_j\propto\frac{1}{d(A,j)+0.05}
```

5. **Backtest.** Walk forward by election cohort (for example 2007, 2011, 2015, 2019), training only on terms whose outcome window had ended. Compare baseline, baseline plus party-mean residual, kNN, ridge regression on the ten stances, and kNN on shuffled profiles (200 shuffles give the permutation p-value). Report MAE, skill = 1 − MAE/MAE of baseline with a bootstrap 95% CI, Brier score for p\_above, and calibration.
6. **Map.** PCA on historical stances, with nulls set to the dimension mean for the map only. Export the mean and components so the app places a pasted text with the same projection.

### Conventions

- **IDs:** `{state lowercase}-{t0}`. There is one term start per state and year, so IDs are unique; never parse names into IDs. Data fields use two-letter state codes in capitals.
- **Keys and types:** snake\_case in all JSON. TypeScript types are generated from `contracts/schemas` with `pnpm gen:types`, never hand-written.
- **Missing data:** unknown is null, never 0. A missing data point drops the row and logs why; nothing is imputed silently.
- **Copy:** neutral words such as "precedent" and "associated with". No rankings, no good or bad governors, no causal verbs.
- **Look:** one font, shadcn/ui and Tailwind tokens in one theme file, Recharts only, and a diverging colour scale centred on zero for outcomes. Party is a text label or a neutral-toned toggle, never red and blue fills.

## Team roles

**Each member owns one stage and the folders behind it, and the ownership check in `make check` blocks any commit that touches someone else's folders.** Member 4 is also integration lead and creates the repo. Each member also owns their own status file, `docs/status/<letter>.md`. What each member does, step by step, is in Agent briefs.

| Member · role | Owns (only edits) |
| --- | --- |
| **1 · A · Data** | `pipeline/ingest/`, `data/raw/` (git-ignored), `data/interim/ingest/` |
| **2 · B · Extraction** | `pipeline/extract/`, `contracts/prompt/`, `data/interim/extract/`, `app/src/app/api/extract/` |
| **3 · C · Model** | `pipeline/model/`, `data/public/`, `docs/pitch_numbers.md` |
| **4 · D · App and integration** | Everything else: repo root files, `contracts/` except `prompt/`, `app/` except the extract route, `scripts/`, `docs/` |

On stage, D presents and C takes the statistics questions. A and B run the backup laptop with the video.

### Initial setup checklist

- [ ] Everyone, 10 minutes: read Verdict and The product, and edit the dimension table if you disagree. It freezes at 21:30.
- [x] Member 4 completed the repo setup, shared the URL, and deployed the public cached demo. See Current handoff for the next work.
- [x] Members 1–3 started their briefs and pushed the ingest, extraction, and model outputs.
- [x] Member 2 completed the batch using a locally authenticated Claude CLI. The public API backend is tracked separately in issue #1.
- [ ] Anyone: ask the organisers on Discord about entering two sponsor challenges and how sponsor judging is scheduled.

## Timeline

**Prove the whole pipeline on 30 terms by 01:00, freeze features at 09:30, and submit by 11:15.** A gate is a check, not a meeting: if it fails, take its fallback from Risks and keep moving.

| Gate | Time | Passes when | If it fails |
| --- | --- | --- | --- |
| G0 | 22:00 | Repo bootstrapped; contracts, schemas and fixtures on `main`; app deployed on fixtures; raw data downloaded; LLM key works | Everyone keeps building on fixtures while member 4 clears the blocker |
| G1 | 01:00 | The 30-term slice runs from speech to profile to outcome to forecast to screen, on real data | Apply the matching fallback in Risks; if still failing at 01:30, drop the debt outcome and keep GDP |
| G2 | 05:30 | 259 historical and 5 candidate profiles verified; outcomes for both metrics; `signal.json` exists; every screen on real data | Demo the fingerprint and map for G-Research, and show the backtest as preliminary |
| G3 | 09:30 | Feature freeze: bug fixes, copy and rehearsal only | Hide any unfinished feature rather than ship it half-done |
| G4 | 11:15 | Submitted on Devpost | Submit whatever is deployed; keep editing until 12:00 |

Between the gates: 21:00–22:00 lock, 22:00–01:00 thin slice, 01:00–05:30 scale, 05:30–09:30 harden, 09:30–11:15 ship, then 45 minutes of buffer.

Sleep is part of the plan. A and B sleep 02:30–05:30, once the batch runs unattended; C and D sleep 05:30–08:00, after G2. A rested presenter is worth more than one extra feature.

## Git and merge rules

**Folder ownership plus schema-checked files make merges boring, which is the goal.** Every rule here exists to prevent a merge conflict at 04:00.

1. One repo. `main` is always deployable. D publishes checked changes to Grimnir using the release procedure in Current handoff. The server image is rebuilt after pulling the agreed commit.
2. One branch per task, named `<letter>/<task>`, such as `b/batch-extract`. Rebase on `main` before merging, and merge small changes at least every two hours.
3. Edit only your own folders (see Team roles). If you need a change elsewhere, ask the owner in chat.
4. `contracts/` changes need one reviewer and a chat message. Add fields; never rename a field or change its meaning. Bump `contract_version`.
5. `data/public/` is written only by `make export`. Never hand-edit it; on a conflict, take either side and re-run the export.
6. `make check` must pass before any merge: schema validation of `data/public/`, ruff, tsc, eslint, the kNN parity test and the ownership check.
7. Secrets live in `.env.local`, and `.env.example` lists every key. Raw data comes from a download script and is never committed.
8. At G1 and G2 everyone merges, D runs the full app, and fixes land before anyone starts new work.

Put this file at the repo root as `AGENTS.md`, plus a `CLAUDE.md` whose only line is `@AGENTS.md`, so every coding agent on the team follows the same rules and knows how to find its brief:

```markdown
# AGENTS.md: PoliScope

## Start here
- The plan is docs/PLAN.md. Read all of it before doing anything.
- Your human will say "I am team member N" (any wording with a number 1-4).
  1 = A Data, 2 = B Extraction, 3 = C Model, 4 = D App and integration.
  Follow that member's brief in the plan's "Agent briefs" section, in order.
- Resume from docs/status/<letter>.md: skip steps already logged as done.
- After the logged brief is complete, take your next action from the plan's
  Current handoff section.
- If contracts/ does not exist yet, member 4 has not bootstrapped the repo.
  Members 1-3: tell your human and stop.

## How to work
- Act without asking inside your own folders (see Team roles in the plan).
- Ask your human only for API keys or logins, a browser task you cannot do,
  a change to contracts/, or a gate you have missed twice.
- Never wait for a teammate: build against contracts/fixtures/ until the real
  file lands. Run git pull before every step.
- After every step: make check, commit as "[<letter>] what changed", then
  git fetch && git rebase origin/main && make check && git push origin HEAD:main
  (repeat if the push is rejected). Append one line to docs/status/<letter>.md:
  time, step, done or blocked, key numbers.
- Run date at every step. If you are behind a gate, take its fallback from the
  plan's Risks section instead of pushing on. From 09:30, fix bugs only.

## Contracts are law
- contracts/ and the plan's "Contract types" define every shared file. Never change them.
- data/public/ is written only by make export; app/src/generated/ only by make sync.
- JSON keys are snake_case. An unknown stance is null, never 0.
- Growth values are decimals per year: 0.004 = 0.4 percentage points.

## Code style
- Python 3.11, pandas, ruff format; scripts run as python -m pipeline.<stage>.<script>.
- TypeScript strict, Next.js App Router, Tailwind + shadcn/ui, Recharts only.
- Import types from app/src/types/contracts.ts (generated). Never redefine them.
- Colours, fonts and spacing come from app/src/styles/theme.ts only.
- Neutral wording: "precedent", "associated with". No rankings, no good or bad.
- Every number in the UI shows its unit and links to its source.
```

## Demo, pitch and submission

**One 2-minute pitch with two endings: for G-Research it ends on the map, for HRT it ends on the backtest.** Demo only from cached, preloaded governors-elect. Live paste is a bonus, never the critical path.

1. **Hook, 0:00–0:15.** "Last Tuesday, 36 US states elected governors, and 19 seats were open. Campaigns are words. We turned the words into data."
2. **Fingerprint, 0:15–0:40.** Pick a governor-elect and show the ten stances. Click one to show the exact sentence behind it: every number traces to a verified quote.
3. **Precedents, 0:40–1:10.** The star lands on the map of 259 governor terms, and the 7 nearest precedents light up with what happened to their states.
4. **Forecast, 1:10–1:40.** Baseline vs precedent-adjusted forecast, with its band and probability.
5. **Ending, 1:40–2:00.** G-Research: "Hidden: what governors actually commit to. Found: 259 speeches, ten dimensions, verified quotes. Useful: anyone's precedents in seconds." HRT: use the measured results in `docs/pitch.md`. Explain that the GDP model had higher error than the baseline and that debt's confidence interval includes zero.

| Likely judge question | Answer |
| --- | --- |
| Isn't this just party? | Party is a comparator in the backtest, and the Signal panel shows both side by side. |
| What about look-ahead bias? | Only the first speech of each term, outcomes measured from the year before it, training only on terms that had already ended. |
| Can an LLM score ideology reliably? | Every stance needs a verified verbatim quote. We report the verify rate, test–retest correlation and party separation. |
| 259 terms is tiny. | Agreed. That's why k was fixed in advance, every number has a 95% CI, and a permutation test checks we beat chance. |
| Is this causal? | No. Precedents are associations, and the app says so beside every forecast. |
| Is this partisan? | Same pipeline for every candidate, no rankings, neutral colours, a balanced demo set. |

### Submission checklist

- [ ] Devpost project created by 09:30 with all four members added
- [ ] Both sponsor challenges selected, once organisers confirm that's allowed
- [x] Public repo with a README covering the pitch, local setup, deployment, data sources, and source terms
- [x] Live URL tested in an isolated desktop browser and a phone-sized viewport
- [ ] Live URL tested on an actual phone
- [ ] 2-minute video recorded from the deployed app and uploaded unlisted
- [ ] Four screenshots: fingerprint, map, forecast, signal
- [ ] Devpost text: inspiration, what it does, how we built it, challenges, what we learned, what's next
- [ ] Offline fallback: production build and the video on two laptops
- [ ] Each pitch ending rehearsed three times, under 2 minutes

## Risks and fallbacks

**The data join and the LLM batch are the two risks that can sink the night, which is why both are tested on 30 terms by 01:00.** Each risk below has a warning sign and a fallback chosen in advance, so nobody debates at 03:00.

| Risk | Early warning | Fallback |
| --- | --- | --- |
| Speech-to-outcome join breaks | Fewer than 30 joined terms at G1 | Join on state and term-start year only, never on names; hand-fix the few leftovers |
| Batch extraction too slow or rate-limited | Fewer than 50 profiles by 02:00 | Cap concurrency, cache by text hash, send the first 8k tokens of each speech, switch to a faster model |
| Hallucinated quotes | Quote-verify rate below 90% | Unverified dimensions become null; tighten the prompt; never display unverified evidence |
| Debt data won't join | Not joined by 23:30 | Swap the second outcome for nonfarm payrolls, which FRED publishes for every state |
| Null backtest | The skill CI spans zero | Present it as the finding; lead the HRT pitch with method rigour and the GDP vs debt contrast |
| Political sensitivity | Anyone on the team uneasy about a screen | Neutral copy, balanced demo set, methodology panel, no rankings |
| Late deploy failure | A checked Docker rebuild fails after 08:00 | Keep the healthy running image while diagnosing the build, and prepare a local production build and video backup |
| Fatigue | Anyone past 20 hours awake | Sleep shifts are part of the plan, not optional |

## Agent briefs

**Each brief is the complete, ordered job for one member's agent: do the steps in order, log each one in your status file, and treat "by G1" as a deadline.** Every brief relies on the contract types and constants in Architecture; if a brief and the contracts ever disagree, the contracts win.

### Member 1 · Data (role A)

Goal: turn the raw sources into the three files everyone else builds on. Owns `pipeline/ingest/`, `data/raw/` (git-ignored), `data/interim/ingest/` and `docs/status/a.md`.

1. **Download (by 22:00).** `python -m pipeline.ingest.download` fetches into `data/raw/`, skipping files already present:
   - the speech archive `https://codeload.github.com/leops95/sots/zip/refs/heads/master`, unzipped to `data/raw/sots/`;
   - the debt file `https://raw.githubusercontent.com/jacobkap/government_finances/master/data/government_finances_1992_2018.csv`;
   - FRED observations from `https://api.stlouisfed.org/fred/series/observations` for real GDP (`<ST>RGSP`) and population (`<ST>POP`) for the 50 states and DC. Read `FRED_API_KEY` from the root `.env.local`. The download script writes the per-series files that the panel builder reads. If an ID fails, record the correction in `pipeline/ingest/fred_ids.json`.
2. **Terms table (by 22:30; B and C are waiting for it).** `python -m pipeline.ingest.build_terms` writes `data/interim/ingest/terms.csv`:
   - Read the archive's `metadata.csv`. Drop rows whose `type` is `sotu`, and drop NH and VT.
   - Sort by state, then year. A row starts a term when the previous row for the same state has `elec_year` = 1 and is exactly one year earlier. (`elec_year` = 1 means the speech year is an election year; the README's `elec_lastyear` is wrong.)
   - `term_id` = lowercase state code, a hyphen and t0, such as `oh-2011`. Party codes: 1 is R, 2 is D, 3 is I.
   - `name`: `speaker` is usually `Lastname_Firstname` with extra tokens for initials, but not always (`Frank_Murkowski` is reversed). Build "Firstname Lastname", then fix odd cases by hand in `pipeline/ingest/name_overrides.json`.
   - Assert exactly 259 rows, 45 states, unique `term_id`, and 30 rows with t0 = 2007. Commit and push at once.
3. **Panel (slice by 23:30, all by G1).** `python -m pipeline.ingest.build_panel` writes `data/interim/ingest/panel.csv`, one row per state (50 plus DC) and year, 1992–2025:
   - `rgdp_musd2017` from FRED (millions of chained 2017 dollars); `pop` in persons (FRED gives thousands); `gdp_pc` = rgdp × 10^6 / pop.
   - `debt_kusd` = the finance file's `debt_at_end_of_fiscal_year`, in thousands of dollars (spot check: Alabama 2018 is 9,856,082). Upper-case `state_abb` and drop any US-total row. `debt_pc` = debt\_kusd × 1,000 / pop.
   - Leave missing cells empty; never impute.
4. **Governor-elect platforms (by G2).** Pick 5 winners of the 3 November 2026 races whose results have been called, at least 2 from each party, preferring open seats. For each, save the campaign site's issues or platform page as plain text in `data/interim/ingest/platforms/<candidate_id>.txt` (candidate\_id = state plus `-2027`, such as `az-2027`) and add a row to `platforms.csv`. Use the campaign site first and Ballotpedia's candidate page second, aiming for 1,500+ words each. If your agent can't browse, ask your human to paste the texts. The app only ever shows short quotes from them.
5. **Recent debt (optional, after G2).** Add 2019–2024 debt from the Census Bureau's state government finances API, and keep it only if it matches the CSV within 1% for 2012–2018. Otherwise debt ends in 2018.
6. **Coverage report (by G3).** End `docs/status/a.md` with a table of terms kept and dropped at each stage and why, plus source URLs and licences for D's README.

Done when `terms.csv` (259 rows), `panel.csv` and the 5 platform texts are on `main`.

### Member 2 · Extraction (role B)

Goal: turn every speech and platform into a Profile with verified quotes, and serve the same extraction live. Owns `pipeline/extract/`, `contracts/prompt/`, `data/interim/extract/`, `app/src/app/api/extract/` and `docs/status/b.md`.

1. **LLM access.** The completed batch uses `LLM_PROVIDER=claude-cli`, `LLM_MODEL_BATCH=haiku`, and `LLM_MODEL_LIVE=sonnet` from the root `.env.local`, with an installed and authenticated Claude CLI. Structured output is constrained by JSON Schema. The hosted HTTP adapter will use a runtime provider secret. Ask your human for a missing login or API key when that backend is being configured.
2. **Prompt (by 22:30).** Write `contracts/prompt/extract_v1.md`, with a `{{DIMENSIONS}}` placeholder filled from `contracts/dimensions.json` at run time. It must tell the model to:
   - score the speaker's own positions and proposals, not policies they attack or merely describe;
   - give each stance from −1 to +1 using the dimension's anchors, or null when the text doesn't address it, and never 0 for "not mentioned";
   - set salience (0 absent, 0.5 discussed, 1 headline priority) and confidence (1 explicit commitment, 0.5 general rhetoric, 0.2 inferred);
   - copy 1–3 evidence quotes per non-null dimension character for character, at most 40 words each;
   - return only JSON matching `Record<DimId, DimScore>`.
3. **Quote verifier.** `pipeline/extract/verify.py` normalises whitespace, curly quotes and dashes in both quote and source, and keeps a quote only if it is an exact substring. A dimension left without quotes becomes stance null, salience 0, confidence 0, no evidence. Record each profile's verify rate.
4. **Batch (slice by 23:30, everything by 02:30).** `python -m pipeline.extract.run_batch` takes `--slice30`, `--all` or `--candidates`. It reads `terms.csv` and `platforms.csv`, sends at most the first 64,000 characters of each text (the current approximation of 16k tokens), and runs `LLM_CONCURRENCY` requests at once (default 8) with retry and backoff. It caches by SHA-1 of prompt version, model and text in `data/interim/extract/cache/` (git-ignored), verifies quotes, and writes `data/interim/extract/profiles.json` sorted by id, plus `extract_log.csv` (id, status, tokens in, tokens out, seconds, verify rate). Push the slice as soon as it's done, start `--all` right after G1, and check the first 20 results before the 02:30 sleep.
5. **Reliability (by G2).** `python -m pipeline.extract.reliability` writes `data/interim/extract/reliability.json`: the overall verify rate; test–retest Pearson r on 30 speeches (seed 7, cache bypassed); and party AUC from 5-fold cross-validated logistic regression on the ten stances, with nulls as 0 for this check only.
6. **Candidates (by G2).** Run `--candidates` once A's platform texts land.
7. **Live route (by G3).** `app/src/app/api/extract/route.ts` takes POST `{text, state, name?}` and returns a Profile with kind `candidate`, using the prompt and dimensions from `app/src/generated/` (never read files outside `app/`). Port the verifier to TypeScript, reject texts over 60,000 characters, cache by text hash in memory, and set `export const maxDuration = 60`. Coordinate with D to pass the provider secret to the Grimnir container at runtime. The production prompt must be present inside the image. See Current handoff and issue #1 for the public deployment switch.

Done when 259 historical and 5 candidate profiles are on `main` with a verify rate of at least 90%, `reliability.json` exists, and the live route returns a valid Profile for a 2,000-word text in under 60 seconds.

### Member 3 · Model (role C)

Goal: turn profiles and panels into outcomes, forecasts, the backtest and the map, and be the only writer of `data/public/`. Owns `pipeline/model/`, `data/public/`, `docs/pitch_numbers.md` and `docs/status/c.md`. Until A's and B's files land, run everything on `contracts/fixtures/`.

1. **Outcomes (slice by G1).** `python -m pipeline.model.outcomes`. For each term and metric, g(x) = \[ln x(t0+3) − ln x(t0−1)\] / 4.
   - `gdp_pc_rel` = g(state gdp\_pc) − g(US gdp\_pc), where US gdp\_pc is the total GDP of the 50 states and DC over their total population.
   - `debt_pc_rel` = g(state debt\_pc) − the median over states of g(debt\_pc) in the same window.
   - `prior` is the same quantity from t0−5 to t0−1. Skip and log any term and metric with a missing year. Expect about 218 GDP rows and 204 debt rows.
2. **Baseline.** Ordinary least squares, actual = a + b × prior. The `baseline` and `residual` in `outcomes.json` come from the fit on all rows; the backtest refits per cohort. Write `baseline.json` with the all-row coefficients and each state's latest prior: GDP over 2021–2025, debt over the latest 4 years available.
3. **kNN (by G1).** `pipeline/model/knn.py` implements the Model spec and constants exactly. Neighbours are historical profiles that have a residual for the metric, never the query itself, with at least 5 dimensions scored by both.
4. **Backtest (by G2).** `python -m pipeline.model.backtest`. A cohort is a t0 year E with at least 8 test terms and at least 30 training terms, where training terms have t0 + 3 ≤ E − 1; refit the baseline on them. Score every test term with five models: baseline; baseline plus the mean training residual of the same party; kNN; ridge regression (alpha 1, nulls as 0) on the ten stances, predicting the residual; and kNN on shuffled training profiles (200 runs). Write `signal.json` with:
   - MAE per model, and skill = 1 − MAE(kNN) / MAE(baseline) with its bootstrap 95% CI;
   - skill against party, and permutation p = (1 + runs with MAE ≤ kNN's) / 201;
   - Brier scores for kNN's p\_above and for the baseline's, where the baseline's is the share of training residuals that lift it above 0;
   - 5-bin calibration.
5. **Map (by G2).** `python -m pipeline.model.pca_map` runs PCA, centred but not scaled, on historical stances with nulls set to the historical dimension mean, places every historical and candidate profile, and writes `map.json`.
6. **Candidate forecasts (by G2).** For each candidate and metric, baseline = a + b × the state's latest prior. If the state has no debt data after 2018, set the debt baseline to 0 and the note to "precedent-only: no recent debt data". Write `forecasts.json`.
7. **Parity fixture (by G2).** `knn_parity.json` holds 5 cases (3 candidates, 2 historical terms) with full expected Forecasts, so D's TypeScript port can prove it matches.
8. **Export.** `make export` validates every file against `contracts/schemas/` and writes `data/public/`. Run it after every step that changes an output, and never write `data/public/` any other way.
9. **Pitch numbers (by G3).** `docs/pitch_numbers.md` gives, for each metric, n, skill with its CI, skill against party and the permutation p-value, each as one plain sentence. If a CI spans zero, say so.

Done when every `data/public/` file validates, `signal.json` covers both metrics, and the parity fixture is on `main`.

### Member 4 · App and integration (role D)

Goal: create the repo, keep `main` deployable, and build the three screens. Owns everything the other three don't: repo root files, `contracts/` except `prompt/`, `app/` except the extract route, `scripts/`, `docs/` except the others' files, and `docs/status/d.md`.

1. **Bootstrap (by 21:30, before anyone else starts).** Your human has already put `docs/PLAN.md`, `AGENTS.md` and `CLAUDE.md` in the folder. Create:
   - `.gitignore` (`data/raw/`, `data/interim/extract/cache/`, `.env.local`, `node_modules/`, `.venv/`), `.env.example` listing every variable named in the briefs, and `docs/status/a.md` to `d.md`;
   - `pipeline/pyproject.toml` for Python 3.11 with pandas, numpy, scikit-learn, requests, jsonschema, pytest and ruff, plus empty `__init__.py` files in `pipeline/`, `ingest/`, `extract/` and `model/`;
   - `contracts/dimensions.json` from the dimension table (id, label, minus, plus, in table order), `contracts/schemas/` generated from the Contract types, and `contracts/fixtures/` with valid fake data for every type, including 12 historical profiles and 1 candidate;
   - `app/` with Next.js App Router, TypeScript strict, Tailwind, shadcn/ui, Recharts, Vitest, `src/styles/theme.ts`, and `src/types/contracts.ts` generated from the schemas;
   - a `Makefile` with `data`, `extract`, `model` and `export` (each calling `python -m pipeline.<stage>.<script>` for the scripts named in the briefs), `sync` (copies the dimensions, the prompt and `data/public/` into `app/src/generated/`, falling back to fixtures for any missing file), `check` (schema validation, ruff, pytest, tsc, eslint, vitest and the ownership check) and `dev`;
   - `scripts/check_ownership.py`, which fails when branch `<letter>/…` changes files outside that letter's folders in Team roles. Push to GitHub (ask your human to create the empty repo if you can't), deploy through the Grimnir Docker and Cloudflare procedure in Current handoff, and post the repo URL for the team.
2. **Screens on fixtures (by G1).** `/` lists the 5 governors-elect and has a "Paste a platform" box. `/s/[id]` shows one subject in three sections, plus methodology:
   - **Fingerprint:** ten diverging bars from −1 to +1, opacity by confidence, "not mentioned" for null. Clicking a bar opens an evidence disclosure with its quotes and source link.
   - **Precedents:** a Recharts scatter of `map.json`, coloured by the selected metric's `actual` on a diverging scale centred on zero. The subject is a star and its 7 neighbours are outlined. Hover shows name, state, years and outcome; axis titles show explained variance.
   - **Forecast and Signal:** a metric toggle; baseline and forecast as dots with the p10–p90 band; one sentence stating p\_above; the neighbour table; and the Signal panel with skill and CI, skill against party, permutation p, Brier score and n. Add the calibration chart when present and the "precedent-only" note when set. Every forecast carries the line "Precedents show association, not cause."
   - **Methodology:** sources, caveats and the reliability numbers.
3. **Live path (by G2).** Port Model spec steps 3 and 4 to `src/lib/knn.ts` and the PCA projection to `src/lib/project.ts`. A Vitest test runs every case in `knn_parity.json` and must match to 1e-9 with identical neighbour ids. Pasted text then goes to B's route, and the returned profile runs through kNN and projection into the same screens.
4. **Integrate at G1 and G2.** Pull, run `make sync && make check && make dev`, click through every screen on real data, and open a GitHub issue tagged with the owner's letter for each problem.
5. **Polish (G2 to G3).** Add empty, loading and error states, keep one consistent theme, and check the deployed URL in a private window and on a phone.
6. **Pitch (by G3).** Write `docs/pitch.md` from Demo, pitch and submission with C's numbers filled in, plus the video script and a Devpost draft.

Done when the deployed URL shows all three screens on real data for the 5 governors-elect, the parity test passes, and `make check` is green on `main`.

## Sources

- [Ballotpedia: Gubernatorial elections, 2026](https://ballotpedia.org/Gubernatorial_elections,_2026): 36 races on 3 November 2026, 19 without an incumbent on the ballot
- [leops95/sots](https://github.com/leops95/sots): speech corpus and metadata; term counts computed from its `metadata.csv`
- [jacobkap/government\_finances](https://github.com/jacobkap/government_finances): state debt CSV, 1992–2018
- [FRED: BEA GDP by State release](https://fred.stlouisfed.org/data/USGOVSLRGSP): chained 2017 dollars, 1997–2025
- [EIA note on BEA state GDP](https://www.eia.gov/state/seds/sep_use/notes/use_gdp.pdf): the 1997 series break, and why the sum of states differs from US GDP
- [HackTheBurgh XIII event listing](https://createwith.com/event/edinburgh-hacktheburgh-xiii-nov-2026): 12:00 Sunday deadline, teams of up to four, sponsor list
- Your uploads: the sponsor challenge slides and the earlier brainstorm
