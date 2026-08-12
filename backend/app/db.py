"""Tortoise ORM configuration.

Aerich (the migration tool) reads `TORTOISE_ORM` via pyproject.toml
([tool.aerich] tortoise_orm = "app.db.TORTOISE_ORM"). The same dict is used to
initialise Tortoise on FastAPI startup in app/main.py.

DATABASE_URL uses Tortoise's URL form, e.g.
    postgres://user:password@localhost:5432/livinghigh
"""

from app.core.config import get_settings

settings = get_settings()

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            # "aerich.models" must be included so Aerich can track migrations.
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}