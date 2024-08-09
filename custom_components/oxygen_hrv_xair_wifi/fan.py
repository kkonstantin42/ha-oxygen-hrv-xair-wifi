from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OxygenHrvEntity
from .oxygen_client import OxygenHrvDevice

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OxygenHrvCoordinator
from .oxygen_client import OxygenHrvDevice

FAN_MODE_VALUES = list(range(45, 105, 5))


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OxygenHrvCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OxygenHrvFanEntity(coordinator)])


class OxygenHrvFanEntity(CoordinatorEntity, FanEntity):
    """Climate entity representing Oxygen Heat Exchange."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    device: OxygenHrvDevice

    def __init__(self, coordinator: OxygenHrvCoordinator) -> None:
        """Init Oxygen HRV entity."""
        super(CoordinatorEntity, self).__init__(coordinator)
        self.device = coordinator.data

        self._attr_unique_id = format_mac(self.device.mac_address) + "-fan"
        self._attr_has_entity_name = True
        self.entity_id = "fan." + DOMAIN
        self._attr_name = "Oxygen HRV Fan"
        self._attr_device_info = coordinator.device_info

        self.set_device_values()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.device = self.coordinator.data
        self.set_device_values()
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        await self.device.set_target_flow(percentage)
        await self.coordinator.async_request_refresh()

    def set_device_values(self) -> None:
        """Set entity state from device."""
        self._attr_percentage = self.device.ga_data.flow()