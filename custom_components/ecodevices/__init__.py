"""GCE Eco-Devices integration"""
import asyncio
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import CONFIG, CONTROLLER, DOMAIN, PLATFORMS, UNDO_UPDATE_LISTENER
from .ecodevicesapi import EcoDevices

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Eco-Devices integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Eco-Devices from a config entry."""
    config = entry.data

    controller = EcoDevices(
        config.get(CONF_HOST),
        config.get(CONF_PORT),
        config.get(CONF_USERNAME),
        config.get(CONF_PASSWORD),
    )

    if not controller.ping():
        _LOGGER.error("GCE Eco-Devices didn't answer to the request, unable to set up")
        raise ConfigEntryNotReady

    _LOGGER.info(
        "Successfully connected to the Eco-Device gateway: %s.",
        config.get(CONF_HOST, CONF_PORT),
    )

    if config.get(CONF_USERNAME) and config.get(CONF_PASSWORD):
        _LOGGER.info(
            "Authenticated as %s.",
            config.get(CONF_USERNAME),
        )

    undo_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_NAME: config.get(CONF_NAME),
        CONTROLLER: controller,
        CONFIG: config,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, controller.host)},
        manufacturer="GCE",
        model="Eco-Devices",
        name=config.get(CONF_NAME),
    )

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
