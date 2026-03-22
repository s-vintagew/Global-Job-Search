import requests
import logging
from datetime import datetime
from app.scrapers.base import BaseScraper
from app.config import RAPIDAPI_KEY

logger = logging.getLogger(__name__)


class JSearchScraper(BaseScraper):
    """
    Scraper for JSearch via RapidAPI.
    Only runs when RAPIDAPI_KEY environment variable is set.
    Free tier: 500 requests/month.
    """

    def __init__(self):
        super().__init__(
            "https://jsearch.p.rapidapi.com/search", "jsearch"
        )
        self.api_key = RAPIDAPI_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def fetch_data(self) -> dict | None:
        if not self.is_available():
            logger.info("[jsearch] Skipped — no RAPIDAPI_KEY configured")
            return None

        try:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            }
            params = {
                "query": "software developer",
                "page": "1",
                "num_pages": "2",
                "date_posted": "week",
            }
            logger.info("[jsearch] Fetching from RapidAPI...")
            response = requests.get(
                self.target_url, headers=headers, params=params, timeout=20
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"[jsearch] Fetch failed: {e}")
            return None

    def parse_jobs(self, raw_data) -> list[dict]:
        if not raw_data or not isinstance(raw_data, dict):
            return []

        items = raw_data.get("data", [])
        if not items:
            return []

        jobs = []
        for item in items:
            try:
                title = item.get("job_title", "Unknown Role")
                company = item.get("employer_name", "Unknown Company")
                url = item.get("job_apply_link") or item.get(
                    "job_google_link", ""
                )
                if not url:
                    continue

                description = item.get("job_description", "")
                if len(description) > 500:
                    description = description[:500] + "..."

                city = item.get("job_city", "")
                country = item.get("job_country", "")
                lat = item.get("job_latitude") or 0.0
                lng = item.get("job_longitude") or 0.0

                is_remote = item.get("job_is_remote", False)
                job_type = "remote" if is_remote else "onsite"

                salary_min = item.get("job_min_salary")
                salary_max = item.get("job_max_salary")
                if salary_min and salary_max:
                    salary = f"${int(salary_min / 1000)}k - ${int(salary_max / 1000)}k"
                else:
                    salary = "Competitive"

                exp = item.get("job_required_experience", {})
                experience_level = None
                if isinstance(exp, dict):
                    exp_text = (
                        exp.get("required_experience_in_months") or ""
                    )
                    if isinstance(exp_text, (int, float)):
                        if exp_text < 24:
                            experience_level = "junior"
                        elif exp_text < 60:
                            experience_level = "mid"
                        else:
                            experience_level = "senior"

                skills = item.get("job_required_skills") or []
                tags_str = ", ".join(skills) if isinstance(skills, list) else ""

                date_str = item.get("job_posted_at_datetime_utc", "")
                try:
                    dt = datetime.fromisoformat(
                        date_str.replace("Z", "+00:00")
                    )
                    posted_date = dt.strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    posted_date = datetime.now().strftime("%Y-%m-%d")

                jobs.append({
                    "title": title,
                    "company": company,
                    "city": city or "Unknown",
                    "country": country,
                    "lat": float(lat),
                    "lng": float(lng),
                    "type": job_type,
                    "experience_level": experience_level,
                    "salary": salary,
                    "description": description,
                    "tags": tags_str,
                    "url": url,
                    "source": self.source_name,
                    "posted_date": posted_date,
                })
            except Exception as e:
                logger.warning(f"JSearch parse error: {e}")
                continue

        return jobs
