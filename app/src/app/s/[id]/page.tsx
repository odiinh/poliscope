import { notFound } from "next/navigation";
import { Subject } from "../../../components/subject";
import { profiles } from "../../../lib/data";
import { subjectView } from "../../../lib/subject-view";

export function generateStaticParams() {
  return profiles.filter(({ kind }) => kind === "candidate").map(({ id }) => ({ id }));
}

export default async function SubjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const profile = profiles.find((candidate) => candidate.id === id);
  if (!profile) notFound();

  return (
    <main className="shell">
      <Subject {...subjectView(profile)} />
    </main>
  );
}
