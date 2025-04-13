"""Calendar integration for the messes.info website."""

import logging
import typing as t
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_CHURCH_NAME, CONF_POSTAL_CODE
from .scraper import scrape_masses

_LOGGER = logging.getLogger(__name__)


class MessesInfoCalendar(CalendarEntity):
    """Representation of a calendar entity for messes info."""

    _postal_code: str
    _church_name: str
    _events: t.List[CalendarEvent]
    _unique_id: str
    _name: str

    def __init__(self, postal_code: str, church_name: str, unique_id: str) -> None:
        """Initialize the calendar entity.

        Args:
            postal_code (str): Postal code of the church.
            church_name (str): Name of the church.
            unique_id (str): Unique identifier for the calendar.
        """
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
        now: datetime = dt_util.now()
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
        _LOGGER.info(
            "Fetching %s events between %s and %s", len(events), start_date, end_date
        )
        return events

    async def async_update(self) -> None:
        """Refresh events."""
        masses: t.Dict[str, t.Any] = await scrape_masses(
            postal_code=self._postal_code,
            church_name=self._church_name,
        )
        _LOGGER.debug("Fetched %s masses", len(masses))
        for mass in masses.values():
            dt = dt_util.parse_datetime(mass["start_date"])
            if dt is None:
                continue
            _LOGGER.debug(
                "Creating event for mass: %s (%s)", mass["title"], mass["subtitle"]
            )
            self._events.append(
                CalendarEvent(
                    start=dt_util.as_local(dt),
                    end=dt_util.as_local(
                        dt + timedelta(hours=1)  # assuming 1 hour mass
                    ),
                    summary=f"{mass['title']} ({mass['subtitle']})",
                    location=f"{mass['street_address']}, {mass['postal_code']}, {mass['address_locality']}",  # pylint: disable=line-too-long
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
    postal_code: str = entry.data[CONF_POSTAL_CODE]
    church_name: str = entry.data[CONF_CHURCH_NAME]
    sanitized_church_name: str = church_name.lower().replace(" ", "_")
    calendar = MessesInfoCalendar(
        postal_code=postal_code,
        church_name=church_name,
        unique_id=f"messe_info_{postal_code}_{sanitized_church_name}",
    )
    await calendar.async_update()
    async_add_entities([calendar])
