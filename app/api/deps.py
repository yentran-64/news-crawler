from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session
from app.repositories import NewsRepository
from app.services import NewsService


def get_news_repository(
    session: Annotated[Session, Depends(get_session)],
) -> NewsRepository:
    return NewsRepository(session)


def get_news_service(
    repository: Annotated[NewsRepository, Depends(get_news_repository)],
) -> NewsService:
    return NewsService(repository)