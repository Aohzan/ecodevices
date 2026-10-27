"""Data update coordinator of the GCE Eco-Devices integration."""

from collections.abc import Awaitable, Callable
from datetime import timedelta
import logging
from typing import Any

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
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

type EcoDevicesConfigEntry = ConfigEntry[EcoDevicesCoordinator]


def get_entry_config(entry: ConfigEntry) -> dict[str, Any]:
    """Return the entry data overridden by the options."""
    return {**entry.data, **entry.options}


class EcoDevicesCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the values of an Eco-Devices."""

    config_entry: EcoDevicesConfigEntry

    def __init__(self, hass: HomeAssistant, entry: EcoDevicesConfigEntry) -> None:
        """Initialize the coordinator."""
        config = get_entry_config(entry)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=config[CONF_SCAN_INTERVAL]),
        )
        self.controller = EcoDevices(
            config[CONF_HOST],
            config[CONF_PORT],
            config.get(CONF_USERNAME),  # ty: ignore[invalid-argument-type] pyecodevices annotates it str, None means no authentication
            config.get(CONF_PASSWORD),  # ty: ignore[invalid-argument-type] pyecodevices annotates it str, None means no authentication
            session=async_get_clientsession(hass, verify_ssl=False),
        )

    async def _async_setup(self) -> None:
        """Read the firmware version and MAC address of the Eco-Devices."""
        await self._async_call(self.controller.get_info)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the values of all inputs."""
        return await self._async_call(self.controller.global_get)

    async def _async_call[T](self, method: Callable[[], Awaitable[T]]) -> T:
        """Call the Eco-Devices API, raising the Home Assistant exceptions."""
        try:
            return await method()
        except EcoDevicesInvalidAuthError as err:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN, translation_key="invalid_auth"
            ) from err
        except EcoDevicesCannotConnectError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="cannot_connect",
                translation_placeholders={"error": str(err)},
            ) from err
