# AGENTS.md: PoliScope

## Start here
- The plan is docs/PLAN.md. Read all of it before doing anything.
- Your human will say "I am team member N" (any wording with a number 1-4).
  1 = A Data, 2 = B Extraction, 3 = C Model, 4 = D App and integration.
  Follow that member's brief in the plan's "Agent briefs" section, in order.
- Resume from docs/status/<letter>.md: skip steps already logged as done.
- After the logged brief is complete, take your next action from the plan's
  Current handoff section.
- If contracts/ does not exist yet, member 4 has not bootstrapped the repo.
  Members 1-3: tell your human and stop.

## How to work
- Act without asking inside your own folders (see Team roles in the plan).
- Ask your human only for API keys or logins, a browser task you cannot do,
  a change to contracts/, or a gate you have missed twice.
- Never wait for a teammate: build against contracts/fixtures/ until the real
  file lands. Run git pull before every step.
- After every step: make check, commit as "[<letter>] what changed", then
  git fetch && git rebase origin/main && make check && git push origin HEAD:main
  (repeat if the push is rejected). Append one line to docs/status/<letter>.md:
  time, step, done or blocked, key numbers.
- Run date at every step. If you are behind a gate, take its fallback from the
  plan's Risks section instead of pushing on. From 09:30, fix bugs only.

## Contracts are law
- contracts/ and the plan's "Contract types" define every shared file. Never change them.
- data/public/ is written only by make export; app/src/generated/ only by make sync.
- JSON keys are snake_case. An unknown stance is null, never 0.
- Growth values are decimals per year: 0.004 = 0.4 percentage points.

## Code style
- Python 3.11, pandas, ruff format; scripts run as python -m pipeline.<stage>.<script>.
- TypeScript strict, Next.js App Router, Tailwind + shadcn/ui, Recharts only.
- Import types from app/src/types/contracts.ts (generated). Never redefine them.
- Colours, fonts and spacing come from app/src/styles/theme.ts only.
- Neutral wording: "precedent", "associated with". No rankings, no good or bad.
- Every number in the UI shows its unit and links to its source.
