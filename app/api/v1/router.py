from fastapi import APIRouter

from app.api.v1.news import router as news_router

api_router = APIRouter()

api_router.include_router(news_router)