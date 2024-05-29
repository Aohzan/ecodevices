"""GCE Eco-Devices integration."""

import asyncio
from datetime import timedelta
import logging

from pyecodevices import (
    EcoDevices,
    EcoDevicesCannotConnectError,
    EcoDevicesInvalidAuthError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_BASE,
    CONF_TI_TYPE_HCHP,
    CONTROLLER,
    COORDINATOR,
    DOMAIN,
    PLATFORMS,
    UNDO_UPDATE_LISTENER,
)

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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

        entry.version = 2

        hass.config_entries.async_update_entry(
            entry, data=entry.data, options=new_options
        )
        _LOGGER.debug("Migration to version %s successful", entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eco-Devices from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    config = entry.data
    options = entry.options

    scan_interval = options.get(CONF_SCAN_INTERVAL, config.get(CONF_SCAN_INTERVAL))
    username = options.get(CONF_USERNAME, config.get(CONF_USERNAME))
    password = options.get(CONF_PASSWORD, config.get(CONF_PASSWORD))

    session = async_get_clientsession(hass, False)

    controller = EcoDevices(
        config[CONF_HOST],
        config[CONF_PORT],
        username,
        password,
        session=session,
    )

    try:
        await controller.get_info()
    except EcoDevicesCannotConnectError as exception:
        raise ConfigEntryNotReady from exception

    async def async_update_data():
        """Fetch data from API."""
        try:
            return await controller.global_get()
        except EcoDevicesInvalidAuthError as err:
            raise UpdateFailed("Authentication error on Eco-Devices") from err
        except EcoDevicesCannotConnectError as err:
            raise UpdateFailed(f"Failed to communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        CONTROLLER: controller,
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *(
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            )
        )
    )

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
