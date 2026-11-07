import Link from "next/link";

export default function NotFound() {
  return (
    <main className="shell">
      <section className="panel">
        <h1>Page unavailable</h1>
        <p>Browse the current candidate profiles from the home page.</p>
        <Link href="/">Return to PoliScope</Link>
      </section>
    </main>
  );
}
