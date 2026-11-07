import { notFound } from "next/navigation";
import { Subject } from "../../../components/subject";
import { forecasts, profiles } from "../../../lib/data";

export function generateStaticParams() {
  return profiles.map(({ id }) => ({ id }));
}

export default async function SubjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const profile = profiles.find((candidate) => candidate.id === id);
  if (!profile) notFound();

  return (
    <main className="shell">
      <Subject profile={profile} forecasts={forecasts.filter((forecast) => forecast.subject_id === id)} />
    </main>
  );
}
