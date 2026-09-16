# News Crawler

FastAPI + SQLModel + PostgreSQL application that continuously ingests news from the VnEconomy RSS feed.

## Scope

- Crawl RSS on a configurable interval (default 300 seconds / 5 minutes).
- Store articles in PostgreSQL.
- List articles with pagination, title search, and publication-date filtering.
- Get article detail.
- Update article title/description with API-key authentication and editor/admin authorization.
- Expose liveness and readiness endpoints.
- Run crawler as a separate worker process.
- Use Alembic for schema migrations.

## Architecture

```text
HTTP API
  Router -> Service -> Repository -> PostgreSQL

Crawler Worker
  Scheduler -> CrawlerService -> HTTP Client -> RSS
                         |
                         v
                    Repository -> PostgreSQL
```

The API and crawler are intentionally separate processes. The crawler does not require an HTTP request to run.

## Requirements

- Python 3.13+
- uv
- PostgreSQL / Neon

## Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` and put a real database URL and strong API keys in it. Never commit `.env`.

## Database migration

Configure `DATABASE_URL`, then:

```powershell
uv run alembic upgrade head
```

Do not use `SQLModel.metadata.create_all()` in application startup.

## Run API

```powershell
uv run uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Run crawler worker

In a second terminal:

```powershell
uv run python -m app.worker
```

The worker runs one crawl immediately, then repeats using `CRAWLER_INTERVAL_SECONDS`.

## API examples

List:

```text
GET /api/v1/news?page=1&size=10
```

Search:

```text
GET /api/v1/news?title=business
```

Date range:

```text
GET /api/v1/news?from_date=2026-01-01T00:00:00Z&to_date=2026-01-31T23:59:59Z
```

Detail:

```text
GET /api/v1/news/{news_id}
```

Update:

```http
PATCH /api/v1/news/{news_id}
Authorization: Bearer <EDITOR_API_KEY>
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description"
}
```

`PATCH` is intentionally used for partial updates. The original review identified ambiguity in the old `PUT` contract.

Health:

```text
GET /health/live
GET /health/ready
```

## Security

The previously exposed database credential must be rotated/revoked before using this rewritten project. A credential appearing in old Git history remains compromised even if the file is later deleted.

Never put real secrets in `.env.example`, source code, logs, or Git history.

Recommended GitHub controls:

- Secret scanning
- Push protection
- Branch protection
- Required review before merge

## Timezone

All timestamps stored by the application are timezone-aware UTC and API date filters use ISO-8601 timestamps. Incoming RSS dates are normalized to UTC.

## RSS policy

Only successful HTTP responses with an acceptable content size are parsed. HTTP 429 and 5xx responses may be retried with bounded exponential backoff and jitter. Other 4xx responses are not retried.

Malformed entries are skipped and counted in the crawl result rather than stopping the entire run.

## Crawl result

Each run produces a structured result containing:

- run id
- source
- start/end time
- HTTP status
- parsed
- inserted
- skipped
- failed
- error summary

Results are logged so operators can diagnose stale or failing ingestion.

## Development

```powershell
uv run ruff check .
uv run black .
uv run pytest
```
