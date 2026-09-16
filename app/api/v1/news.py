from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_news_service, require_editor_or_admin
from app.schemas.news import NewsListResponse, NewsResponse, NewsUpdate
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=NewsListResponse)
def get_news(
    service: Annotated[NewsService, Depends(get_news_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    title: str | None = Query(default=None, min_length=1, max_length=200),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
) -> NewsListResponse:
    if from_date and to_date and from_date > to_date:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_date must be less than or equal to to_date",
        )

    items, total = service.get_news(
        page=page,
        size=size,
        title=title.strip() if title else None,
        from_date=from_date,
        to_date=to_date,
    )

    return NewsListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(
    news_id: UUID,
    service: Annotated[NewsService, Depends(get_news_service)],
) -> NewsResponse:
    return service.get_news_detail(news_id)


@router.patch(
    "/{news_id}",
    response_model=NewsResponse,
    dependencies=[Depends(require_editor_or_admin)],
)
def update_news(
    news_id: UUID,
    payload: NewsUpdate,
    service: Annotated[NewsService, Depends(get_news_service)],
) -> NewsResponse:
    return service.update_news(news_id, payload)
