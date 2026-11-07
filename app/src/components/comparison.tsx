"use client";

import { useId, useState } from "react";
import { metricIds, metrics, percent, pp } from "../lib/policy";
import type { ComparisonData } from "../lib/subject-view";
import type { Metric, Signal } from "../types/contracts";
import { Calibration, ForecastPlot, PrecedentMap } from "./charts";

function skillSummary([low, high]: Signal["skill_ci95"]) {
  if (high < 0) return "Precedents increased forecast error versus the prior-trend baseline in this backtest.";
  if (low > 0) return "Precedents reduced forecast error versus the prior-trend baseline in this backtest.";
  return "The interval includes zero, so the difference in forecast error remains uncertain.";
}

export function Comparison({ data }: { data: ComparisonData }) {
  const metricName = useId();
  const [metric, setMetric] = useState<Metric>("gdp_pc_rel");
  const forecast = data.forecasts.find((row) => row.metric === metric);
  const signal = data.signals.find((row) => row.metric === metric);
  const nearest = new Set(forecast?.neighbours.map(({ id }) => id));
  const points = (data.map?.points ?? []).map(({ id, x, y, name, state, term_start, subject, outcomes }) => ({
    id, x, y, name, state, subject, neighbour: nearest.has(id),
    years: outcomes[metric]?.window.join("–") ?? String(term_start),
    actual: outcomes[metric]?.actual ?? null,
  }));
  const { outcome, benchmark, source } = metrics[metric];

  return (
    <>
      <fieldset className="space-y-2">
        <legend className="font-semibold">Outcome metric</legend>
        <div className="flex flex-wrap gap-2">
          {metricIds.map((id) => (
            <label key={id} className="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm has-checked:border-foreground">
              <input type="radio" className="accent-(--poliscope-accent)" name={metricName} checked={metric === id} onChange={() => setMetric(id)} />
              {metrics[id].label}
            </label>
          ))}
        </div>
      </fieldset>
      <section className="panel" aria-labelledby="precedents">
        <h2 id="precedents">Historical precedents</h2>
        <p>Each point shows a term placed by its policy fingerprint. Colour shows annual {outcome} relative to {benchmark}. <a href={source}>Outcome source</a></p>
        {data.map && points.length ? <PrecedentMap points={points} explained={data.map.explained} /> : <p>The precedent map is unavailable for this dataset.</p>}
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
            <p>The estimated probability that {outcome} exceeds {benchmark} is <strong>{percent(forecast.p_above)}</strong>. <a href={source}>Outcome source</a></p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <caption className="pb-2 text-left font-semibold">Seven nearest precedents</caption>
                <thead><tr><th>Term</th><th>Distance</th><th>Weight</th><th>Residual</th></tr></thead>
                <tbody className="divide-y divide-border">
                  {forecast.neighbours.map(({ id, distance, weight, residual }) => {
                    const precedent = data.precedents[id];
                    const url = precedent?.url;
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
              <p>{skillSummary(signal.skill_ci95)}</p>
              <p><a href="https://github.com/odiinh/poliscope/blob/main/docs/PLAN.md#model-spec">Backtest specification</a></p>
              {signal.calibration.length > 0 && <Calibration bins={signal.calibration} />}
            </>
          ) : <p>Backtest results are unavailable for this metric.</p>}
        </div>
      </section>
    </>
  );
}
