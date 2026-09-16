import logging
import signal
import threading

from apscheduler.schedulers.blocking import BlockingScheduler

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import get_session
from app.repositories.news_repository import NewsRepository
from app.services.crawler_service import CrawlerService

logger = logging.getLogger(__name__)


def run_crawl() -> None:
    session = next(get_session())
    try:
        service = CrawlerService(
            repository=NewsRepository(session),
            settings=settings,
        )
        service.crawl()
    finally:
        session.close()


def main() -> None:
    configure_logging(settings)

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_crawl,
        trigger="interval",
        seconds=settings.crawler_interval_seconds,
        id="vneconomy-rss-crawl",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    stop_event = threading.Event()

    def shutdown(signum, frame):
        logger.info("worker_shutdown signal=%s", signum)
        scheduler.shutdown(wait=False)
        stop_event.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info(
        "crawler_worker_started interval_seconds=%s source=%s",
        settings.crawler_interval_seconds,
        settings.rss_url,
    )

    run_crawl()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
