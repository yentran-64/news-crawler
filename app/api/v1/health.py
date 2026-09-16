from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.database import get_session
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready(
    session: Annotated[Session, Depends(get_session)],
):
    healthy = HealthService(session).database_ready()
    if not healthy:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unavailable"},
        )
    return {"status": "ready", "database": "ok"}
