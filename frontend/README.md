# Codebase Onboarding Agent — Frontend

React (Vite) UI for the RAG backend in `../backend`. Three views:

1. **Index Repo** — paste a GitHub URL, calls `POST /repos/index`.
2. **Chat** — ask questions about the indexed repo, calls `POST /repos/{repo_id}/ask`.
3. **History** — past Q&A pairs for the repo, calls `GET /repos/{repo_id}/history`.

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local   # only needed if the backend isn't on 127.0.0.1:8000
npm run dev
```

Open **http://localhost:5173**. The backend must already be running (see
`../backend/README` / root `README.md`) — this app is a pure client that
talks to it over HTTP; it has no server of its own.

## How it talks to the backend

`src/api.js` is the only file that calls `fetch()`. Every component
(`RepoInput`, `Chat`, `History`) imports functions from it and never
constructs a request itself. The base URL comes from the
`VITE_API_BASE_URL` env var (default `http://127.0.0.1:8000`).

Because the dev server runs on a different origin
(`http://localhost:5173`) than the API (`http://127.0.0.1:8000`), the
browser enforces CORS: it will only let this page read the response if
the backend explicitly allows that origin. That's configured in
`backend/app/main.py`'s `CORSMiddleware` — see the root README for
details. Without it, every fetch above would fail with a CORS error
even though the backend itself works fine (e.g. via `/docs` or curl).

## Build

```bash
npm run build   # outputs to dist/
npm run lint    # oxlint
```

## Deployment (e.g. Vercel)

Set `VITE_API_BASE_URL` to the deployed backend's URL as an environment
variable on the hosting platform — nothing in the code needs to change,
`src/api.js` already reads it. On Vercel: Project → Settings →
Environment Variables → add `VITE_API_BASE_URL` (e.g.
`https://codebase-onboarding-agent-ecc8.onrender.com`) for the
Production environment, then redeploy.

That last part matters: Vite inlines `import.meta.env.VITE_*` values
into the built JS at **build time**, not read at runtime in the
browser. Saving the env var in Vercel's dashboard doesn't retroactively
change an already-built deployment — it only takes effect on the next
build, so trigger a redeploy after adding or changing it.

The backend's CORS config is the other half of this: it only accepts
requests from origins listed in its `ALLOWED_ORIGINS` env var (see
`backend/.env.example`). Once you have your Vercel URL, set it there
too (on Render's dashboard for this service) — otherwise the browser
will block every request with a CORS error even though
`VITE_API_BASE_URL` is pointed at the right place.
