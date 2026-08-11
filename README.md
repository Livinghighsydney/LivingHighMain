# Living High — Website Revamp

Full rebuild of [livinghigh.com.au](https://livinghigh.com.au) off WordPress onto
**Next.js (frontend) + FastAPI (backend)**, matching the Living High KB stack.

> See [`CLAUDE.md`](./CLAUDE.md) for the full project brief: migration approach,
> what must carry over exactly (URLs, Meta Pixel, GTM), staging/rollout plan, and
> security requirements. Read it before making changes.

## Repo layout

```
LivingHighMain/
├─ frontend/   # Next.js (App Router, TypeScript, Tailwind) — deploys to Vercel
├─ backend/    # FastAPI (Postgres, slowapi rate-limiting) — deploys to Railway
├─ docs/       # migration / deployment / rollout notes
└─ CLAUDE.md   # project brief & guardrails
```

## Getting started

This repo currently contains **structure + config only** — no dependencies are
installed yet. To bring each app online:

### Frontend

```bash
cd frontend
cp .env.example .env.local     # fill in values
npm install
npm run dev                    # http://localhost:3000
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1     # PowerShell (Windows)
pip install -r requirements.txt
cp .env.example .env           # fill in values
uvicorn app.main:app --reload  # http://localhost:8000
```

## Non-negotiables (from CLAUDE.md)

- **Preserve URL structure** and reuse the existing **Meta Pixel**
  (`2502462696653746`) + **GTM** (`GTM-T4NPBPPZ`) — do not mint new IDs.
- **Secrets live in Vercel/Railway env vars**, never in the repo.
- Security is built in from the start: rate limiting, locked CORS, HTTPS/HSTS,
  security headers, server-side input validation, Sentry.

## Out of scope (for now)

Payment/checkout, booking calendar engine, chat-widget embed (waiting on KB),
owner portal. Conversion flow is **listing → lead form / WhatsApp → human**.
