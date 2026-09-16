from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def clean_required_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be empty")
    return value


class NewsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, min_length=1, max_length=100_000)

    @field_validator("title", "description")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return None if value is None else clean_required_text(value)


class NewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    link: str
    pub_date: datetime
    created_at: datetime
    updated_at: datetime


class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int
    page: int
    size: int
