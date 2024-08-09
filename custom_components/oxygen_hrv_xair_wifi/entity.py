from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .oxygen_client import OxygenHrvDevice
from .coordinator import OxygenHrvCoordinator


class OxygenHrvEntity(CoordinatorEntity):
    """Generic Oxygen Hrv entity."""

    def __init__(self, coordinator: OxygenHrvCoordinator, idx: int):
        super(CoordinatorEntity, self).__init__(coordinator, context=idx)
