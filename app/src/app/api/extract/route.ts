// POST {text, state, name?, party?} -> Profile (kind "candidate"), scored with the batch prompt.
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import dimensions from "@/generated/dimensions.json";
import type { DimScore, Party, Profile } from "@/types/contracts";
import { verifyDims, type RawScore } from "./verify";

export const maxDuration = 60;

const MAX_CHARS = 60_000;
const MODEL = process.env.LLM_MODEL_LIVE || "sonnet";
const PARTIES: Party[] = ["D", "R", "I"];
const EMPTY: DimScore = { stance: null, salience: 0, confidence: 0, evidence: [] };
// shortcut: per-instance memory cache, lost on restart; fine for a demo
const cache = new Map<string, Record<string, DimScore>>();

const SCORE_SCHEMA = {
  type: "object",
  properties: {
    stance: { type: ["number", "null"], minimum: -1, maximum: 1 },
    salience: { type: "number", minimum: 0, maximum: 1 },
    confidence: { type: "number", minimum: 0, maximum: 1 },
    evidence: { type: "array", items: { type: "string" }, maxItems: 3 },
  },
  required: ["stance", "salience", "confidence", "evidence"],
  additionalProperties: false,
};
const OUTPUT_SCHEMA = JSON.stringify({
  type: "object",
  properties: Object.fromEntries(dimensions.map((d) => [d.id, SCORE_SCHEMA])),
  required: dimensions.map((d) => d.id),
  additionalProperties: false,
});

async function systemPrompt() {
  const template = await readFile(path.join(process.cwd(), "src/generated/extract_v1.md"), "utf8");
  const lines = dimensions.map((d) => `- \`${d.id}\` (${d.label}): −1 = ${d.minus}; +1 = ${d.plus}`);
  return template.replace("{{DIMENSIONS}}", lines.join("\n"));
}

// shortcut: shells out to the local Claude Code CLI, so this route only works where `claude` is
// installed and logged in (make dev), not on Vercel; swap in an API client to deploy it
async function runClaude(text: string): Promise<Record<string, RawScore>> {
  const args = [
    "-p", "--model", MODEL, "--output-format", "json", "--tools", "",
    "--no-session-persistence", "--setting-sources", "",
    "--system-prompt", await systemPrompt(), "--json-schema", OUTPUT_SCHEMA,
  ];
  return new Promise((resolve, reject) => {
    const child = spawn("claude", args, { timeout: 55_000 });
    let stdout = "";
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      try {
        const res = JSON.parse(stdout);
        if (res.is_error || typeof res.structured_output !== "object") throw new Error(res.result);
        resolve(res.structured_output);
      } catch {
        reject(new Error(`claude exited ${code}`));
      }
    });
    child.stdin.end(text);
  });
}

const bad = (error: string, status = 400) => Response.json({ error }, { status });

export async function POST(req: Request) {
  const body: unknown = await req.json().catch(() => null);
  if (typeof body !== "object" || body === null) return bad("Body must be a JSON object");
  const { text, state, name, party } = body as Record<string, unknown>;
  if (typeof text !== "string" || !text.trim()) return bad("text is required");
  if (text.length > MAX_CHARS) return bad(`text is over ${MAX_CHARS} characters`, 413);
  if (typeof state !== "string" || !/^[A-Z]{2}$/.test(state)) return bad("state must be a two-letter code");
  if (name !== undefined && typeof name !== "string") return bad("name must be a string");
  if (party !== undefined && !PARTIES.includes(party as Party)) return bad("party must be D, R or I");

  const sha1 = createHash("sha1").update(text).digest("hex");
  let dims = cache.get(sha1);
  if (!dims) {
    try {
      dims = verifyDims(await runClaude(text), text).dims;
    } catch (e) {
      return bad(`Extraction failed: ${(e as Error).message}`, 502);
    }
    cache.set(sha1, dims);
  }
  const profile: Profile = {
    id: `${state.toLowerCase()}-2027`,
    kind: "candidate",
    name: (name as string | undefined)?.trim() || "Pasted text",
    state,
    // shortcut: pasted text has no party, so "I" stands in; only the party comparator reads it
    party: (party as Party | undefined) ?? "I",
    term_start: 2027,
    source: { type: "pasted", year: new Date().getFullYear(), url: "", sha1 },
    dims: Object.fromEntries(dimensions.map((d) => [d.id, dims[d.id] ?? EMPTY])) as Profile["dims"],
    extractor: { model: MODEL, prompt_version: "v1" },
  };
  return Response.json(profile);
}
