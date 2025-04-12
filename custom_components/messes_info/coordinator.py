"""Coordinator for fetching and updating mass information from Messes Info."""

import logging
import typing as t
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .scraper import scrape_masses


class MessesInfoCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching and updating mass information."""

    postal_code: str
    church_name: str
    hourly_update_interval: int

    def __init__(self, hass: HomeAssistant, config: t.Mapping[str, t.Any]) -> None:
        """Initialize the coordinator.

        Args:
            hass (HomeAssistant): Home Assistant instance.
            config (t.Mapping[str, t.Any]):
                Configuration data containing postal code and church name.
        """
        self.postal_code = config["postal_code"]
        self.church_name = config["church_name"]
        self.hourly_update_interval = config["update_interval"]

        super().__init__(
            hass=hass,
            logger=logging.getLogger("messes_info"),
            name=f"Masses for {self.church_name} ({self.postal_code})",
            update_interval=timedelta(hours=self.hourly_update_interval),
        )

    async def _async_update_data(self) -> t.Dict[str, t.Any]:
        """Update data from the Messes Info website.spmak

        Raises:
            UpdateFailed: If there is an error fetching mass data.

        Returns:
            t.Dict[str, t.Any]: Dict of mass details.
        """
        try:
            return await scrape_masses(self.postal_code, self.church_name)
        except Exception as exception:
            raise UpdateFailed(f"Error fetching mass data: {exception}") from exception
