from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env.

    Secrets must come from the environment (Railway env vars in production),
    never hard-coded — see CLAUDE.md security requirements.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # CORS: comma-separated allowed origins. Never "*". See CLAUDE.md.
    cors_origins: str = "http://localhost:3000"

    # Tortoise ORM URL form, e.g. postgres://user:password@host:5432/dbname
    database_url: str = ""
    sentry_dsn: str = ""

    # WordPress migration source
    wp_base_url: str = ""
    wc_consumer_key: str = ""
    wc_consumer_secret: str = ""
    cloudinary_url: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
