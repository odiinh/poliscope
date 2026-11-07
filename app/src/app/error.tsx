"use client";

export default function ErrorView({ reset }: { reset: () => void }) {
  return (
    <main className="shell">
      <section className="panel">
        <h1>This page could not load</h1>
        <button className="rounded-lg bg-primary px-4 py-2 text-primary-foreground" onClick={reset}>Try again</button>
      </section>
    </main>
  );
}
