from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.number import NumberEntity
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
	async_add_entities([BoostFlowNumber(coordinator), BoostTimeNumber(coordinator)])


class BoostFlowNumber(CoordinatorEntity, NumberEntity):

	device: OxygenHrvDevice

	def __init__(self, coordinator: OxygenHrvCoordinator) -> None:
		"""Init Oxygen HRV entity."""
		super(CoordinatorEntity, self).__init__(coordinator)
		self.device = coordinator.data

		self._attr_unique_id = format_mac(self.device.mac_address) + "-boostflow"
		self._attr_has_entity_name = True
		self.entity_id = "number." + DOMAIN + "_boost_flow"
		self._attr_name = "Oxygen HRV Boost Flow"
		self._attr_device_info = coordinator.device_info
		self._attr_native_min_value = 1
		self._attr_native_max_value = 100
		self._attr_native_unit_of_measurement = "%"
		self.set_device_values()

	async def async_set_native_value(self, value: float) -> None:
		await self.device.set_boost_flow(value)


	@callback
	def _handle_coordinator_update(self) -> None:
		"""Handle updated data from the coordinator."""
		self.device = self.coordinator.data
		self.set_device_values()
		self.async_write_ha_state()

	def set_device_values(self) -> None:
		"""Set entity state from device."""
		self._attr_native_value = self.device.ga_data.boost_flow()



class BoostTimeNumber(CoordinatorEntity, NumberEntity):

	device: OxygenHrvDevice

	def __init__(self, coordinator: OxygenHrvCoordinator) -> None:
		"""Init Oxygen HRV entity."""
		super(CoordinatorEntity, self).__init__(coordinator)
		self.device = coordinator.data

		self._attr_unique_id = format_mac(self.device.mac_address) + "-boosttime"
		self._attr_has_entity_name = True
		self.entity_id = "number.oxygen_hrv_boost_time_minutes"
		self._attr_name = "Oxygen HRV Boost Time in minutes"
		self._attr_device_info = coordinator.device_info
		self._attr_native_min_value = 1
		self._attr_native_max_value = 30
		self._attr_native_step = 1
		self._attr_native_unit_of_measurement = "min"
		self.set_device_values()

	async def async_set_native_value(self, value: float) -> None:
		await self.device.set_boost_time(int(value))


	@callback
	def _handle_coordinator_update(self) -> None:
		"""Handle updated data from the coordinator."""
		self.device = self.coordinator.data
		self.set_device_values()
		self.async_write_ha_state()

	def set_device_values(self) -> None:
		"""Set entity state from device."""
		self._attr_native_value = float(self.device.ga_data.boost_time())
