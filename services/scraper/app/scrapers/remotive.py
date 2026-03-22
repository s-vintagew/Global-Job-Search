from app.scrapers.base import BaseScraper
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class RemotiveScraper(BaseScraper):
    """Scraper for Remotive's public JSON API (https://remotive.com/api/remote-jobs)."""

    def __init__(self):
        super().__init__("https://remotive.com/api/remote-jobs", "remotive")

    def parse_jobs(self, raw_data) -> list[dict]:
        if not raw_data:
            return []

        # Remotive wraps jobs in {"0": count, "jobs": [...]}
        if isinstance(raw_data, dict):
            items = raw_data.get("jobs", [])
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

                raw_location = item.get("candidate_required_location", "Worldwide")
                tags_list = item.get("tags", [])
                tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else ""

                salary = item.get("salary", "Competitive") or "Competitive"

                # Map Remotive category to a job type hint
                category = item.get("category", "")
                job_type = "remote"  # Remotive is remote-only

                date_str = item.get("publication_date")
                if date_str:
                    try:
                        dt = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                        posted_date = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        posted_date = datetime.now().strftime("%Y-%m-%d")
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
                    "salary": salary,
                    "description": description,
                    "tags": tags_str if tags_str else category,
                    "url": url,
                    "source": self.source_name,
                    "posted_date": posted_date,
                })
            except Exception as e:
                logger.warning(f"Remotive parse error: {e}")
                continue

        return jobs
