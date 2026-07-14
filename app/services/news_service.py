from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.models import News
from app.repositories import NewsRepository
from app.schemas import NewsUpdate


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
        """
        Get news list with pagination and filters.
        """

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
        """
        Get news detail by id.
        """

        news = self.repository.get_by_id(news_id)

        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found",
            )

        return news

    def update_news(
        self,
        news_id: UUID,
        payload: NewsUpdate,
    ) -> News:
        """
        Update a news article.
        """

        news = self.repository.get_by_id(news_id)

        if news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found",
            )

        news.title = payload.title
        news.description = payload.description
        news.updated_at = datetime.now(UTC)

        return self.repository.update(news)