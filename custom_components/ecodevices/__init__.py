"""GCE Eco-Devices integration."""

import logging

from homeassistant.core import HomeAssistant

from .const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_BASE,
    CONF_TI_TYPE_HCHP,
    PLATFORMS,
)
from .coordinator import EcoDevicesConfigEntry, EcoDevicesCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(
    hass: HomeAssistant, entry: EcoDevicesConfigEntry
) -> bool:
    """Migrate old config entry."""

    if entry.version == 1:
        _LOGGER.debug("Entry version %s needs migration", entry.version)
        new_options = entry.options.copy()

        t1_enabled = new_options.get(
            CONF_T1_ENABLED, entry.data.get(CONF_T1_ENABLED, False)
        )
        t2_enabled = new_options.get(
            CONF_T2_ENABLED, entry.data.get(CONF_T2_ENABLED, False)
        )
        t1_hchp = new_options.get("t1_hchp", entry.data.get("t1_hchp", False))
        t2_hchp = new_options.get("t2_hchp", entry.data.get("t2_hchp", False))

        if t1_enabled:
            new_options[CONF_T1_TYPE] = (
                CONF_TI_TYPE_HCHP if t1_hchp else CONF_TI_TYPE_BASE
            )
            _LOGGER.debug("Set T1 type to %s", new_options[CONF_T1_TYPE])
        if t2_enabled:
            new_options[CONF_T2_TYPE] = (
                CONF_TI_TYPE_HCHP if t2_hchp else CONF_TI_TYPE_BASE
            )
            _LOGGER.debug("Set T2 type to %s", new_options[CONF_T2_TYPE])

        hass.config_entries.async_update_entry(entry, options=new_options, version=2)
        _LOGGER.debug("Migration to version %s successful", entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: EcoDevicesConfigEntry) -> bool:
    """Set up Eco-Devices from a config entry."""
    coordinator = EcoDevicesCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EcoDevicesConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
