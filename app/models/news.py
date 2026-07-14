from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class News(SQLModel, table=True):
    __tablename__ = "news"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str = Field(index=True, max_length=500)

    description: str

    link: str = Field(unique=True, index=True)

    pub_date: datetime

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )