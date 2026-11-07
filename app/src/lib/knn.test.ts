import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import parityJson from "../generated/knn_parity.json";
import type { KnnParity, MapData, Outcome, Profile } from "../types/contracts";
import { map, outcomes, profiles, publicInputs } from "./data";
import { nearestForecast } from "./knn";
import { dimensions } from "./policy";
import { project } from "./project";

const tolerance = 1e-9;

function fixture<T>(filename: string): T {
  return JSON.parse(readFileSync(new URL(`../../../contracts/fixtures/${filename}.json`, import.meta.url), "utf8")) as T;
}

function expectNear(actual: number, expected: number) {
  expect(Math.abs(actual - expected)).toBeLessThanOrEqual(tolerance);
}

function checkForecasts({ cases }: KnnParity, profiles: Profile[], outcomes: Outcome[]) {
  test("parity cases are present", () => {
    expect(cases.length).toBeGreaterThan(0);
  });

  test.each(cases)("matches kNN parity for $query.id ($metric)", ({ query, metric, baseline, expected }) => {
    const actual = nearestForecast(query, metric, baseline, profiles, outcomes, expected.note);
    expect(actual).not.toBeNull();
    if (!actual) return;
    expect(actual.subject_id).toBe(expected.subject_id);
    expect(actual.metric).toBe(expected.metric);
    for (const key of ["baseline", "forecast", "p10", "p90", "p_above"] as const) {
      expectNear(actual[key], expected[key]);
    }
    expect(actual.neighbours.map(({ id }) => id)).toEqual(expected.neighbours.map(({ id }) => id));
    actual.neighbours.forEach((row, index) => {
      const other = expected.neighbours[index];
      expectNear(row.distance, other.distance);
      expectNear(row.weight, other.weight);
      expectNear(row.residual, other.residual);
    });
  });
}

function checkProjection(profiles: Profile[], map: MapData) {
  test("matches the exported PCA coordinates", () => {
    const positions = new Map(map.points.map((point) => [point.id, point]));
    for (const profile of profiles) {
      const expected = positions.get(profile.id);
      expect(expected).toBeDefined();
      if (!expected) continue;
      const actual = project(profile, map);
      expectNear(actual.x, expected.x);
      expectNear(actual.y, expected.y);
    }
  });
}

const fixtureProfiles = fixture<Profile[]>("profiles");
const fixtureOutcomes = fixture<Outcome[]>("outcomes");
describe("contract fixtures", () => {
  checkForecasts(fixture<KnnParity>("knn_parity"), fixtureProfiles, fixtureOutcomes);
  checkProjection(fixtureProfiles, fixture<MapData>("map"));
});

if (publicInputs.has("knn_parity.json")) {
  describe("Python model export", () => {
    checkForecasts(parityJson as unknown as KnnParity, profiles, outcomes);
  });
}
if (publicInputs.has("map.json") && map) checkProjection(profiles, map);

test("uses the Python neighbour order when distances differ at machine precision", () => {
  const base = fixtureProfiles[0];
  function withStances(profile: Profile, stances: number[], confidences: number[]) {
    const dims = Object.fromEntries(dimensions.map(({ id }, index) => [id, {
      ...profile.dims[id], stance: stances[index], confidence: confidences[index],
    }])) as Profile["dims"];
    return { ...profile, dims };
  }
  const zeroes = Array<number>(10).fill(0);
  const ones = Array<number>(10).fill(1);
  const query = withStances({ ...base, id: "mi-2027", kind: "candidate" }, zeroes, ones);
  const precedents = fixtureProfiles.slice(0, 7).map((profile) => withStances(profile, zeroes, ones));
  precedents[5] = withStances(precedents[5],
    [0.4, -0.2, 0.8, -1, -0.8, 0.2, 0, -0.6, 0.6, -0.8],
    [0.7, 0.6, 0.8, 0.6, 0.3, 0.7, 0.3, 0.6, 0.7, 1]);
  precedents[6] = withStances(precedents[6],
    [-0.2, 0.8, 0.4, -0.6, 0.6, -0.8, 0.2, -0.8, 0, -1],
    [0.6, 0.8, 0.7, 0.6, 0.7, 1, 0.7, 0.3, 0.3, 0.6]);

  const actual = nearestForecast(query, "gdp_pc_rel", 0, precedents, fixtureOutcomes);
  expect(actual?.neighbours.slice(-2).map(({ id }) => id)).toEqual([precedents[6].id, precedents[5].id]);
});
