from pydantic import ValidationError
import pytest

from app.schemas.news import NewsUpdate


def test_news_update_rejects_blank_title() -> None:
    with pytest.raises(ValidationError):
        NewsUpdate(title="   ")


def test_news_update_accepts_partial_update() -> None:
    payload = NewsUpdate(title="  New title  ")
    assert payload.title == "New title"
    assert payload.description is None
