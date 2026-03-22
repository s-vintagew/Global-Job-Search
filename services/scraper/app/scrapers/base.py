from abc import ABC, abstractmethod
import requests
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all job site scrapers."""

    def __init__(self, target_url: str, source_name: str):
        self.target_url = target_url
        self.source_name = source_name
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/html, */*;q=0.8",
        }

    def fetch_data(self) -> str | dict | list | None:
        """Fetch raw HTML/JSON from the target URL."""
        try:
            logger.info(f"[{self.source_name}] Fetching {self.target_url}...")
            response = requests.get(
                self.target_url, headers=self.headers, timeout=20
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            return response.text

        except requests.RequestException as e:
            logger.error(f"[{self.source_name}] Fetch failed: {e}")
            return None

    @abstractmethod
    def parse_jobs(self, raw_data) -> list[dict]:
        """
        Parse raw data into standardised job dicts with keys:
        title, company, city, country, lat, lng, type,
        experience_level, salary, description, tags, url,
        source, posted_date
        """
        pass

    def run(self) -> list[dict]:
        """Execute the full scrape pipeline for this source."""
        raw_data = self.fetch_data()
        if not raw_data:
            return []

        jobs = self.parse_jobs(raw_data)
        logger.info(f"[{self.source_name}] Scraped {len(jobs)} jobs")
        return jobs
