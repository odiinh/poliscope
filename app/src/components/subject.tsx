import { dimensions, metrics, percent, sourceUrl } from "../lib/policy";
import type { ComparisonData } from "../lib/subject-view";
import { theme } from "../styles/theme";
import type { Profile, Reliability } from "../types/contracts";
import { Comparison } from "./comparison";

function Fingerprint({ profile }: { profile: Profile }) {
  const source = sourceUrl(profile.source.url);
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
                  {stance === 0 && <span className="absolute inset-y-0 left-1/2 w-1 -translate-x-1/2 bg-foreground" style={{ opacity: confidence }} />}
                  {stance !== null && stance !== 0 && <span className="absolute h-full" style={{
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

export function Subject({ profile, comparison, fixtureMode, reliability, pasted = false }: {
  profile: Profile;
  comparison: ComparisonData;
  fixtureMode: boolean;
  reliability: Reliability | null;
  pasted?: boolean;
}) {
  return (
    <article id={pasted ? "platform-results" : undefined} className="space-y-6">
      <header className="space-y-2">
        <p className="eyebrow">{pasted ? "Pasted platform" : fixtureMode ? "Synthetic fixture" : "Subject"}</p>
        {pasted ? <h2>{profile.name}</h2> : <h1>{profile.name}</h1>}
        <p className="text-muted-foreground">{profile.state} · {profile.term_start}</p>
        {fixtureMode && <p role="note" className="rounded-lg bg-muted p-3 text-sm">Historical comparisons and model scores use synthetic data.</p>}
      </header>
      <Fingerprint profile={profile} />
      <Comparison data={comparison} />
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
