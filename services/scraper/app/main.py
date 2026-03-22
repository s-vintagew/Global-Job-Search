"""
Scraper Worker — Entry Point
Runs an initial scrape on startup, then schedules scrapes every 12 hours.
"""

import time
import logging
import sys
from datetime import datetime
from sqlalchemy import text

from apscheduler.schedulers.blocking import BlockingScheduler

from app.database import SessionLocal, engine
from app.models import Base, Job
from app.geocoder import LocationProcessor, normalize_country
from app.scrapers.remoteok import RemoteOKScraper
from app.scrapers.remotive import RemotiveScraper
from app.scrapers.arbeitnow import ArbeitnowScraper
from app.scrapers.jsearch import JSearchScraper

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("scraper")

# ─── All scrapers ────────────────────────────────────────────
SCRAPERS = [
    RemoteOKScraper(),
    RemotiveScraper(),
    ArbeitnowScraper(),
    JSearchScraper(),
]


def wait_for_db(max_retries: int = 30, delay: float = 2.0):
    """Wait until PostgreSQL is accepting connections."""
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database is ready!")
            return
        except Exception:
            logger.info(
                f"Waiting for DB... ({attempt}/{max_retries})"
            )
            time.sleep(delay)

    logger.error("Could not connect to database. Exiting.")
    sys.exit(1)


def run_scraping_pipeline():
    """Orchestrate all scrapers: fetch → geocode → deduplicate → store."""
    logger.info("=" * 60)
    logger.info(f"Starting scraping pipeline at {datetime.now()}")
    logger.info("=" * 60)

    db = SessionLocal()
    processor = LocationProcessor()
    total_added = 0

    try:
        for scraper in SCRAPERS:
            # JSearch is optional
            if hasattr(scraper, "is_available") and not scraper.is_available():
                continue

            try:
                raw_jobs = scraper.run()
            except Exception as e:
                logger.error(
                    f"[{scraper.source_name}] Scraper crashed: {e}"
                )
                continue

            added = 0
            for job_data in raw_jobs:
                # Deduplicate by URL
                exists = (
                    db.query(Job.id)
                    .filter(Job.url == job_data["url"])
                    .first()
                )
                if exists:
                    continue

                # Geocode
                geo = processor.process_location(job_data.get("city", ""))
                job_data["city"] = geo["city"]
                job_data["country"] = normalize_country(geo["country"])
                job_data["lat"] = geo["lat"]
                job_data["lng"] = geo["lng"]

                db_job = Job(**job_data)
                db.add(db_job)
                added += 1

            db.commit()
            total_added += added
            logger.info(
                f"[{scraper.source_name}] Added {added} new jobs"
            )

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info(f"Pipeline complete — {total_added} total new jobs added")
    logger.info("=" * 60)


def main():
    # 1. Wait for database
    wait_for_db()

    # 2. Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")

    # 3. Initial scrape
    run_scraping_pipeline()

    # 4. Schedule recurring scrapes every 12 hours
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_scraping_pipeline,
        "interval",
        hours=12,
        next_run_time=None,  # Don't run immediately again
    )
    logger.info("Scheduler started — next scrape in 12 hours")
    scheduler.start()


if __name__ == "__main__":
    main()
