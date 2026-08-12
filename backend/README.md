# Backend — FastAPI

Lead-capture / listings API. Deploys to **Railway**. Postgres for data.

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1     # PowerShell (Windows)
pip install -r requirements.txt
cp .env.example .env           # fill in values (incl. DATABASE_URL)

# First time only — create migrations dir + tables from the models:
aerich init-db

uvicorn app.main:app --reload  # http://localhost:8000
```

Health check: `GET http://localhost:8000/health` (works even without a DB).

> Python note: pinned deps target CPython 3.12/3.13. If `asyncpg` has no wheel
> for your Python (e.g. 3.14 is very new), use a 3.12/3.13 venv for now.

## Database — Tortoise ORM + Aerich

Config lives in `app/db.py` (`TORTOISE_ORM`), wired to Aerich via
`pyproject.toml` (`[tool.aerich]`). Tortoise is initialised on app startup in
`app/main.py` when `DATABASE_URL` is set.

```bash
aerich init-db                 # first migration + apply (run once)
aerich migrate --name <change> # after editing models: generate a migration
aerich upgrade                 # apply pending migrations
aerich downgrade               # roll back
```

Models live in `app/models/` and are all re-exported from `app/models/__init__.py`
(so Aerich discovers them via the "app.models" entry).

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
├─ db.py           # TORTOISE_ORM config (used by app + Aerich)
├─ core/config.py  # env-based settings (pydantic-settings)
├─ api/            # route modules (add here)
└─ models/         # Tortoise models
     ├─ base.py    #   TimestampedModel, ContentBase (path/SEO/i18n), PublishStatus
     ├─ content.py #   Locale, Suburb, Category, MediaAsset, Listing, Page, Post
     ├─ leads.py   #   Lead (the listing -> lead -> human conversion flow)
     └─ system.py  #   Redirect (legacy URL map), AdminUser (2FA)
migrations/        # Aerich-generated migrations (created by `aerich init-db`)
scripts/           # one-time migration scripts (WP dump/REST API → new schema)
```

## Migration scripts

The WordPress → new-schema migration (WP REST API export, Cloudinary image
upload, old→new URL mapping) lives in `scripts/`. See CLAUDE.md "Migration
approach". Do **not** migrate the raw WP MySQL DB.