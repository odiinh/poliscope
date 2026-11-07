import type { Baseline, Forecast, Metric, Neighbour, Outcome, Profile } from "../types/contracts";
import { dimensions } from "./policy";

const K = 7;
const DISTANCE_FLOOR = 0.05;
const MIN_SHARED = 5;

// NumPy's contiguous sum for the ten dimensions adds four pairs, then the
// final two terms. Use the same order so rounding preserves neighbour order.
function sumDimensions(values: number[]) {
  const first = (values[0] + values[1]) + (values[2] + values[3]);
  const second = (values[4] + values[5]) + (values[6] + values[7]);
  return first + second + values[8] + values[9];
}

function distance(query: Profile, precedent: Profile) {
  let shared = 0;
  const weights: number[] = [];
  const squared: number[] = [];
  for (const { id } of dimensions) {
    const a = query.dims[id];
    const b = precedent.dims[id];
    if (a.stance === null || b.stance === null) {
      weights.push(0);
      squared.push(0);
      continue;
    }
    const confidence = Math.min(a.confidence, b.confidence);
    shared += 1;
    weights.push(confidence);
    squared.push(confidence * (a.stance - b.stance) ** 2);
  }
  const total = sumDimensions(weights);
  return shared >= MIN_SHARED && total > 0 ? Math.sqrt(sumDimensions(squared) / total) : null;
}

function quantile(neighbours: Neighbour[], baseline: number, q: number) {
  const sorted = [...neighbours].sort((a, b) => a.residual - b.residual);
  let cumulative = 0;
  for (const row of sorted) {
    cumulative += row.weight;
    if (cumulative >= q) return baseline + row.residual;
  }
  return baseline + sorted[sorted.length - 1].residual;
}

export function candidateBaseline(baseline: Baseline, state: string, metric: Metric) {
  const prior = baseline.latest_prior[state]?.[metric];
  if (prior == null) {
    const label = metric === "debt_pc_rel" ? "debt" : "GDP";
    return { value: 0, note: `precedent-only: no recent ${label} data` };
  }
  const { a, b } = baseline.coefs[metric];
  return { value: a + b * prior, note: null };
}

export function nearestForecast(
  query: Profile,
  metric: Metric,
  baseline: number,
  profiles: Profile[],
  outcomes: Outcome[],
  note: string | null = null,
): Forecast | null {
  const residuals = new Map(outcomes.filter((row) => row.metric === metric).map((row) => [row.term_id, row.residual]));
  const eligible = profiles.flatMap((profile) => {
    if (profile.kind !== "historical" || profile.id === query.id) return [];
    const residual = residuals.get(profile.id);
    if (residual === undefined) return [];
    const d = distance(query, profile);
    return d === null ? [] : [{ id: profile.id, residual, distance: d, weight: 1 / (d + DISTANCE_FLOOR) }];
  });
  if (eligible.length < K) return null;
  eligible.sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id, "en"));
  const neighbours = eligible.slice(0, K) as Forecast["neighbours"];
  const total = neighbours.reduce((sum, row) => sum + row.weight, 0);
  for (const row of neighbours) row.weight /= total;

  return {
    subject_id: query.id,
    metric,
    baseline,
    forecast: baseline + neighbours.reduce((sum, row) => sum + row.weight * row.residual, 0),
    p10: quantile(neighbours, baseline, 0.1),
    p90: quantile(neighbours, baseline, 0.9),
    p_above: Math.min(1, neighbours.reduce((sum, row) => baseline + row.residual > 0 ? sum + row.weight : sum, 0)),
    neighbours,
    note,
  };
}
