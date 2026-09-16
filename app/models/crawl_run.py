from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, SQLModel


class CrawlRun(SQLModel, table=True):
    __tablename__ = "crawl_runs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source: str = Field(max_length=2000)
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    finished_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    http_status: int | None = None
    parsed: int = 0
    inserted: int = 0
    skipped: int = 0
    failed: int = 0
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
