import dimensionJson from "../generated/dimensions.json";
import type { DimId, Metric } from "../types/contracts";

export const dimensions = dimensionJson as (typeof dimensionJson[number] & { id: DimId })[];
export const metricIds = ["gdp_pc_rel", "debt_pc_rel"] as const satisfies readonly Metric[];

export const metrics: Record<Metric, { label: string; outcome: string; benchmark: string; source: string }> = {
  gdp_pc_rel: {
    label: "Real GDP per capita",
    outcome: "real GDP per capita growth",
    benchmark: "the US benchmark",
    source: "https://fred.stlouisfed.org/data/USGOVSLRGSP",
  },
  debt_pc_rel: {
    label: "State debt per capita",
    outcome: "state debt per capita growth",
    benchmark: "the median-state benchmark",
    source: "https://github.com/jacobkap/government_finances",
  },
};

export const percent = (value: number) => `${(100 * value).toFixed(1)}%`;
export const pp = (value: number) => `${(100 * value).toFixed(2)} pp/yr`;

export function sourceUrl(url: string) {
  try {
    const { protocol } = new URL(url);
    return protocol === "https:" || protocol === "http:" ? url : undefined;
  } catch {
    return undefined;
  }
}
