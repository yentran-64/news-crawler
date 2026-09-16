import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.models.news import News
from app.repositories.news_repository import NewsRepository
from app.schemas.news import NewsUpdate

logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self, repository: NewsRepository):
        self.repository = repository

    def get_news(
        self,
        page: int,
        size: int,
        title: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[list[News], int]:
        items = self.repository.get_all(
            page=page,
            size=size,
            title=title,
            from_date=from_date,
            to_date=to_date,
        )
        total = self.repository.count(
            title=title,
            from_date=from_date,
            to_date=to_date,
        )
        return items, total

    def get_news_detail(self, news_id: UUID) -> News:
        news = self.repository.get_by_id(news_id)
        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found",
            )
        return news

    def update_news(self, news_id: UUID, payload: NewsUpdate, actor_role: str = "unknown") -> News:
        if payload.title is None and payload.description is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one editable field is required",
            )

        news = self.get_news_detail(news_id)

        if payload.title is not None:
            news.title = payload.title
        if payload.description is not None:
            news.description = payload.description

        news.updated_at = datetime.now(UTC)
        updated = self.repository.update(news)
        logger.info("news_updated news_id=%s actor_role=%s", news_id, actor_role)
        return updated
