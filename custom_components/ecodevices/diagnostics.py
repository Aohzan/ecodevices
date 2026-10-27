"""Diagnostics support for the GCE Eco-Devices integration."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .coordinator import EcoDevicesConfigEntry

TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    # Meter serial numbers
    "T1_ADCO",
    "T2_ADCO",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: EcoDevicesConfigEntry
) -> dict[str, Any]:
    """Return the diagnostics of a config entry."""
    coordinator = entry.runtime_data
    controller = coordinator.controller
    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "device": {"version": controller.version},
        "data": async_redact_data(coordinator.data, TO_REDACT),
    }
