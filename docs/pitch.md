# PoliScope pitch and demo

## Two-minute video and stage script

Open a preloaded candidate with a verified quote, both forecasts, and a point on the precedent map. Keep the home page in a second tab for the reset. Record the cached path for the backup.

| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:15 | Home and the preloaded candidates | “Governors make promises in speeches and platforms. Those promises are easy to read one at a time and hard to compare across states and years. PoliScope turns them into policy fingerprints and looks for historical precedents.” |
| 0:15–0:40 | Open a candidate, then expand a dimension with evidence | “Each bar scores a policy dimension against two written anchors. Fainter bars show lower confidence. An unmentioned policy stays blank. Open a bar and you can read the quote behind the score and go back to the source.” |
| 0:40–1:10 | Show the candidate star and select an outlined point | “The star is the candidate. Each point is a historical term, positioned by its policy fingerprint. The outlines mark the seven nearest terms for this outcome. Select one to see its state, years, and how its outcome compared with the benchmark.” |
| 1:10–1:40 | Compare the baseline, forecast, and band. Switch metrics. | “We start with the state’s prior trend, then adjust it using the seven similar terms. We show a range and a probability that growth exceeds the benchmark. GDP is compared with the US. Debt is compared with the median state. Precedents show association, not cause.” |
| 1:40–2:00 | Use one of the endings below | Record a separate closing for each track. |

### G-Research ending

Return to the map, then reopen the evidence.

“The policy commitments were already in the text. We made them comparable by using the same ten dimensions and checking each quote against its source. You can move from a claim in a platform to historical precedents and see the evidence behind the comparison.”

### HRT ending

Keep the Signal panel visible and switch from GDP to debt.

“Across 129 held-out GDP terms, the precedent model’s error was 15.7% higher than the prior-trend baseline. Across 128 debt terms, the error was 9.3% higher, with an interval that crosses zero. We’d keep the baseline as the decision rule and use the precedents to explore the history behind the estimate.”

## Results for the presenter

These figures come from Member C’s model and pitch-number generator, run against the historical panel and 259 profiles at commit `a109353`. Check them against `docs/pitch_numbers.md` and the deployed Signal panel before recording. Skill measures the reduction in mean absolute error relative to the comparator. Negative skill means higher error.

| Outcome | Test terms | Skill vs prior trend and 95% CI | Skill vs party | Permutation p |
| --- | --- | --- | --- | --- |
| Real GDP per capita vs US | 129 | −15.7% [−23.6%, −8.7%] | −16.1% | 0.995 |
| State debt per capita vs median state | 128 | −9.3% [−21.7%, 1.6%] | −5.2% | 0.398 |

The Brier score for GDP was 0.327 with precedents versus 0.263 for the baseline. For debt it was 0.278 versus 0.267. Lower scores indicate more accurate probabilities.

## Devpost draft

### Inspiration

We wanted to make governors’ policy commitments comparable across states and election cycles. Speeches and platforms contain those commitments, but they are written for different audiences and rarely structured for analysis.

### What it does

PoliScope scores ten policy dimensions from a public speech or platform. Readers can inspect the quote behind a score, explore similar historical terms on a map, and compare their economic outcomes. The forecast shows a prior-trend baseline, a precedent-adjusted estimate, a range, and the probability of exceeding the benchmark.

### How we built it

A Python pipeline joins first-of-term speeches with state-year economic data. Structured extraction supplies stance, salience, confidence, and evidence. We check the quotes against the source text before displaying them. The model uses confidence-weighted distances to find seven precedents and exports schema-checked JSON to a Next.js app. The browser mirrors the model’s arithmetic for pasted platforms.

### Challenges we worked through

A term’s speech and outcome window have to line up. GDP and debt have different coverage, so each outcome is evaluated on the years and terms with the necessary data. We kept missing stances explicit and verified evidence before including it. We also checked that the browser and Python put the same precedents in the same order.

### What we learned

Policy text becomes much easier to compare when readers can trace a score back to a sentence. In the walk-forward test, precedents increased GDP forecast error by 15.7% relative to prior trends. The debt estimate also had higher error, with a confidence interval that included zero. The results support using the baseline for forecasting and the fingerprints for historical exploration.

### What’s next

Extend coverage with additional verified platforms, improve the evidence workflow, and test forecasts on later election cohorts as their outcomes become available.

## Recording checklist

- Choose a cached candidate with a useful quote and both metric views.
- Record the fingerprint, map, forecast, and Signal panel.
- Check the stage script against the real export and rehearse both endings.
- Upload the two-minute recording as unlisted and add the live and repository links to Devpost.
- Keep a production build and the recording on both backup laptops.
