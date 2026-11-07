"use client";

import { useState } from "react";
import {
  dimensions, fixtureMode, map, metrics, outcomes, percent, pp, profiles, reliability, signals,
} from "../lib/data";
import { theme } from "../styles/theme";
import type { Forecast, MapData, Metric, Profile } from "../types/contracts";
import { Calibration, ForecastPlot, PrecedentMap } from "./charts";

const profileById = new Map(profiles.map((profile) => [profile.id, profile]));
const metricIds = Object.keys(metrics) as Metric[];

function sourceLink(url: string) {
  try {
    const protocol = new URL(url).protocol;
    return protocol === "https:" || protocol === "http:" ? url : undefined;
  } catch {
    return undefined;
  }
}

function Fingerprint({ profile }: { profile: Profile }) {
  const source = sourceLink(profile.source.url);
  return (
    <section className="panel" aria-labelledby="fingerprint">
      <h2 id="fingerprint">Policy fingerprint</h2>
      <p>Scores range from −1 to +1. Fainter bars show lower extraction confidence. Open a dimension to read its evidence.</p>
      <div className="divide-y divide-border">
        {dimensions.map(({ id, label, minus, plus }) => {
          const { stance, confidence, evidence } = profile.dims[id];
          return (
            <details key={id} className="py-3">
              <summary className="cursor-pointer">
                <span className="font-medium">{label}</span>
                <span className="float-right text-muted-foreground">
                  {stance === null ? "Not mentioned" : `${stance > 0 ? "+" : ""}${stance.toFixed(2)}`}
                </span>
                <span aria-hidden="true" className="relative mt-2 block h-3 overflow-hidden rounded-full bg-muted">
                  <span className="absolute left-1/2 h-full border-l border-muted-foreground" />
                  {stance !== null && <span className="absolute h-full" style={{
                    left: `${50 + Math.min(stance, 0) * 50}%`,
                    width: `${Math.abs(stance) * 50}%`,
                    background: stance < 0 ? theme.negative : theme.positive,
                    opacity: confidence,
                  }} />}
                </span>
                <span className="mt-1 flex justify-between gap-3 text-xs text-muted-foreground">
                  <span>−1 · {minus}</span><span className="text-right">+1 · {plus}</span>
                </span>
              </summary>
              <div className="mt-3 space-y-2 border-l-2 border-border pl-3 text-sm">
                {evidence.length ? evidence.map((quote, index) => (
                  <blockquote key={index}>“{quote}”</blockquote>
                )) : <p>No verified quote for this dimension.</p>}
                {stance !== null && <p>Confidence {percent(confidence)}</p>}
                {source && <a href={source}>Read the source text</a>}
              </div>
            </details>
          );
        })}
      </div>
    </section>
  );
}

