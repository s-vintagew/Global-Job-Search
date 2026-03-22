from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import logging
import random

logger = logging.getLogger(__name__)


# ─── Country-name normalization map ──────────────────────────
COUNTRY_ALIASES = {
    "us": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "great britain": "United Kingdom",
    "ca": "Canada",
    "au": "Australia",
    "de": "Germany",
    "deutschland": "Germany",
    "fr": "France",
    "in": "India",
    "sg": "Singapore",
    "jp": "Japan",
    "br": "Brazil",
    "nl": "Netherlands",
    "es": "Spain",
    "it": "Italy",
    "se": "Sweden",
    "no": "Norway",
    "dk": "Denmark",
    "fi": "Finland",
    "ie": "Ireland",
    "nz": "New Zealand",
    "ch": "Switzerland",
    "at": "Austria",
    "be": "Belgium",
    "pt": "Portugal",
    "pl": "Poland",
    "cz": "Czech Republic",
    "kr": "South Korea",
    "mx": "Mexico",
    "ar": "Argentina",
    "co": "Colombia",
    "il": "Israel",
    "ae": "United Arab Emirates",
    "za": "South Africa",
}


def normalize_country(name: str) -> str:
    """Normalise country codes/abbreviations to full names."""
    if not name:
        return "Worldwide"
    key = name.lower().strip()
    return COUNTRY_ALIASES.get(key, name.strip())


class LocationProcessor:
    """Convert string locations into lat/lng coordinates for the globe."""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="global_jobs_search_v2")
        self.location_cache: dict[str, dict] = {}

        self.fallbacks = {
            "worldwide": {"lat": 20.0, "lng": 0.0, "country": "Worldwide"},
            "remote":    {"lat": 20.0, "lng": 0.0, "country": "Worldwide"},
            "anywhere":  {"lat": 20.0, "lng": 0.0, "country": "Worldwide"},
            "global":    {"lat": 20.0, "lng": 0.0, "country": "Worldwide"},
            "us":        {"lat": 39.83, "lng": -98.58, "country": "United States"},
            "united states": {"lat": 39.83, "lng": -98.58, "country": "United States"},
            "usa":       {"lat": 39.83, "lng": -98.58, "country": "United States"},
            "eu":        {"lat": 51.0, "lng": 10.0, "country": "Europe"},
            "europe":    {"lat": 51.0, "lng": 10.0, "country": "Europe"},
        }

    def process_location(self, raw_location_str: str) -> dict:
        if not raw_location_str:
            return self._get_fallback("worldwide")

        loc_lower = raw_location_str.lower().strip()

        # Check explicit fallbacks
        for key, value in self.fallbacks.items():
            if key in loc_lower:
                return self._get_fallback(key)

        # Cache lookup
        if loc_lower in self.location_cache:
            return self.location_cache[loc_lower]

        # Geocode via Nominatim
        try:
            logger.info(f"Geocoding: {raw_location_str}")
            time.sleep(1.1)  # Be polite to the free API
            location = self.geolocator.geocode(raw_location_str, timeout=10)

            if location:
                address_parts = location.address.split(",")
                raw_country = address_parts[-1].strip() if address_parts else "Unknown"
                country = normalize_country(raw_country)

                result = {
                    "city": address_parts[0].strip() if len(address_parts) > 1 else raw_location_str,
                    "country": country,
                    "lat": location.latitude,
                    "lng": location.longitude,
                }
                self.location_cache[loc_lower] = result
                return result

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding failed for {raw_location_str}: {e}")

        return self._get_fallback("worldwide", randomize=True)

    def _get_fallback(self, key: str, randomize: bool = False) -> dict:
        data = self.fallbacks.get(key, self.fallbacks["worldwide"])
        lat = float(data["lat"])
        lng = float(data["lng"])

        if randomize:
            lat += random.uniform(-5.0, 5.0)
            lng += random.uniform(-10.0, 10.0)

        return {
            "city": "Remote",
            "country": data["country"],
            "lat": lat,
            "lng": lng,
        }
