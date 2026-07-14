from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NewsUpdate(BaseModel):
    title: str
    description: str


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