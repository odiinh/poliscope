import type { MapData, Profile } from "../types/contracts";
import { dimensions } from "./policy";

export function project(profile: Profile, map: MapData): MapData["points"][number] {
  const centred = dimensions.map(({ id }, index) => {
    const stance = profile.dims[id].stance;
    return stance === null ? 0 : stance - map.mean[index];
  });
  const [x, y] = map.components.map((component) =>
    component.reduce((sum, weight, index) => sum + weight * centred[index], 0));
  return { id: profile.id, x, y };
}
