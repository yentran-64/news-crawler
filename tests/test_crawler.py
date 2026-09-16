from datetime import UTC, datetime

from app.services.crawler_service import CrawlerService


def test_parse_entry_datetime_normalizes_to_utc() -> None:
    value = CrawlerService._parse_entry_datetime(
        {"published": "Thu, 20 Aug 2026 10:00:00 +0700"}
    )
    assert value == datetime(2026, 8, 20, 3, 0, tzinfo=UTC)


def test_parse_entry_datetime_returns_none_for_invalid_value() -> None:
    assert CrawlerService._parse_entry_datetime({"published": "bad"}) is None
