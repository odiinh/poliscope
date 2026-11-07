import baselineJson from "../generated/baseline.json";
import dimensionJson from "../generated/dimensions.json";
import forecastJson from "../generated/forecasts.json";
import mapJson from "../generated/map.json";
import outcomeJson from "../generated/outcomes.json";
import profileJson from "../generated/profiles.json";
import publicFiles from "../generated/public-files.json";
import reliabilityJson from "../generated/reliability.json";
import signalJson from "../generated/signal.json";
import type {
  Baseline, DimId, Forecast, MapData, Metric, Outcome, Profile, Reliability, Signal,
} from "../types/contracts";

export const dimensions = dimensionJson as (typeof dimensionJson[number] & { id: DimId })[];
export const profiles = profileJson as Profile[];
const publicNames = new Set<string>(publicFiles);
export const fixtureMode = !publicNames.has("profiles.json");

function sameDataset(file: string) {
  return publicNames.has(file) !== fixtureMode;
}

export const outcomes = sameDataset("outcomes.json") ? outcomeJson as Outcome[] : [];
export const forecasts = sameDataset("forecasts.json") ? forecastJson as Forecast[] : [];
export const signals = sameDataset("signal.json") ? signalJson as unknown as Signal[] : [];
export const map = sameDataset("map.json") ? mapJson as MapData : null;
export const baseline = sameDataset("baseline.json") ? baselineJson as unknown as Baseline : null;
export const reliability = sameDataset("reliability.json") ? reliabilityJson as Reliability : null;

export const metrics: Record<Metric, { label: string; benchmark: string; source: string }> = {
  gdp_pc_rel: {
    label: "Real GDP per capita",
    benchmark: "the US benchmark",
    source: "https://fred.stlouisfed.org/data/USGOVSLRGSP",
  },
  debt_pc_rel: {
    label: "State debt per capita",
    benchmark: "the median-state benchmark",
    source: "https://github.com/jacobkap/government_finances",
  },
};

export const percent = (value: number) => `${(100 * value).toFixed(1)}%`;
export const pp = (value: number) => `${(100 * value).toFixed(2)} pp/yr`;
