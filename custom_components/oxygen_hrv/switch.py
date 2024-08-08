from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .coordinator import OxygenHrvCoordinator
from .entity import OxygenHrvEntity
from .oxygen_client import OxygenHrvDevice
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
		hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
	coordinator: OxygenHrvCoordinator = hass.data[DOMAIN][entry.entry_id]
	async_add_entities([BoostEnabledSwitch(coordinator)])


class BoostEnabledSwitch(CoordinatorEntity, SwitchEntity):

	device: OxygenHrvDevice

	def __init__(self, coordinator: OxygenHrvCoordinator) -> None:
		"""Init Oxygen HRV entity."""
		super(CoordinatorEntity, self).__init__(coordinator)
		self.device = coordinator.data

		self._attr_unique_id = format_mac(self.device.mac_address) + "-boostenabled"
		self._attr_has_entity_name = True
		self.entity_id = "switch.oxygen_hrv_boost_enabled"
		self._attr_name = "Oxygen HRV Boost Enabled"
		self._attr_device_info = DeviceInfo(
			connections={(self.device.mac_address, self.device.mac_address)},
			name="Oxygen LT HRV",
			manufacturer="UAB Oxygen",
		)
		self.set_device_values()

	async def async_turn_on(self) -> None:
		await self.device.start_boost()

	async def async_turn_off(self) -> None:
		await self.device.stop_boost()


	@callback
	def _handle_coordinator_update(self) -> None:
		"""Handle updated data from the coordinator."""
		self.device = self.coordinator.data
		self.set_device_values()
		self.async_write_ha_state()

	def set_device_values(self) -> None:
		"""Set entity state from device."""
		self._attr_is_on = self.device.ga_data.boost_enabled()
