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
from .entity import OxygenHrvEntity
from .oxygen_client import OxygenHrvDevice

FAN_MODE_VALUES = list(range(45, 105, 5))


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OxygenHrvCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OxygenHrvClimateEntity(coordinator)])


class OxygenHrvClimateEntity(CoordinatorEntity, ClimateEntity):
    """Climate entity representing Oxygen Heat Exchange."""

    _attr_supported_features = (
        ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
    )

    def __init__(self, coordinator: OxygenHrvCoordinator) -> None:
        """Init Oxygen HRV entity."""
        super(CoordinatorEntity, self).__init__(coordinator)

        self.device = coordinator.data

        self._attr_fan_modes = [str(fan_flow) + "%" for fan_flow in FAN_MODE_VALUES]
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:fan"
        self._attr_target_temperature_low = 19.0
        self._attr_target_temperature_high = 30.0
        self._attr_target_temperature_step = 1.0
        self._attr_hvac_modes = [HVACMode.AUTO]
        self._attr_hvac_mode = HVACMode.AUTO

        self._attr_unique_id = format_mac(self.device.mac_address) + "-climate"
        self._attr_has_entity_name = True
        self.entity_id = "climate.oxygen_hrv"
        self._attr_name = "Oxygen HRV Climate"
        self._attr_device_info = DeviceInfo(
            connections={(self.device.mac_address, self.device.mac_address)},
            name="Oxygen LT HRV",
            manufacturer="UAB Oxygen",
        )
        self.set_device_values()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.device = self.coordinator.data
        self.set_device_values()
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.device.turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.device.turn_off()
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        print("Setting fan mode to " + fan_mode)
        await self.device.set_target_flow(fan_mode.rstrip("%"))
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs[ATTR_TEMPERATURE]
        print("Setting temperature to " + str(temperature))
        await self.device.set_target_temp(temperature)
        await self.coordinator.async_request_refresh()

    def set_device_values(self) -> None:
        """Set entity state from device."""
        self._attr_current_temperature = self.device.real_temp
        self._attr_target_temperature = self.device.target_temp
        self._attr_fan_mode = next(
            str(fan_flow) + "%"
            for fan_flow in FAN_MODE_VALUES
            if fan_flow >= self.device.target_flow
        )
