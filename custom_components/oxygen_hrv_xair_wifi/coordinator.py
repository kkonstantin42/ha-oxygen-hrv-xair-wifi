"""Oxygen HRV coordinator."""

from asyncio import timeout
from datetime import timedelta
import logging

from homeassistant.components.climate import HVACMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .oxygen_client import CannotConnect, OxygenHrvDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MAX_TRANSIENT_FAILURES = 3


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
            update_interval=timedelta(seconds=15),
        )

        self.device = device
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.mac_address)},
            name="Oxygen HRV X-Air",
            manufacturer="UAB Oxygen Group",
        )

        self._fail_count = 0

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """OFF powers the device down; AUTO powers it on."""
        if hvac_mode == HVACMode.OFF:
            await self.device.turn_off()
        else:
            await self.device.turn_on()
        await self.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Power the device on."""
        await self.device.turn_on()
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Power the device off; the controller stays reachable while off."""
        await self.device.turn_off()
        await self.async_request_refresh()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        Tolerate a few consecutive transient errors (keeping the last known
        state) before marking the device unavailable.
        """
        try:
            _LOGGER.debug("Updating oxygen state")
            async with timeout(10):
                await self.device.fetch_state()
            self._fail_count = 0
            return self.device
        except CannotConnect as err:
            self._fail_count += 1
            if self.data is not None and self._fail_count <= MAX_TRANSIENT_FAILURES:
                _LOGGER.warning(
                    "Oxygen HRV transient error %s/%s: %s",
                    self._fail_count,
                    MAX_TRANSIENT_FAILURES,
                    err,
                )
                return self.data
            raise UpdateFailed(
                f"Error communicating with Oxygen HRV API: {err}"
            ) from err
