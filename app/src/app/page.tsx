import Link from "next/link";
import { PlatformForm } from "../components/platform-form";
import { fixtureMode, profiles } from "../lib/data";

export default function Home() {
  const candidates = profiles.filter(({ kind }) => kind === "candidate");
  const historicalPreview = !fixtureMode && candidates.length === 0;
  const subjects = historicalPreview ? profiles.filter(({ kind }) => kind === "historical") : candidates;
  return (
    <main className="shell space-y-6">
      <header className="space-y-3">
        <p className="eyebrow">Policy and precedent</p>
        <h1>Every promise has a precedent.</h1>
        <p className="max-w-xl text-lg text-muted-foreground">
          Explore governors’ policy fingerprints, similar historical terms, and what those precedents can tell us about state outcomes.
        </p>
      </header>
      <section className="panel" aria-labelledby="candidates">
        <h2 id="candidates">{fixtureMode ? "Example candidate" : historicalPreview ? "Historical terms" : "Governors-elect"}</h2>
        {fixtureMode && <p className="text-muted-foreground">This preview uses synthetic profiles and outcomes.</p>}
        {historicalPreview && <p>Explore available historical profiles while the candidate set is being prepared.</p>}
        {subjects.length ? (
          <ul className="grid gap-3 sm:grid-cols-2">
            {subjects.map(({ id, name, state, term_start }) => (
              <li key={id}>
                <Link className="block rounded-lg border border-border p-4 hover:bg-muted" href={`/s/${id}`} prefetch={historicalPreview ? false : undefined}>
                  <strong>{name}</strong>
                  <span className="block text-sm text-muted-foreground">{state} · {term_start}</span>
                </Link>
              </li>
            ))}
          </ul>
        ) : <p>No profiles are available yet.</p>}
      </section>
      <PlatformForm />
    </main>
  );
}
