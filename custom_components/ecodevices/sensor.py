"""Support for the GCE Eco-Devices."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_ENABLED,
    CONF_C1_ICON,
    CONF_C1_NAME,
    CONF_C1_UNIT_OF_MEASUREMENT,
    CONF_C2_DEVICE_CLASS,
    CONF_C2_ENABLED,
    CONF_C2_ICON,
    CONF_C2_NAME,
    CONF_C2_UNIT_OF_MEASUREMENT,
    CONF_T1_ENABLED,
    CONF_T1_NAME,
    CONF_T1_UNIT_OF_MEASUREMENT,
    CONF_T2_ENABLED,
    CONF_T2_NAME,
    CONF_T2_UNIT_OF_MEASUREMENT,
    CONFIG,
    CONTROLLER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default="Eco-Devices"): str,
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Required(CONF_T1_ENABLED, default=False): bool,
        vol.Optional(CONF_T1_NAME): str,
        vol.Optional(CONF_T1_UNIT_OF_MEASUREMENT): str,
        vol.Required(CONF_T2_ENABLED, default=False): bool,
        vol.Optional(CONF_T2_NAME): str,
        vol.Optional(CONF_T2_UNIT_OF_MEASUREMENT): str,
        vol.Required(CONF_C1_ENABLED, default=False): bool,
        vol.Optional(CONF_C1_NAME): str,
        vol.Optional(CONF_C1_ICON): str,
        vol.Optional(CONF_C1_UNIT_OF_MEASUREMENT): str,
        vol.Optional(CONF_C1_DEVICE_CLASS): str,
        vol.Required(CONF_C2_ENABLED, default=False): bool,
        vol.Optional(CONF_C2_NAME): str,
        vol.Optional(CONF_C2_ICON): str,
        vol.Optional(CONF_C2_UNIT_OF_MEASUREMENT): str,
        vol.Optional(CONF_C2_DEVICE_CLASS): str,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import the platform into a config entry."""

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the GCE Eco-Devices platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    controller = data[CONTROLLER]
    controller_name = data[CONF_NAME]
    config = data[CONFIG]

    entities = []

    if config.get(CONF_T1_ENABLED):
        _LOGGER.info("Add the t1 entity.")
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "current_t1",
                config.get(CONF_T1_NAME, "Teleinfo 1"),
                config.get(CONF_T1_UNIT_OF_MEASUREMENT, "VA"),
                "mdi:flash",
                "power",
            )
        )
    if config.get(CONF_T2_ENABLED):
        _LOGGER.info("Add the t2 entity.")
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "current_t2",
                config.get(CONF_T2_NAME, "Teleinfo 2"),
                config.get(CONF_T2_UNIT_OF_MEASUREMENT, "VA"),
                "mdi:flash",
                "power",
            )
        )
    if config.get(CONF_C1_ENABLED):
        _LOGGER.info("Add the c1 entities.")
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "daily_c1",
                f"{config.get(CONF_C1_NAME, 'Meter 1')} Daily",
                config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                config.get(CONF_C1_ICON),
                config.get(CONF_C1_DEVICE_CLASS),
            )
        )
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "total_c1",
                f"{config.get(CONF_C1_NAME, 'Meter 1')} Total",
                config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                config.get(CONF_C1_ICON),
                config.get(CONF_C1_DEVICE_CLASS),
            )
        )
    if config.get(CONF_C2_ENABLED):
        _LOGGER.info("Add the c2 entities.")
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "daily_c2",
                f"{config.get(CONF_C2_NAME, 'Meter 2')} Daily",
                config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                config.get(CONF_C2_ICON),
                config.get(CONF_C2_DEVICE_CLASS),
            )
        )
        entities.append(
            EdDevice(
                controller,
                controller_name,
                "total_c2",
                f"{config.get(CONF_C2_NAME, 'Meter 2')} Total",
                config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                config.get(CONF_C2_ICON),
                config.get(CONF_C2_DEVICE_CLASS),
            )
        )

    if entities:
        async_add_entities(entities, True)


class EdDevice(Entity):
    """Representation of a Sensor."""

    def __init__(
        self, controller, controller_name, request, name, unit, icon, device_class
    ):
        """Initialize the sensor."""
        self._controller = controller
        self._controller_name = controller_name
        self._request = request
        self._name = name
        self._unit = unit
        self._icon = icon
        self._device_class = device_class

        self._state = None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._controller.host)},
            "name": self._controller_name,
            "manufacturer": "GCE",
            "model": "Eco-Devices",
            "via_device": (DOMAIN, self._controller.host),
        }

    @property
    def unique_id(self):
        return f"ecodevices_{self._controller.host}_{str(self._request)}"

    @property
    def device_class(self):
        return self._device_class

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        return self._icon

    def update(self):
        self._state = self._controller.get(self._request)
