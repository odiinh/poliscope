import baselineJson from "../generated/baseline.json";
import forecastJson from "../generated/forecasts.json";
import mapJson from "../generated/map.json";
import outcomeJson from "../generated/outcomes.json";
import profileJson from "../generated/profiles.json";
import publicFiles from "../generated/public-files.json";
import reliabilityJson from "../generated/reliability.json";
import signalJson from "../generated/signal.json";
import type { Baseline, Forecast, MapData, Outcome, Profile, Reliability, Signal } from "../types/contracts";

export const publicInputs = new Set<string>(publicFiles);
const publicProfiles = publicInputs.has("profiles.json");
export const fixtureMode = !publicProfiles;

// make sync falls back per file. A subject view uses only files with the same
// provenance as its profiles, so partial exports cannot surface synthetic results.
function matching<T>(file: string, data: unknown): T | null {
  return publicInputs.has(file) === publicProfiles ? data as T : null;
}

export const profiles = profileJson as unknown as Profile[];
export const outcomes = matching<Outcome[]>("outcomes.json", outcomeJson) ?? [];
export const forecasts = matching<Forecast[]>("forecasts.json", forecastJson) ?? [];
export const signals = matching<Signal[]>("signal.json", signalJson) ?? [];
export const map = matching<MapData>("map.json", mapJson);
export const baseline = matching<Baseline>("baseline.json", baselineJson);
export const reliability = matching<Reliability>("reliability.json", reliabilityJson);
