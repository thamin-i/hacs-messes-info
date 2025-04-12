"""Sensor for scraping messes.info using BeautifulSoup and aiohttp."""

import typing as t

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MessesInfoCoordinator


class MessesInfoSensor(Entity):
    """Representation of a sensor that scrapes data from messes.info."""

    _coordinator: MessesInfoCoordinator
    _attr_name: str
    _attr_unique_id: str

    def __init__(self, coordinator: MessesInfoCoordinator, entry_id: str) -> None:
        """Initialize the sensor.

        Args:
            coordinator (MessesInfoCoordinator): Data update coordinator.
            entry_id (str): Configuration entry ID.
        """
        self._coordinator = coordinator
        church_name: str = coordinator.church_name
        postal_code: str = coordinator.postal_code
        self._attr_name = f"Masses for {church_name} ({postal_code})"
        self._attr_unique_id = entry_id

    @property
    def state(self) -> t.Optional[int]:
        """Get the state of the sensor.

        Returns:
            t.Optional[int]: Number of masses or None if no data is available.
        """
        return len(self._coordinator.data) if self._coordinator.data else None

    @property
    def extra_state_attributes(self) -> t.Dict[str, t.Dict[str, t.Any]]:
        """Get extra state attributes for the sensor.

        Returns:
            t.Dict[str, t.Dict[str, t.Any]]: Dict of masses with their details.
        """
        return {"masses": self._coordinator.data}

    async def async_update(self) -> None:
        """Request an update from the coordinator."""
        await self._coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform for the Messes Info integration.

    Args:
        hass (HomeAssistant): Home Assistant instance.
        entry (ConfigEntry): Configuration entry.
        async_add_entities (AddEntitiesCallback): Callback to add entities.
    """
    coordinator: MessesInfoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MessesInfoSensor(coordinator, entry.entry_id)])
