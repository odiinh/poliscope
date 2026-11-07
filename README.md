# PoliScope

PoliScope turns governors' words into policy fingerprints and compares them with historical precedents.

## Team setup

Install Python 3.11 (or let uv install it), Node.js 24, uv, and pnpm 12.16.1. Run these commands from the repository root.

```sh
uv sync --project pipeline --python 3.11 --locked
pnpm --dir app install --frozen-lockfile
cp -n .env.example .env.local
make check
make dev
```

Open [localhost:3000](http://localhost:3000) to see the scaffold with synthetic data. Add extraction credentials to the root `.env.local` when needed. Members 1–3 can work from `contracts/fixtures/` while real data is in progress. See [the build plan](docs/PLAN.md) for briefs, data sources, and branch ownership.

Run `make sync` to refresh app inputs after a public data export or prompt update. Run `pnpm --dir app gen:types` to regenerate TypeScript types from the shared schemas.
