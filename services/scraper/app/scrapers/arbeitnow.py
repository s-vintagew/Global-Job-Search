from app.scrapers.base import BaseScraper
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class ArbeitnowScraper(BaseScraper):
    """Scraper for Arbeitnow's public JSON API (https://www.arbeitnow.com/api/job-board-api)."""

    def __init__(self):
        super().__init__(
            "https://www.arbeitnow.com/api/job-board-api", "arbeitnow"
        )

    def parse_jobs(self, raw_data) -> list[dict]:
        if not raw_data:
            return []

        # Arbeitnow wraps in {"data": [...], "links": {...}, "meta": {...}}
        if isinstance(raw_data, dict):
            items = raw_data.get("data", [])
        elif isinstance(raw_data, list):
            items = raw_data
        else:
            return []

        jobs = []
        for item in items:
            try:
                title = item.get("title", "Unknown Role")
                company = item.get("company_name", "Unknown Company")
                url = item.get("url", "")
                if not url:
                    continue

                description = item.get("description", "")
                description = re.sub(r"<[^>]+>", "", description)
                if len(description) > 500:
                    description = description[:500] + "..."

                raw_location = item.get("location", "Europe")
                is_remote = item.get("remote", False)
                job_type = "remote" if is_remote else "onsite"

                tags_list = item.get("tags", [])
                tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else ""

                # Arbeitnow uses epoch timestamp for created_at
                created_at = item.get("created_at")
                if isinstance(created_at, (int, float)):
                    posted_date = datetime.fromtimestamp(created_at).strftime(
                        "%Y-%m-%d"
                    )
                else:
                    posted_date = datetime.now().strftime("%Y-%m-%d")

                jobs.append({
                    "title": title,
                    "company": company,
                    "city": raw_location,
                    "country": "",
                    "lat": 0.0,
                    "lng": 0.0,
                    "type": job_type,
                    "experience_level": None,
                    "salary": "Competitive",
                    "description": description,
                    "tags": tags_str,
                    "url": url,
                    "source": self.source_name,
                    "posted_date": posted_date,
                })
            except Exception as e:
                logger.warning(f"Arbeitnow parse error: {e}")
                continue

        return jobs