export function Subject({ profile, forecasts, projected, pasted = false }: {
  profile: Profile;
  forecasts: Forecast[];
  projected?: MapData["points"][number];
  pasted?: boolean;
}) {
  const [metric, setMetric] = useState<Metric>("gdp_pc_rel");
  const forecast = forecasts.find((row) => row.metric === metric);
  const signal = signals.find((row) => row.metric === metric);
  const byOutcome = new Map(outcomes.filter((row) => row.metric === metric).map((row) => [row.term_id, row]));
  const nearest = new Set(forecast?.neighbours.map((row) => row.id));
  const points = (map?.points ?? []).flatMap((point) => {
    if (projected && point.id === profile.id) return [];
    const historical = profileById.get(point.id);
    if (!historical || (historical.kind !== "historical" && point.id !== profile.id)) return [];
    const outcome = byOutcome.get(point.id);
    return [{
      ...point, name: historical.name, state: historical.state,
      years: outcome ? outcome.window.join("–") : String(historical.term_start),
      actual: outcome?.actual ?? null, neighbour: nearest.has(point.id), subject: point.id === profile.id,
    }];
  });
  if (projected) {
    points.push({
      ...projected, name: profile.name, state: profile.state, years: String(profile.term_start),
      actual: null, subject: true, neighbour: false,
    });
  }
  const { label, benchmark, source } = metrics[metric];

  return (
    <article className="space-y-6">
      <header className="space-y-2">
        <p className="eyebrow">{pasted ? "Pasted platform" : fixtureMode ? "Synthetic fixture" : "Subject"}</p>
        <h1>{profile.name}</h1>
        <p className="text-muted-foreground">{profile.state} · {profile.term_start}</p>
        {fixtureMode && <p role="note" className="rounded-lg bg-muted p-3 text-sm">Historical comparisons and model scores use synthetic data.</p>}
      </header>
      <Fingerprint profile={profile} />
      <fieldset className="space-y-2">
        <legend className="font-semibold">Outcome metric</legend>
        <div className="flex flex-wrap gap-2">
          {metricIds.map((id) => (
            <label key={id} className="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm has-checked:border-foreground">
              <input type="radio" name={pasted ? "pasted-metric" : "metric"} checked={metric === id} onChange={() => setMetric(id)} />
              {metrics[id].label}
            </label>
          ))}
        </div>
      </fieldset>
      <section className="panel" aria-labelledby="precedents">
        <h2 id="precedents">Historical precedents</h2>
        <p>Each point shows a term placed by its policy fingerprint. Colour shows annual {label.toLowerCase()} growth relative to {benchmark}. <a href={source}>Outcome source</a></p>
        {map && points.length ? <PrecedentMap points={points} explained={map.explained} /> : <p>The precedent map is unavailable for this dataset.</p>}
      </section>
      <section className="panel" aria-labelledby="forecast">
        <h2 id="forecast">Forecast and Signal</h2>
        <p>Precedents show association, not cause.</p>
        {forecast ? (
          <>
            {forecast.note && <p className="rounded-lg bg-muted p-3">{forecast.note}</p>}
            <ForecastPlot forecast={forecast} />
            <dl className="grid gap-3 sm:grid-cols-3">
              <div><dt>Baseline</dt><dd>{pp(forecast.baseline)}</dd></div>
              <div><dt>Forecast</dt><dd>{pp(forecast.forecast)}</dd></div>
              <div><dt>80% precedent band</dt><dd>{pp(forecast.p10)} to {pp(forecast.p90)}</dd></div>
            </dl>
            <p>The estimated probability that {label.toLowerCase()} growth exceeds {benchmark} is <strong>{percent(forecast.p_above)}</strong>. <a href={source}>Outcome source</a></p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <caption className="pb-2 text-left font-semibold">Seven nearest precedents</caption>
                <thead><tr><th>Term</th><th>Distance</th><th>Weight</th><th>Residual</th></tr></thead>
                <tbody className="divide-y divide-border">
                  {forecast.neighbours.map(({ id, distance, weight, residual }) => {
                    const precedent = profileById.get(id);
                    const url = sourceLink(precedent?.source.url ?? "");
                    const name = precedent ? `${precedent.name} · ${precedent.state} ${precedent.term_start}` : id;
                    return <tr key={id}>
                      <td className="py-2 pr-3">{url ? <a href={url}>{name}</a> : name}</td>
                      <td className="pr-3">{distance.toFixed(3)}</td><td className="pr-3">{percent(weight)}</td><td>{pp(residual)}</td>
                    </tr>;
                  })}
                </tbody>
              </table>
            </div>
          </>
        ) : <p>There is no forecast for this subject and metric in the current dataset.</p>}
        <div className="space-y-3 border-t border-border pt-4">
          <h3>Signal · out-of-sample backtest</h3>
          {signal ? (
            <>
              <dl className="grid gap-3 sm:grid-cols-3">
                <div><dt>Skill vs baseline</dt><dd>{percent(signal.skill)}</dd></div>
                <div><dt>95% confidence interval</dt><dd>{signal.skill_ci95.map(percent).join(" to ")}</dd></div>
                <div><dt>Skill vs party</dt><dd>{percent(signal.skill_vs_party)}</dd></div>
                <div><dt>Permutation p-value</dt><dd>{signal.permutation_p.toFixed(3)}</dd></div>
                <div><dt>Brier score · model / baseline</dt><dd>{signal.brier.knn.toFixed(3)} / {signal.brier.baseline.toFixed(3)}</dd></div>
                <div><dt>Test terms</dt><dd>{signal.n_test}</dd></div>
              </dl>
              {signal.calibration.length > 0 && <Calibration bins={signal.calibration} />}
            </>
          ) : <p>Backtest results are unavailable for this metric.</p>}
        </div>
      </section>
      <section className="panel" aria-labelledby="methodology">
        <h2 id="methodology">Methodology</h2>
        <p>We score ten policy dimensions using verified source quotes. The map projects the scores into two dimensions. The forecast adjusts a prior-trend baseline using the weighted residuals of seven similar historical terms. The backtest trains on terms whose outcome windows had already ended.</p>
        <p>Campaign platforms and speeches can omit policy positions. National and state conditions can affect outcomes. The precedent band describes the spread of similar historical outcomes.</p>
        {reliability ? (
          <dl className="grid gap-3 sm:grid-cols-4">
            <div><dt>Profiles</dt><dd>{reliability.n_profiles}</dd></div>
            <div><dt>Quote verification</dt><dd>{percent(reliability.verify_rate)}</dd></div>
            <div><dt>Test–retest correlation</dt><dd>{reliability.test_retest_r.toFixed(2)}</dd></div>
            <div><dt>Party separation · AUC</dt><dd>{reliability.party_auc.toFixed(2)}</dd></div>
          </dl>
        ) : <p>Extraction reliability results are unavailable.</p>}
        <p className="flex flex-wrap gap-x-4 gap-y-2">
          <a href="https://github.com/leops95/sots">Speech corpus</a>
          <a href={metrics.gdp_pc_rel.source}>GDP data</a>
          <a href={metrics.debt_pc_rel.source}>Debt data</a>
          <a href="https://github.com/odiinh/poliscope/blob/main/docs/PLAN.md">Model specification</a>
        </p>
      </section>
    </article>
  );
}
