from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OxygenHrvCoordinator
from .oxygen_client import OxygenHrvDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OxygenHrvCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OxygenHrvFanEntity(coordinator)])


class OxygenHrvFanEntity(CoordinatorEntity, FanEntity):
    """Fan entity representing Oxygen Heat Exchange."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
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

    @property
    def is_on(self) -> bool:
        """Power state reported by the device."""
        return self.device.ga_data.power_on()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.device = self.coordinator.data
        self.set_device_values()
        self.async_write_ha_state()

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None:
        """Power the device on."""
        await self.coordinator.async_turn_on()
        if percentage is not None:
            await self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Power the device off."""
        await self.coordinator.async_turn_off()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        await self.device.set_target_flow(percentage)
        await self.coordinator.async_request_refresh()

    def set_device_values(self) -> None:
        """Set entity state from device; show the flow setpoint even when off."""
        self._attr_percentage = self.device.ga_data.flow()
