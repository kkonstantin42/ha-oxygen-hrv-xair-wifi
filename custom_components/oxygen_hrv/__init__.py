"""The oxygen_hrv integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .oxygen_client import OxygenHrvDevice
from .coordinator import OxygenHrvCoordinator

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.FAN]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up oxygen_hrv from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    device = OxygenHrvDevice(entry.data[CONF_HOST])
    coordinator = OxygenHrvCoordinator(hass, device)

    await coordinator.async_config_entry_first_refresh()

    await device.fetch_state()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
