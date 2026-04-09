# MS Learn Dashboard

A Blazor WebAssembly dashboard that visualises my [Microsoft Learn](https://learn.microsoft.com) transcript — modules completed, trophies earned, and certifications achieved.

🔗 **Live site:** <https://quintelier.dev/ms-learn/>

## Features

- **Dashboard** — stats cards (modules, training hours, XP, certifications), monthly-progress bar chart, role-distribution doughnut chart, and a recent-modules list
- **Modules page** — searchable, filterable (product / role / level), sortable, paginated list of all completed modules with links back to MS Learn
- **Achievements page** — certification cards with expiry indicators and a trophy grid
- Data is fetched daily from the MS Learn transcript API via GitHub Actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Blazor WebAssembly (.NET 10) |
| Styling | Bootstrap 5.3 + Bootstrap Icons |
| Charts | Chart.js 4 |
| Hosting | GitHub Pages (`gh-pages` branch) |
| CI/CD | GitHub Actions |

## Running Locally

```bash
cd src/ms-learn
dotnet run
```

Then open <http://localhost:5000> (or the port shown in the terminal).

> The app reads `wwwroot/data/transcript.json`. Run `scripts/fetch_transcript.py` first to get real data, or the placeholder file is used automatically.

## Fetching Transcript Data Manually

```bash
python scripts/fetch_transcript.py
```

This writes the latest transcript JSON to `src/ms-learn/wwwroot/data/transcript.json`.

## GitHub Actions Workflow

The workflow (`.github/workflows/deploy.yml`) runs on every push to `main`, daily at 06:00 UTC, and on manual dispatch:

1. **`fetch-data`** — Python script fetches the MS Learn transcript API and commits the JSON if it changed.
2. **`deploy`** — Publishes the Blazor WASM app with `dotnet publish`, patches the base path to `/ms-learn/`, copies `index.html` → `404.html` for client-side routing, and deploys to the `gh-pages` branch using the JamesIves deploy action.
