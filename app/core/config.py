from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "News Crawler"

    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True

    DATABASE_URL: str = Field(...)

    RSS_URL: str = Field(...)

    CRAWLER_INTERVAL: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()