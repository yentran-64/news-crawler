from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.repositories.news_repository import NewsRepository
from app.services.news_service import NewsService

bearer_scheme = HTTPBearer(auto_error=False)


def get_news_repository(
    session: Annotated[Session, Depends(get_session)],
) -> NewsRepository:
    return NewsRepository(session)


def get_news_service(
    repository: Annotated[NewsRepository, Depends(get_news_repository)],
) -> NewsService:
    return NewsService(repository)


def require_editor_or_admin(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> str:
    if credentials is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if token == settings.admin_api_key.get_secret_value():
        return "admin"
    if token == settings.editor_api_key.get_secret_value():
        return "editor"

    from fastapi import HTTPException, status

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_admin(
    role: Annotated[str, Depends(require_editor_or_admin)],
) -> str:
    from fastapi import HTTPException, status

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )
    return role
