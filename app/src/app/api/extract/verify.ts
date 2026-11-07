// TypeScript port of pipeline/extract/verify.py; keep the two in step.
import type { DimScore } from "@/types/contracts";

export type RawScore = Partial<Omit<DimScore, "evidence">> & { evidence?: string[] };

const SWAP: Record<string, string> = {
  "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
  "“": '"', "”": '"', "„": '"', "‟": '"', "″": '"',
  "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "―": "-", "−": "-",
};
const SWAP_RE = new RegExp(`[${Object.keys(SWAP).join("")}]`, "g");
const clamp = (v: unknown, lo: number) => Math.max(lo, Math.min(1, Number(v) || 0));

export function normalise(text: string): string {
  return text.replace(SWAP_RE, (c) => SWAP[c]).replace(/\s+/g, " ").trim();
}

/** Keep only quotes that are exact substrings of source; a dimension with none becomes null. */
export function verifyDims(dims: Record<string, RawScore>, source: string) {
  const haystack = normalise(source);
  const out: Record<string, DimScore> = {};
  let kept = 0;
  let given = 0;
  for (const [id, score] of Object.entries(dims)) {
    const quotes = (score.evidence ?? []).map((q) => q.trim()).filter(Boolean);
    given += quotes.length;
    const good = quotes
      .filter((q) => q.split(/\s+/).length <= 40 && haystack.includes(normalise(q)))
      .slice(0, 3);
    kept += good.length;
    out[id] =
      score.stance == null || good.length === 0
        ? { stance: null, salience: 0, confidence: 0, evidence: [] }
        : {
            stance: clamp(score.stance, -1),
            salience: clamp(score.salience, 0),
            confidence: clamp(score.confidence, 0),
            evidence: good as DimScore["evidence"],
          };
  }
  return { dims: out, kept, given };
}
