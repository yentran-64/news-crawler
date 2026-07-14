from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_news_service
from app.schemas import NewsListResponse, NewsResponse, NewsUpdate
from app.services import NewsService

router = APIRouter(
    prefix="/news",
    tags=["News"],
)


@router.get(
    "",
    response_model=NewsListResponse,
)
def get_news(
    service: Annotated[NewsService, Depends(get_news_service)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    title: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
):
    items, total = service.get_news(
        page=page,
        size=size,
        title=title,
        from_date=from_date,
        to_date=to_date,
    )

    return NewsListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{news_id}",
    response_model=NewsResponse,
)
def get_news_detail(
    news_id: UUID,
    service: Annotated[NewsService, Depends(get_news_service)],
):
    return service.get_news_detail(news_id)


@router.put(
    "/{news_id}",
    response_model=NewsResponse,
)
def update_news(
    news_id: UUID,
    payload: NewsUpdate,
    service: Annotated[NewsService, Depends(get_news_service)],
):
    return service.update_news(
        news_id=news_id,
        payload=payload,
    )