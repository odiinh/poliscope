"use client";

import { map } from "../lib/data";
import { project } from "../lib/project";
import { subjectView } from "../lib/subject-view";
import type { Profile } from "../types/contracts";
import { Subject } from "./subject";

export default function LiveSubject({ profile }: { profile: Profile }) {
  const projected = map ? project(profile, map) : undefined;
  return <Subject {...subjectView(profile, { pasted: true, projected })} />;
}
