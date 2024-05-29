"""Generic entity for EcoDevices."""

from pyecodevices import EcoDevices

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo

from .const import DOMAIN


def get_device_info(controller: EcoDevices) -> DeviceInfo:
    """Get device info."""
    return DeviceInfo(
        identifiers={(DOMAIN, controller.mac_address)},
        manufacturer="GCE Electronics",
        model="Eco-Devices",
        name=f"Eco-Devices {controller.host}:{controller.port!s}",
        sw_version=controller.version,
        connections={(CONNECTION_NETWORK_MAC, controller.mac_address)},
        configuration_url=f"http://{controller.host}:{controller.port}",
    )
