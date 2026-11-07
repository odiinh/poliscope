"use client";

import dynamic from "next/dynamic";
import { useState, type FormEvent } from "react";
import { dimensions } from "../lib/policy";
import type { Profile } from "../types/contracts";

const LiveSubject = dynamic(() => import("./live-subject"), {
  loading: () => <p role="status">Preparing historical comparisons…</p>,
});

const MAX_CHARS = 60_000;
const states = "AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY".split(" ");

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isCandidate(value: unknown): value is Profile {
  if (!record(value)) return false;
  const { dims, source } = value;
  return value.kind === "candidate" && typeof value.id === "string" &&
    typeof value.name === "string" && typeof value.state === "string" &&
    typeof value.term_start === "number" && record(source) && typeof source.url === "string" &&
    record(dims) && dimensions.every(({ id }) => {
      const score = dims[id];
      return record(score) && (score.stance === null || typeof score.stance === "number") &&
        typeof score.confidence === "number" && Array.isArray(score.evidence) &&
        score.evidence.every((quote) => typeof quote === "string");
    });
}

export function PlatformForm() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<Profile | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const text = String(data.get("text") ?? "");
    const state = String(data.get("state") ?? "");
    const name = String(data.get("name") ?? "").trim();
    setError("");
    setResult(null);
    if (!text.trim() || text.length > MAX_CHARS || !states.includes(state)) {
      setError("Select a state and enter up to 60,000 characters of platform text.");
      return;
    }
    setPending(true);
    try {
      const response = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, state, name: name || undefined }),
        signal: AbortSignal.timeout(65_000),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = response.status < 500 && record(payload) && typeof payload.error === "string"
          ? payload.error
          : "Live extraction is unavailable. You can still explore the preloaded profiles.";
        setError(detail);
      } else if (isCandidate(payload)) {
        setResult(payload);
      } else {
        setError("The extractor returned an incomplete profile. Try again.");
      }
    } catch {
      setError("The extraction request could not finish. Try again.");
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      <section className="panel" aria-labelledby="paste">
        <h2 id="paste">Paste a platform</h2>
        <p className="text-sm text-muted-foreground">Enter a public policy statement to extract its fingerprint and compare it with historical terms.</p>
        <form onSubmit={submit} aria-busy={pending} className="space-y-3">
          <fieldset disabled={pending} className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="grid gap-1">
                State or district
                <select name="state" required defaultValue="" className="rounded-lg border border-border bg-background p-2">
                  <option value="" disabled>Select a state</option>
                  {states.map((state) => <option key={state} value={state}>{state}</option>)}
                </select>
              </label>
              <label className="grid gap-1">
                Subject name (optional)
                <input name="name" maxLength={120} className="rounded-lg border border-border bg-background p-2" />
              </label>
            </div>
            <label className="grid gap-1">
              Platform text
              <textarea name="text" rows={6} maxLength={MAX_CHARS} required className="rounded-lg border border-border bg-background p-3" />
            </label>
            <button type="submit" className="rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground disabled:opacity-60">
              {pending ? "Analysing…" : "Analyse platform"}
            </button>
          </fieldset>
        </form>
        {pending && <p role="status">Extracting policy scores and checking quotes. This can take up to a minute.</p>}
        {error && <p role="alert" className="rounded-lg bg-muted p-3">{error}</p>}
        {result && <p role="status">Platform extracted. <a href="#platform-results">View results</a></p>}
      </section>
      {result && <LiveSubject profile={result} />}
    </>
  );
}
