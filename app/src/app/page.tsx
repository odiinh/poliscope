import Link from "next/link";
import { fixtureMode, profiles } from "../lib/data";

export default function Home() {
  const candidates = profiles.filter((profile) => profile.kind === "candidate");
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
        <h2 id="candidates">{fixtureMode ? "Example candidate" : "Governors-elect"}</h2>
        {fixtureMode && <p className="text-muted-foreground">This preview uses synthetic profiles and outcomes.</p>}
        {candidates.length ? (
          <ul className="grid gap-3 sm:grid-cols-2">
            {candidates.map(({ id, name, state, term_start }) => (
              <li key={id}>
                <Link className="block rounded-lg border border-border p-4 hover:bg-muted" href={`/s/${id}`}>
                  <strong>{name}</strong>
                  <span className="block text-sm text-muted-foreground">{state} · {term_start}</span>
                </Link>
              </li>
            ))}
          </ul>
        ) : <p>No candidate profiles are available yet.</p>}
      </section>
      <section className="panel" aria-labelledby="paste">
        <h2 id="paste">Paste a platform</h2>
        <label htmlFor="platform">Platform text</label>
        <textarea id="platform" rows={5} className="w-full rounded-lg border border-border p-3" disabled />
        <p className="text-sm text-muted-foreground">Live extraction will be available when the extraction route is connected.</p>
      </section>
    </main>
  );
}
