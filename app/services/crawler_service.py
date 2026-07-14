from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import feedparser

from app.models.news import News
from app.repositories.news_repository import NewsRepository


class CrawlerService:
    RSS_URL = "https://en.vneconomy.vn/rss.html"

    def __init__(self, repository: NewsRepository):
        self.repository = repository

    def crawl(self) -> int:
        feed = feedparser.parse(self.RSS_URL)

        inserted = 0

        for entry in feed.entries:

            if self.repository.get_by_link(entry.link):
                continue

            news = News(
                title=entry.title,
                description=entry.get("description", ""),
                link=entry.link,
                pub_date=self._parse_datetime(entry),
            )

            self.repository.create(news)

            inserted += 1

        return inserted

    @staticmethod
    def _parse_datetime(entry) -> datetime:
        if "published" in entry:
            return parsedate_to_datetime(entry.published)

        return datetime.now(UTC)