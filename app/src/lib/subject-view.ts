import { baseline, fixtureMode, forecasts, map, outcomes, profiles, reliability, signals } from "./data";
import { candidateBaseline, nearestForecast } from "./knn";
import { metricIds, sourceUrl } from "./policy";
import type { Forecast, MapData, Metric, Outcome, Profile, Signal } from "../types/contracts";

type Term = Pick<Profile, "name" | "state" | "term_start">;
type Precedent = Term & { url?: string };
type Point = MapData["points"][number] & Term & {
  subject: boolean;
  outcomes: Partial<Record<Metric, Pick<Outcome, "actual" | "window">>>;
};

export type ComparisonData = {
  map: { points: Point[]; explained: MapData["explained"] } | null;
  forecasts: Forecast[];
  signals: Signal[];
  precedents: Record<string, Precedent>;
};

const profileById = new Map(profiles.map((profile) => [profile.id, profile]));
const outcomesById = new Map<string, Partial<Record<Metric, Outcome>>>();
for (const outcome of outcomes) {
  const { term_id, metric } = outcome;
  const terms = outcomesById.get(term_id) ?? {};
  terms[metric] = outcome;
  outcomesById.set(term_id, terms);
}

function term({ name, state, term_start }: Profile): Term {
  return { name, state, term_start };
}

function subjectForecasts(profile: Profile, pasted: boolean) {
  if (!pasted && profile.kind === "candidate") {
    return forecasts.filter(({ subject_id }) => subject_id === profile.id);
  }

  return metricIds.flatMap((metric) => {
    const outcome = outcomesById.get(profile.id)?.[metric];
    const estimate = pasted
      ? baseline && candidateBaseline(baseline, profile.state, metric)
      : outcome && { value: outcome.baseline, note: "Retrospective estimate using the available historical terms." };
    if (!estimate) return [];
    const forecast = nearestForecast(profile, metric, estimate.value, profiles, outcomes, estimate.note);
    return forecast ? [forecast] : [];
  });
}

export function subjectView(profile: Profile, options: {
  pasted?: boolean;
  projected?: MapData["points"][number];
} = {}) {
  const { pasted = false, projected } = options;
  const subjectEstimates = subjectForecasts(profile, pasted);
  const points = (map?.points ?? []).flatMap((point): Point[] => {
    const subject = point.id === profile.id;
    if (subject && projected) return [];
    const source = subject ? profile : profileById.get(point.id);
    if (!source || (!subject && source.kind !== "historical")) return [];
    const pointOutcomes: Point["outcomes"] = {};
    for (const metric of metricIds) {
      const outcome = outcomesById.get(point.id)?.[metric];
      if (outcome) pointOutcomes[metric] = { actual: outcome.actual, window: outcome.window };
    }
    return [{ ...point, ...term(source), subject, outcomes: pointOutcomes }];
  });
  if (projected) points.push({ ...projected, ...term(profile), subject: true, outcomes: {} });

  const precedents: Record<string, Precedent> = {};
  for (const forecast of subjectEstimates) {
    for (const { id } of forecast.neighbours) {
      const match = profileById.get(id);
      if (match) precedents[id] = { ...term(match), url: sourceUrl(match.source.url) };
    }
  }

  const comparison: ComparisonData = {
    map: map ? { points, explained: map.explained } : null,
    forecasts: subjectEstimates,
    signals,
    precedents,
  };
  return { profile, comparison, fixtureMode, reliability, pasted };
}
