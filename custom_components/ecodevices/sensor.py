"""Support for the GCE Eco-Devices."""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_ENABLED,
    CONF_C1_NAME,
    CONF_C1_UNIT_OF_MEASUREMENT,
    CONF_C2_DEVICE_CLASS,
    CONF_C2_ENABLED,
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
    COORDINATOR,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the GCE Eco-Devices platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    controller = data[CONTROLLER]
    coordinator = data[COORDINATOR]
    config = data[CONFIG]

    entities = []

    if config.get(CONF_T1_ENABLED):
        _LOGGER.debug("Add the t1 entity.")
        entities.append(
            T1EdDevice(
                controller,
                coordinator,
                "t1",
                config.get(CONF_T1_NAME),
                config.get(CONF_T1_UNIT_OF_MEASUREMENT),
                "power",
                "mdi:flash",
            )
        )
    if config.get(CONF_T2_ENABLED):
        _LOGGER.debug("Add the t2 entity.")
        entities.append(
            T2EdDevice(
                controller,
                coordinator,
                "t2",
                config.get(CONF_T2_NAME),
                config.get(CONF_T2_UNIT_OF_MEASUREMENT),
                "power",
                "mdi:flash",
            )
        )
    if config.get(CONF_C1_ENABLED):
        _LOGGER.debug("Add the c1 entity.")
        entities.append(
            C1EdDevice(
                controller,
                coordinator,
                "c1",
                config.get(CONF_C1_NAME),
                config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                config.get(CONF_C1_DEVICE_CLASS),
            )
        )
    if config.get(CONF_C2_ENABLED):
        _LOGGER.debug("Add the c2 entity.")
        entities.append(
            C2EdDevice(
                controller,
                coordinator,
                "c2",
                config.get(CONF_C2_NAME),
                config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                config.get(CONF_C2_DEVICE_CLASS),
            )
        )

    if entities:
        async_add_entities(entities, True)


class EdDevice(CoordinatorEntity):
    """Representation of a generic Eco-Devices sensor."""

    def __init__(
        self,
        controller,
        coordinator,
        input_name,
        name,
        unit,
        device_class,
        icon=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.controller = controller
        self._input_name = input_name
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._icon = icon
        self._state = None

    @property
    def device_info(self):
        """Return device information identifier."""
        return {
            "identifiers": {(DOMAIN, self.controller.host)},
            "via_device": (DOMAIN, self.controller.host),
        }

    @property
    def unique_id(self):
        """Return an unique id."""
        return "_".join(
            [
                DOMAIN,
                self.controller.host,
                "sensor",
                self._input_name,
            ]
        )

    @property
    def device_class(self):
        """Return the device_class."""
        return self._device_class

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement if specified."""
        return self._unit

    @property
    def icon(self):
        """Return the icon if specified."""
        return self._icon


class T1EdDevice(EdDevice):
    """Initialize the T1 sensor."""

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data["T1_PAPP"]

    @property
    def state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "ptec": self.coordinator.data["T1_PTEC"],
                "souscription": self.coordinator.data["T1_ISOUSC"],
                "intensite_max": self.coordinator.data["T1_IMAX"],
                "intensite_max_ph1": self.coordinator.data["T1_IMAX1"],
                "intensite_max_ph2": self.coordinator.data["T1_IMAX2"],
                "intensite_max_ph3": self.coordinator.data["T1_IMAX3"],
            }


class T2EdDevice(EdDevice):
    """Initialize the T2 sensor."""

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data["T2_PAPP"]

    @property
    def state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "ptec": self.coordinator.data["T2_PTEC"],
                "souscription": self.coordinator.data["T2_ISOUSC"],
                "intensite_max": self.coordinator.data["T2_IMAX"],
                "intensite_max_ph1": self.coordinator.data["T2_IMAX1"],
                "intensite_max_ph2": self.coordinator.data["T2_IMAX2"],
                "intensite_max_ph3": self.coordinator.data["T2_IMAX3"],
            }


class C1EdDevice(EdDevice):
    """Initialize the C1 sensor."""

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data["c0day"]

    @property
    def state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "total": self.coordinator.data["count0"],
                "fuel": self.coordinator.data["c0_fuel"],
            }


class C2EdDevice(EdDevice):
    """Initialize the C2 sensor."""

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data["c1day"]

    @property
    def state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "total": self.coordinator.data["count1"],
                "fuel": self.coordinator.data["c1_fuel"],
            }
