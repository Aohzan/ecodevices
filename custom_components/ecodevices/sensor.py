"""Support for the GCE Eco-Devices."""
import voluptuous as vol
import logging

from .ecodevicesapi import ECODEVICE as ecodevice

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD
)

_LOGGER = logging.getLogger(__name__)

CONF_T1_NAME = "t1_name"
CONF_T1_UNIT_OF_MEASUREMENT = "t1_unit_of_measurement"
CONF_T2_NAME = "t2_name"
CONF_T2_UNIT_OF_MEASUREMENT = "t2_unit_of_measurement"
CONF_C1_NAME = "c1_name"
CONF_C1_ICON = "c1_icon"
CONF_C1_UNIT_OF_MEASUREMENT = "c1_unit_of_measurement"
CONF_C1_DEVICE_CLASS = "c1_device_class"
CONF_C2_NAME = "c2_name"
CONF_C2_ICON = "c2_icon"
CONF_C2_UNIT_OF_MEASUREMENT = "c2_unit_of_measurement"
CONF_C2_DEVICE_CLASS = "c2_device_class"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_PORT, default=80): cv.port,
        vol.Optional(CONF_T1_NAME): cv.string,
        vol.Optional(CONF_T1_UNIT_OF_MEASUREMENT, default="VA"): cv.string,
        vol.Optional(CONF_T2_NAME): cv.string,
        vol.Optional(CONF_T2_UNIT_OF_MEASUREMENT, default="VA"): cv.string,
        vol.Optional(CONF_C1_NAME): cv.string,
        vol.Optional(CONF_C1_ICON): cv.string,
        vol.Optional(CONF_C1_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_C1_DEVICE_CLASS): cv.string,
        vol.Optional(CONF_C2_NAME): cv.string,
        vol.Optional(CONF_C2_ICON): cv.string,
        vol.Optional(CONF_C2_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_C2_DEVICE_CLASS): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the GCE Eco-Devices platform."""
    controller = ecodevice(config.get(CONF_HOST), config.get(CONF_PORT), config.get(CONF_USERNAME), config.get(CONF_PASSWORD))
    entities = []

    if controller.ping():
        _LOGGER.info(
            "Successfully connected to the Eco-Device gateway: %s.",
            config.get(CONF_HOST, CONF_PORT),
        )

        if config.get(CONF_USERNAME) and config.get(CONF_PASSWORD):
            _LOGGER.info(
                "Authenticated as %s.",
                config.get(CONF_USERNAME),
            )

        if config.get(CONF_T1_NAME):
            _LOGGER.info("Add the t1 device with name: %s.", config.get(CONF_T1_NAME))
            entities.append(
                EdDevice(
                    controller,
                    "current_t1",
                    config.get(CONF_T1_NAME),
                    config.get(CONF_T1_UNIT_OF_MEASUREMENT),
                    "mdi:flash",
                    "power",
                )
            )
        if config.get(CONF_T2_NAME):
            _LOGGER.info("Add the t2 device with name: %s.", config.get(CONF_T2_NAME))
            entities.append(
                EdDevice(
                    controller,
                    "current_t2",
                    config.get(CONF_T2_NAME),
                    config.get(CONF_T2_UNIT_OF_MEASUREMENT),
                    "mdi:flash",
                    "power",
                )
            )
        if config.get(CONF_C1_NAME):
            _LOGGER.info("Add the c1 device with name: %s.", config.get(CONF_C1_NAME))
            entities.append(
                EdDevice(
                    controller,
                    "daily_c1",
                    f"{config.get(CONF_C1_NAME)} Daily",
                    config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                    config.get(CONF_C1_ICON),
                    config.get(CONF_C1_DEVICE_CLASS),
                )
            )
            entities.append(
                EdDevice(
                    controller,
                    "total_c1",
                    f"{config.get(CONF_C1_NAME)} Total",
                    config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                    config.get(CONF_C1_ICON),
                    config.get(CONF_C1_DEVICE_CLASS),
                )
            )
        if config.get(CONF_C2_NAME):
            _LOGGER.info("Add the c2 device with name: %s.", config.get(CONF_C2_NAME))
            entities.append(
                EdDevice(
                    controller,
                    "daily_c2",
                    f"{config.get(CONF_C1_NAME)} Daily",
                    config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                    config.get(CONF_C2_ICON),
                    config.get(CONF_C2_DEVICE_CLASS),
                )
            )
            entities.append(
                EdDevice(
                    controller,
                    "total_c2",
                    f"{config.get(CONF_C1_NAME)} Total",
                    config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                    config.get(CONF_C2_ICON),
                    config.get(CONF_C2_DEVICE_CLASS),
                )
            )
    else:
        _LOGGER.error(
            "Can't connect to the platform %s:%s, please check host, port and authentication parameters if enabled.",
            config.get(CONF_HOST), config.get(CONF_PORT),
        )
    if entities:
        add_entities(entities, True)


class EdDevice(Entity):
    """Representation of a Sensor."""

    def __init__(self, controller, request, name, unit, icon, device_class):
        """Initialize the sensor."""
        self._controller = controller
        self._request = request
        self._name = name
        self._unit = unit
        self._icon = icon
        self._device_class = device_class

        self._state = None
        self._uid = f"{self._controller.host}_{str(self._request)}"

    @property
    def device_info(self):
        return {
            "identifiers": {("ecodevices", self._uid)},
            "name": self._name,
            "manufacturer": "GCE",
            "model": "ECO-DEVICES",
            "via_device": ("ecodevices", self._controller.host),
        }

    @property
    def unique_id(self):
        return self._uid

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
