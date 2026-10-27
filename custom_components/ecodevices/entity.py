"""Generic entity for EcoDevices."""

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import EcoDevicesCoordinator


def entity_unique_id(mac_address: str, suffix: str) -> str:
    """Return the unique ID of an entity of the Eco-Devices."""
    return slugify(f"{DOMAIN}_{mac_address}_{suffix}")


class EcoDevicesEntity(CoordinatorEntity[EcoDevicesCoordinator]):
    """Base entity of an Eco-Devices input."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoDevicesCoordinator,
        unique_id_suffix: str,
        translation_key: str,
        input_number: int,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        controller = coordinator.controller
        self._input_number = input_number
        self._attr_unique_id = entity_unique_id(
            controller.mac_address, unique_id_suffix
        )
        self._attr_translation_key = translation_key
        self._attr_translation_placeholders = {"input": str(input_number)}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, controller.mac_address)},
            manufacturer="GCE Electronics",
            model="Eco-Devices",
            name=f"Eco-Devices {controller.host}:{controller.port}",
            sw_version=controller.version,
            connections={(CONNECTION_NETWORK_MAC, controller.mac_address)},
            configuration_url=f"http://{controller.host}:{controller.port}",
        )
