"""Calendar integration for the messes.info website."""

import typing as t
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import MessesInfoCoordinator


class ChurchMassCalendar(CalendarEntity):
    """Representation of a calendar entity for church masses."""

    _name: str
    coordinator: MessesInfoCoordinator
    _events: t.List[CalendarEvent]
    _unique_id: str

    def __init__(
        self, name: str, coordinator: MessesInfoCoordinator, unique_id: str
    ) -> None:
        """Initialize the calendar entity.

        Args:
            name (str): Name of the calendar.
            coordinator (MessesInfoCoordinator): Data update coordinator.
        """
        self._name = name
        self.coordinator = coordinator
        self._events = []
        self._unique_id = unique_id

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
        return [
            event for event in self._events if start_date <= event.start <= end_date
        ]

    async def async_update(self) -> None:
        """Refresh event data from the coordinator."""
        await self.coordinator.async_request_refresh()

        self._events = []
        print(f"Iterating over {len(self.coordinator.data.get('masses', []))} masses")
        for mass in self.coordinator.data.get("masses", []):
            print(f"Processing mass: {mass}")
            dt = dt_util.parse_datetime(f"{mass['date']}T{mass['hour']}")
            if dt is None:
                continue
            self._events.append(
                CalendarEvent(
                    start=dt,
                    end=dt + timedelta(hours=1),  # assuming 1 hour mass
                    summary=mass["name"],
                    location=mass["location"],
                    description=f"Mass at {mass['location']}",
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
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the calendar entity for the messes.info integration.

    Args:
        hass (HomeAssistant): Home Assistant instance.
        entry (ConfigEntry): Configuration entry.
        async_add_entities (AddEntitiesCallback): Callback to add entities.
    """
    coordinator: MessesInfoCoordinator = hass.data[DOMAIN][entry.entry_id]
    unique_id: str = f"messe_info_{entry.data['postal_code']}_{entry.data['church_name'].lower().replace(' ', '_')}"  # pylint: disable=line-too-long
    async_add_entities([ChurchMassCalendar(entry.title, coordinator, unique_id)], True)
