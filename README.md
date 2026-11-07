# PoliScope

PoliScope turns governors’ words into policy fingerprints and compares them with historical precedents.

[Open PoliScope](https://poliscope.hydroxide.uk) · [Current team handoff](docs/PLAN.md#current-handoff)

## Team setup

Install Python 3.11 (or let uv install it), Node.js 24, uv, and pnpm 10.34.9. Run these commands from the repository root.

```sh
uv sync --project pipeline --python 3.11 --locked
pnpm --dir app install --frozen-lockfile
cp -n .env.example .env.local
make check
make dev
```

Open [localhost:3000](http://localhost:3000). The app uses the model export from `data/public/` when it is available. Otherwise it labels the synthetic preview. Local live extraction uses an authenticated Claude CLI on `PATH`. The app loads its local environment from `.env.local` at the repository root.

Run `make sync` after a public data export or prompt update. Run `pnpm --dir app gen:types` to regenerate TypeScript types from the shared schemas. See [the build plan](docs/PLAN.md) for the team briefs and ownership rules.

## Docker deployment

The production image includes the five cached candidate profiles and the schema-checked public export.

```sh
docker compose up -d --build
docker compose ps
```

The app listens on `127.0.0.1:3101`. In Cloudflare Tunnel, publish `poliscope.hydroxide.uk` with service URL `http://localhost:3101`. The deployment uses Grimnir’s existing tunnel. D publishes a checked change with `ssh grimnir 'cd ~/poliscope && git pull --ff-only && docker compose up -d --build && docker compose ps'`. Pushing to `main` shares code with the team. The public site updates when D rebuilds the server image.

Live extraction is disabled in the container while the hosted provider adapter is pending in [issue #1](https://github.com/odiinh/poliscope/issues/1). Local development keeps the authenticated Claude CLI path.

## Data sources

- State of the State transcripts and metadata are available under CC0 1.0. [Speech corpus](https://github.com/leops95/sots)
- The U.S. Census Bureau’s Annual Survey of State Government Finances supplies state debt. [Debt data mirror](https://github.com/jacobkap/government_finances)
- BEA real GDP and U.S. Census population series are retrieved through FRED. [GDP series](https://fred.stlouisfed.org/data/USGOVSLRGSP), [FRED](https://fred.stlouisfed.org/)
- Candidate profiles use public campaign platforms. The app attributes each quote to its source. [Data coverage and source terms](docs/status/a.md#sources-and-licences-for-the-readme)
