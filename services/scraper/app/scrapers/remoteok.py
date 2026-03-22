from app.scrapers.base import BaseScraper
from datetime import datetime
import re


class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK's public JSON API."""

    def __init__(self):
        super().__init__("https://remoteok.com/api", "remoteok")

    def parse_jobs(self, raw_data) -> list[dict]:
        if not raw_data or not isinstance(raw_data, list):
            return []

        jobs = []
        for item in raw_data:
            if "legal" in item:
                continue

            try:
                title = item.get("position", "Unknown Role")
                company = item.get("company", "Unknown Company")
                url = item.get("url", "")
                if not url:
                    continue

                description = item.get("description", "")
                if len(description) > 500:
                    description = description[:500] + "..."

                raw_location = item.get("location", "Worldwide")
                tags_list = item.get("tags", [])
                tags_str = ", ".join(tags_list) if isinstance(tags_list, list) else ""

                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")
                if salary_min and salary_max:
                    salary = f"${int(salary_min / 1000)}k - ${int(salary_max / 1000)}k"
                else:
                    salary = "Competitive"

                date_str = item.get("date")
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
                    "type": "remote",
                    "experience_level": None,
                    "salary": salary,
                    "description": re.sub(r"<[^>]+>", "", description),
                    "tags": tags_str,
                    "url": url,
                    "source": self.source_name,
                    "posted_date": posted_date,
                })
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f"RemoteOK parse error: {e}"
                )
                continue

        return jobs
