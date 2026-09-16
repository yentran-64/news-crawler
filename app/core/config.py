from functools import lru_cache

from pydantic import Field, PositiveInt, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "News Crawler"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: SecretStr

    rss_url: str = "https://en.vneconomy.vn/rss.html"
    crawler_interval_seconds: PositiveInt = Field(default=300, le=86400)

    http_connect_timeout_seconds: PositiveInt = Field(default=5, le=120)
    http_read_timeout_seconds: PositiveInt = Field(default=15, le=300)
    http_write_timeout_seconds: PositiveInt = Field(default=5, le=120)
    http_pool_timeout_seconds: PositiveInt = Field(default=5, le=120)
    http_max_response_bytes: PositiveInt = Field(default=2_000_000, le=20_000_000)
    http_max_retries: int = Field(default=3, ge=0, le=5)
    http_backoff_base_seconds: float = Field(default=0.5, gt=0, le=30)
    http_max_redirects: int = Field(default=3, ge=0, le=10)

    editor_api_key: SecretStr
    admin_api_key: SecretStr

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        value = value.upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if value not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
