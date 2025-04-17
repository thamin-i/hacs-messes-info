"""Constants for the Messes Info integration."""

import typing as t

BASE_URL: str = "https://messes.info"
CONF_DAYS_AHEAD: str = "days_ahead"
CONF_CHURCH_NAME: str = "church_name"
CONF_CHURCH_CITY: str = "city"
CONF_CHURCH_POSTAL_CODE: str = "postal_code"
DOMAIN: str = "messes_info"
PLATFORMS: t.List[str] = ["calendar"]
