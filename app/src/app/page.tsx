import profiles from "../generated/profiles.json";

export default function Home() {
  const candidates = profiles.filter((profile) => profile.kind === "candidate");
  return (
    <main className="mx-auto max-w-2xl space-y-(--poliscope-space) p-(--poliscope-space)">
      <h1 className="text-3xl font-semibold">PoliScope</h1>
      <p>Policy fingerprints and historical precedents.</p>
      <ul aria-label="Candidates">
        {candidates.map(({ id, name, state }) => (
          <li key={id}>{name} ({state})</li>
        ))}
      </ul>
    </main>
  );
}
