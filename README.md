# PoliScope

PoliScope turns governors’ words into policy fingerprints and compares them with historical precedents.

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

## Vercel

Import the GitHub repository as a Next.js project. Set the root directory to `app`, enable source files outside the root for the build, and use `pnpm build`. The build reads the shared contracts and data export from the repository root. [Vercel root directory settings](https://vercel.com/docs/monorepos/monorepo-faq)

The cached candidate demo can run independently of live extraction. The provider adapter for Vercel is tracked in [issue #1](https://github.com/odiinh/poliscope/issues/1).

## Data sources

- State of the State transcripts and metadata are available under CC0 1.0. [Speech corpus](https://github.com/leops95/sots)
- The U.S. Census Bureau’s Annual Survey of State Government Finances supplies state debt. [Debt data mirror](https://github.com/jacobkap/government_finances)
- BEA real GDP and U.S. Census population series are retrieved through FRED. [GDP series](https://fred.stlouisfed.org/data/USGOVSLRGSP), [FRED](https://fred.stlouisfed.org/)
- Candidate profiles use public campaign platforms. The app attributes each quote to its source. [Data coverage and source terms](docs/status/a.md#sources-and-licences-for-the-readme)
