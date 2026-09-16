import logging
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from uuid import UUID, uuid4

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.models.crawl_run import CrawlRun
from app.models.news import News
from app.repositories.news_repository import NewsRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CrawlResult:
    run_id: UUID
    source: str
    started_at: datetime
    finished_at: datetime
    http_status: int | None
    parsed: int
    inserted: int
    skipped: int
    failed: int
    error: str | None


class CrawlerService:
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self, repository: NewsRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def crawl(self) -> CrawlResult:
        run_id = uuid4()
        started_at = datetime.now(UTC)
        parsed = inserted = skipped = failed = 0
        http_status: int | None = None
        error: str | None = None

        try:
            content, http_status = self._fetch_feed()
            feed = feedparser.parse(content)

            if getattr(feed, "bozo", False) and not feed.entries:
                raise ValueError("RSS feed could not be parsed")

            for entry in feed.entries:
                parsed += 1
                try:
                    news = self._entry_to_news(entry)
                    if news is None:
                        failed += 1
                        continue

                    if self.repository.insert_if_absent(news):
                        inserted += 1
                    else:
                        skipped += 1
                except (ValueError, TypeError, KeyError) as exc:
                    failed += 1
                    logger.warning(
                        "crawl_entry_failed run_id=%s error=%s",
                        run_id,
                        type(exc).__name__,
                    )
                except SQLAlchemyError:
                    self.repository.session.rollback()
                    raise

            self.repository.session.commit()

        except Exception as exc:
            self.repository.session.rollback()
            error = type(exc).__name__
            logger.exception("crawl_failed run_id=%s source=%s", run_id, self.settings.rss_url)

        finished_at = datetime.now(UTC)
        result = CrawlResult(
            run_id=run_id,
            source=self.settings.rss_url,
            started_at=started_at,
            finished_at=finished_at,
            http_status=http_status,
            parsed=parsed,
            inserted=inserted,
            skipped=skipped,
            failed=failed,
            error=error,
        )
        self.repository.session.add(
            CrawlRun(
                id=result.run_id,
                source=result.source,
                started_at=result.started_at,
                finished_at=result.finished_at,
                http_status=result.http_status,
                parsed=result.parsed,
                inserted=result.inserted,
                skipped=result.skipped,
                failed=result.failed,
                error=result.error,
            )
        )
        try:
            self.repository.session.commit()
        except SQLAlchemyError:
            self.repository.session.rollback()
            logger.exception("crawl_result_persist_failed run_id=%s", result.run_id)

        logger.info(
            "crawl_finished run_id=%s source=%s status=%s parsed=%s inserted=%s "
            "skipped=%s failed=%s duration_seconds=%.3f",
            result.run_id,
            result.source,
            result.http_status,
            result.parsed,
            result.inserted,
            result.skipped,
            result.failed,
            (result.finished_at - result.started_at).total_seconds(),
        )
        return result

    def _fetch_feed(self) -> tuple[bytes, int]:
        timeout = httpx.Timeout(
            connect=self.settings.http_connect_timeout_seconds,
            read=self.settings.http_read_timeout_seconds,
            write=self.settings.http_write_timeout_seconds,
            pool=self.settings.http_pool_timeout_seconds,
        )

        headers = {"User-Agent": "news-crawler/1.0"}

        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            max_redirects=self.settings.http_max_redirects,
            headers=headers,
        ) as client:
            for attempt in range(self.settings.http_max_retries + 1):
                try:
                    response = client.get(self.settings.rss_url)
                    if response.status_code in self.RETRYABLE_STATUS_CODES:
                        if attempt >= self.settings.http_max_retries:
                            response.raise_for_status()
                        self._sleep_before_retry(attempt)
                        continue

                    response.raise_for_status()

                    content = response.content
                    if len(content) > self.settings.http_max_response_bytes:
                        raise ValueError("RSS response exceeds configured size limit")

                    content_type = response.headers.get("content-type", "").lower()
                    if content_type and not (
                        "xml" in content_type
                        or "rss" in content_type
                        or "atom" in content_type
                        or "text/plain" in content_type
                        or "text/html" in content_type
                    ):
                        raise ValueError(
                            f"Unexpected RSS content type: {content_type}"
                        )

                    return content, response.status_code

                except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout):
                    if attempt >= self.settings.http_max_retries:
                        raise
                    self._sleep_before_retry(attempt)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in self.RETRYABLE_STATUS_CODES:
                        if attempt >= self.settings.http_max_retries:
                            raise
                        self._sleep_before_retry(attempt)
                        continue
                    raise

        raise RuntimeError("RSS request failed")

    def _sleep_before_retry(self, attempt: int) -> None:
        delay = self.settings.http_backoff_base_seconds * (2**attempt)
        jitter = random.uniform(0, delay * 0.25)
        time.sleep(delay + jitter)

    @staticmethod
    def _entry_to_news(entry) -> News | None:
        title = str(entry.get("title", "")).strip()
        link = str(entry.get("link", "")).strip()
        description = CrawlerService._to_plain_text(entry.get("description", ""))

        if not title or not link:
            return None

        pub_date = CrawlerService._parse_entry_datetime(entry)
        if pub_date is None:
            return None

        return News(
            title=title[:500],
            description=description,
            link=link[:2000],
            pub_date=pub_date,
        )

    @staticmethod
    def _to_plain_text(value: str) -> str:
        return BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)

    @staticmethod
    def _parse_entry_datetime(entry) -> datetime | None:
        raw = entry.get("published") or entry.get("updated")
        if not raw:
            return None

        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)

        return parsed.astimezone(UTC)
