"""Calendar integration for the messes.info website."""

import typing as t
from datetime import datetime
from zoneinfo import ZoneInfo

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_CHURCH_NAME, CONF_CITY, CONF_POSTAL_CODE
from .logger import logger
from .scraper import MessesInfoScraper


class MessesInfoCalendar(CalendarEntity):
    """Representation of a calendar entity for messes info."""

    _church_city: str
    _postal_code: str
    _church_name: str
    _events: t.List[CalendarEvent]
    _unique_id: str
    _name: str

    def __init__(
        self, city: str, postal_code: str, church_name: str, unique_id: str
    ) -> None:
        """Initialize the calendar entity.

        Args:
            postal_code (str): Postal code of the church.
            church_name (str): Name of the church.
            unique_id (str): Unique identifier for the calendar.
        """
        self._church_city = city
        self._postal_code = postal_code
        self._church_name = church_name
        self._events = []
        self._unique_id = unique_id
        self._name = f"Messes {church_name} [{postal_code}]"

    @property
    def name(self) -> str:
        """Return the name of the calendar.

        Returns:
            str: Name of the calendar.
        """
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the calendar.

        Returns:
            str: Unique ID of the calendar.
        """
        return self._unique_id

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event.

        Returns:
            CalendarEvent | None: Next event or None if no events are available.
        """
        now: datetime = dt_util.now(time_zone=ZoneInfo("Europe/Paris"))
        for event in sorted(self._events, key=lambda x: x.start):
            if event.start > now:
                return event
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> t.List[CalendarEvent]:
        """Return all events between start and end date.

        Args:
            hass (HomeAssistant): Home Assistant instance.
            start_date (datetime): Events start date.
            end_date (datetime): Events end date.

        Returns:
            t.List[CalendarEvent]: List of events within the date range.
        """
        events: t.List[CalendarEvent] = [
            event for event in self._events if start_date <= event.start <= end_date
        ]
        logger.info(
            "Fetching %s events between %s and %s", len(events), start_date, end_date
        )
        return events

    async def async_update(self) -> None:
        """Refresh events."""
        masses: t.Dict[str, t.List[t.Dict[str, t.Any]]] = {}
        masses = await MessesInfoScraper(
            church={
                "name": self._church_name,
                "city": self._church_city,
                "short_postal_code": self._postal_code[:2],
                "full_postal_code": self._postal_code,
            }
        ).scrape(days_count=7)
        logger.debug("Fetched %s masses days", len(masses.keys()))
        for masses_list in masses.values():
            for mass in masses_list:
                logger.debug(
                    "Creating event for mass: %s (%s)", mass["type"], mass["start_date"]
                )
                self._events.append(
                    CalendarEvent(
                        start=mass["start_date"],
                        end=mass["end_date"],
                        summary=f"{mass['type']}",
                        location=f"{mass['community']['address']}, {mass['community']['postal_code']} {mass['community']['city']}",  # pylint:disable=line-too-long
                        uid=f"{mass['community']['name']}_{mass['start_date'].isoformat()}",
                    )
                )

    async def async_create_event(self, **kwargs: t.Any) -> None:
        """Create a new event.

        Args:
            kwargs (t.Any): Event details.
        """
        raise NotImplementedError("Event creation is not supported.")

    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Delete an event.

        Args:
            uid (str): Unique identifier of the event.
            recurrence_id (str | None, optional): Recurrence ID. Defaults to None.
            recurrence_range (str | None, optional): Recurrence range. Defaults to None.
        """
        raise NotImplementedError("Event suppression is not supported.")


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the calendar entity for the messes.info integration.

    Args:
        hass (HomeAssistant): Home Assistant instance.
        entry (ConfigEntry): Configuration entry.
        async_add_entities (AddEntitiesCallback): Callback to add entities.
    """
    city: str = entry.data[CONF_CITY]
    postal_code: str = entry.data[CONF_POSTAL_CODE]
    church_name: str = entry.data[CONF_CHURCH_NAME]
    sanitized_church_name: str = church_name.lower().replace(" ", "_")
    calendar = MessesInfoCalendar(
        city=city,
        postal_code=postal_code,
        church_name=church_name,
        unique_id=f"messe_info_{city}_{postal_code}_{sanitized_church_name}",
    )
    await calendar.async_update()
    async_add_entities([calendar])
