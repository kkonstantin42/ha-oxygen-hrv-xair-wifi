"""Oxygen HRV coordinator."""

from asyncio import timeout
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .oxygen_client import CannotConnect, OxygenHrvDevice

_LOGGER = logging.getLogger(__name__)


class OxygenHrvCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, device: OxygenHrvDevice) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Oxygen HRV Coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),
        )
        self.device = device

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            _LOGGER.debug("Updating oxygen state")
            async with timeout(10):
                await self.device.fetch_state()
                return self.device
        except CannotConnect as err:
            raise UpdateFailed(
                f"Error communicating with Oxygen HRV API: {err}"
            ) from err
