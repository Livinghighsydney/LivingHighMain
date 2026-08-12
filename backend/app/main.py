"""FastAPI application entrypoint.

Security is built in from the start (see CLAUDE.md "Security requirements"):
rate limiting (slowapi), CORS locked to the frontend domain, and standard
security headers. Sentry is wired up when a DSN is provided. Tortoise ORM is
initialised on startup when DATABASE_URL is set (Aerich owns the schema).
"""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from tortoise import Tortoise

from app.core.config import get_settings
from app.db import TORTOISE_ORM

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Aerich owns schema migrations, so we do NOT generate_schemas here.
    # Skip DB init when DATABASE_URL is unset so /health works without Postgres.
    db_enabled = bool(settings.database_url)
    if db_enabled:
        await Tortoise.init(config=TORTOISE_ORM)
    yield
    if db_enabled:
        await Tortoise.close_connections()


# Rate limiter — add stricter @limiter.limit(...) on form/login endpoints
# especially (CLAUDE.md). A conservative default guards everything.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(title="Living High API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — locked to the configured frontend origin(s), never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Attach standard security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
    return response


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
