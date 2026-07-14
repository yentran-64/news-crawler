from datetime import datetime
from uuid import UUID

from sqlmodel import Session, func, select

from app.models import News


class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, news: News) -> News:
        self.session.add(news)
        self.session.commit()
        self.session.refresh(news)
        return news
    
    def get_by_id(self, news_id: UUID) -> News | None:
        return self.session.get(News, news_id)

    def get_by_link(self, link: str) -> News | None:
        statement = select(News).where(News.link == link)
        return self.session.exec(statement).first()

    def count(self) -> int:
        statement = select(func.count()).select_from(News)
        return self.session.exec(statement).one()

    def get_all(
    self,
    page: int,
    size: int,
    title: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    ):
        statement = select(News)

        if title:
            statement = statement.where(
                News.title.ilike(f"%{title}%")
            )

        if from_date:
            statement = statement.where(
                News.pub_date >= from_date
            )

        if to_date:
            statement = statement.where(
                News.pub_date <= to_date
            )

        statement = statement.offset(
            (page - 1) * size
        ).limit(size)

        return self.session.exec(statement).all()

    def update(self, news: News) -> News:
        self.session.add(news)
        self.session.commit()
        self.session.refresh(news)
        return news