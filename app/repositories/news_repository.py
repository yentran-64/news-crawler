from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, func, select

from app.models.news import News


class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_if_absent(self, news: News) -> bool:
        statement = (
            insert(News)
            .values(
                id=news.id,
                title=news.title,
                description=news.description,
                link=news.link,
                pub_date=news.pub_date,
                created_at=news.created_at,
                updated_at=news.updated_at,
            )
            .on_conflict_do_nothing(index_elements=[News.link])
        )
        result = self.session.exec(statement)
        return result.rowcount == 1

    def get_by_id(self, news_id: UUID) -> News | None:
        return self.session.get(News, news_id)

    def count(
        self,
        title: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        statement = select(func.count()).select_from(News)

        if title:
            statement = statement.where(News.title.ilike(f"%{title}%"))
        if from_date:
            statement = statement.where(News.pub_date >= from_date)
        if to_date:
            statement = statement.where(News.pub_date <= to_date)

        return self.session.exec(statement).one()

    def get_all(
        self,
        page: int,
        size: int,
        title: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[News]:
        statement = select(News)

        if title:
            statement = statement.where(News.title.ilike(f"%{title}%"))
        if from_date:
            statement = statement.where(News.pub_date >= from_date)
        if to_date:
            statement = statement.where(News.pub_date <= to_date)

        statement = (
            statement
            .order_by(News.pub_date.desc())
            .offset((page - 1) * size)
            .limit(size)
        )

        return list(self.session.exec(statement).all())

    def update(self, news: News) -> News:
        self.session.add(news)
        self.session.commit()
        self.session.refresh(news)
        return news
