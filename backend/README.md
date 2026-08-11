# Backend — FastAPI

Lead-capture / listings API. Deploys to **Railway**. Postgres for data.

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1     # PowerShell (Windows)
pip install -r requirements.txt
cp .env.example .env           # fill in values
uvicorn app.main:app --reload  # http://localhost:8000
```

Health check: `GET http://localhost:8000/health`

## Security (already wired in `app/main.py`)

- **Rate limiting** via slowapi — a conservative global default is set; add
  stricter `@limiter.limit(...)` on form/login endpoints (CLAUDE.md).
- **CORS** locked to `CORS_ORIGINS` (never `*`).
- **Security headers** (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, HSTS in production) via middleware.
- **Sentry** initialised when `SENTRY_DSN` is set.
- Secrets come from env only — never commit `.env`.

## Structure

```
app/
├─ main.py         # entrypoint: CORS, rate limiting, security headers, /health
├─ core/config.py  # env-based settings (pydantic-settings)
├─ api/            # route modules (add here)
└─ models/         # SQLAlchemy models (listing/property schema)
scripts/           # one-time migration scripts (WP REST API → new schema)
```

## Migration scripts

The WordPress → new-schema migration (WP REST API export, Cloudinary image
upload, old→new URL mapping) lives in `scripts/`. See CLAUDE.md "Migration
approach". Do **not** migrate the raw WP MySQL DB.