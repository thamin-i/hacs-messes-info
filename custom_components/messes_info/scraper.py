"""Scraper for the Messes Info website."""

import json
import logging
import typing as t
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp
import async_timeout

from .const import API_KEY, BASE_URL

_LOGGER = logging.getLogger(__name__)


class MessesInfoScraper:
    """Scraper for the Messes Info website."""

    url: str = f"{BASE_URL}/gwtRequest"
    headers: t.Dict[str, str] = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    request_timeout: int = 10
    church: t.Dict[str, str]

    def __init__(self, church: t.Dict[str, str]) -> None:
        """Initialize the scraper.

        Args:
            church (t.Dict[str, str]): Targeted church information.
        """
        self.church = church
        _LOGGER.debug(
            "MessesInfoScraper initialized with church: %s",
            json.dumps(church),
        )

    async def request_masses(self, day: str) -> t.Dict[str, t.Any]:
        """Request masses list for a specific day.

        Args:
            day (str): Date in the format "dd-mm-yyyy".

        Returns:
            t.Dict[str, t.Any]: JSON response from the server.
        """
        _LOGGER.debug("Requesting masses for date: %s", day)
        json_data: t.Dict[str, t.Any] = {
            "F": "cef.kephas.shared.request.AppRequestFactory",
            "I": [
                {
                    "O": API_KEY,
                    "P": [
                        f"eglise {self.church['name']} ville {self.church['city']} .fr {self.church['short_postal_code']} {self.church['full_postal_code']} {day} all-celebration",  # pylint:disable=line-too-long
                        0,  # page number [int | None]
                        100,  # page size [int | None]
                        None,  # start localities [int | None]
                        None,  # limit localities [int | None]
                        None,  # ??? [str | None]
                        None,  # query more [str | None]
                    ],
                    "R": [
                        "listCelebrationTime.locality",
                    ],
                },
            ],
        }

        async with async_timeout.timeout(self.request_timeout):
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url=self.url, json=json_data) as response:
                    json_response: t.Dict[str, t.Any] = await response.json()
                    return json_response

    def parse_community(self, event_p: t.Dict[str, t.Any]) -> t.Dict[str, str]:
        """Parse community information from the returned event.

        Args:
            event_p (t.Dict[str, t.Any]): Event data.

        Returns:
            t.Dict[str, str]: Parsed community information.
        """
        return {
            "name": event_p["name"],
            "address": event_p["address"],
            "postal_code": event_p["zipcode"],
            "city": event_p["city"],
            "latitude": event_p["latitude"],
            "longitude": event_p["longitude"],
        }

    def parse_mass(self, event_p: t.Dict[str, t.Any]) -> t.Dict[str, str | datetime]:
        """Parse mass information from the returned event.

        Args:
            event_p (t.Dict[str, t.Any]): Event data.

        Returns:
            t.Dict[str, str | datetime]: Parsed mass information.
        """
        start_date: datetime = datetime.strptime(
            f"{event_p['date']} {event_p['time']}", "%Y-%m-%d %Hh%M"
        ).replace(tzinfo=ZoneInfo("Europe/Paris"))
        hours, minutes = map(int, event_p["length"].lower().replace("h", " ").split())
        end_date = start_date + timedelta(hours=hours, minutes=minutes)
        return {
            "start_date": start_date,
            "end_date": end_date,
            "type": event_p.get("type", "Messe"),
        }

    def parse_masses(self, response: t.Dict[str, t.Any]) -> t.List[t.Dict[str, t.Any]]:
        """Parse masses information from the JSON response.

        Args:
            response (t.Dict[str, t.Any]): JSON response data.

        Returns:
            t.List[t.Dict[str, t.Any]]: Parsed masses information.
        """
        for status in response["S"]:
            if status is not True:
                raise ValueError("Invalid response status")

        masses: t.List[t.Dict[str, t.Any]] = []
        community: t.Dict[str, str] | None = None
        for event in response["O"]:
            if "community" in event["P"]:
                community = self.parse_community(event["P"])
            elif "celebrationInfoId" in event["P"]:
                masses.append(self.parse_mass(event["P"]))

        for mass in masses:
            mass["community"] = community
        return masses

    async def scrape(
        self, days_count: int, scraped_days: t.List[str]
    ) -> t.Dict[str, t.List[t.Dict[str, t.Any]]]:
        """Scrape masses information for a given number of days.

        Args:
            days_count (int): Number of days to scrape. Starting from today.
            scraped_days (t.List[str]): List of already scraped days.

        Returns:
            t.Dict[str, t.List[t.Dict[str, t.Any]]]: Scraped masses information.
        """
        days: t.List[str] = [
            (datetime.today() + timedelta(days=i)).strftime("%d-%m-%Y")
            for i in range(days_count)
        ]
        days = [day for day in days if day not in scraped_days]
        masses: t.Dict[str, t.List[t.Dict[str, t.Any]]] = {}
        for day in days:
            masses[day] = self.parse_masses(await self.request_masses(day))
        return masses
