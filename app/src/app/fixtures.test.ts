import { expect, test } from "vitest";
import dimensions from "../generated/dimensions.json";
import profiles from "../generated/profiles.json";
import type { DimId } from "../types/contracts";

test("synced profiles expose every shared dimension", () => {
  const ids = dimensions.map((dimension) => dimension.id as DimId);
  expect(ids).toHaveLength(10);
  for (const profile of profiles) {
    expect(Object.keys(profile.dims).sort()).toEqual([...ids].sort());
  }
});
