from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "News Crawler API"}