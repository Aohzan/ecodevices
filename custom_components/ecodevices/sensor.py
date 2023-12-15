"""Support for the GCE Eco-Devices."""
from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_ENABLED,
    CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
    CONF_C1_UNIT_OF_MEASUREMENT,
    CONF_C2_DEVICE_CLASS,
    CONF_C2_ENABLED,
    CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
    CONF_C2_UNIT_OF_MEASUREMENT,
    CONF_T1_ENABLED,
    CONF_T1_HCHP,
    CONF_T2_ENABLED,
    CONF_T2_HCHP,
    CONTROLLER,
    COORDINATOR,
    DEFAULT_C1_NAME,
    DEFAULT_C2_NAME,
    DEFAULT_T1_NAME,
    DEFAULT_T2_NAME,
    DOMAIN,
    TELEINFO_EXTRA_ATTR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the GCE Eco-Devices platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data[CONTROLLER]
    coordinator = data[COORDINATOR]
    config = entry.data
    options = entry.options

    t1_enabled = options.get(CONF_T1_ENABLED, config.get(CONF_T1_ENABLED))
    t1_hchp = options.get(CONF_T1_HCHP, config.get(CONF_T1_HCHP))
    t2_enabled = options.get(CONF_T2_ENABLED, config.get(CONF_T2_ENABLED))
    t2_hchp = options.get(CONF_T2_HCHP, config.get(CONF_T2_HCHP))
    c1_enabled = options.get(CONF_C1_ENABLED, config.get(CONF_C1_ENABLED))
    c2_enabled = options.get(CONF_C2_ENABLED, config.get(CONF_C2_ENABLED))

    entities: list[EdDevice] = []

    if t1_enabled:
        _LOGGER.debug("Add the teleinfo 1 entities")
        entities.append(
            TeleinfoInputEdDevice(
                controller,
                coordinator,
                input_number=1,
                input_name="t1",
                name=DEFAULT_T1_NAME,
                unit=UnitOfPower.WATT,
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:flash",
            )
        )
        if t1_hchp:
            entities.append(
                TeleinfoInputTotalHchpEdDevice(
                    controller,
                    coordinator,
                    input_number=1,
                    input_name="t1_total",
                    name=DEFAULT_T1_NAME + " Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
            entities.append(
                TeleinfoInputTotalHcEdDevice(
                    controller,
                    coordinator,
                    input_number=1,
                    input_name="t1_total_hc",
                    name=DEFAULT_T1_NAME + " HC Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
            entities.append(
                TeleinfoInputTotalHpEdDevice(
                    controller,
                    coordinator,
                    input_number=1,
                    input_name="t1_total_hp",
                    name=DEFAULT_T1_NAME + " HP Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
        else:
            entities.append(
                TeleinfoInputTotalEdDevice(
                    controller,
                    coordinator,
                    input_number=1,
                    input_name="t1_total",
                    name=DEFAULT_T1_NAME + " Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
    if t2_enabled:
        _LOGGER.debug("Add the teleinfo 2 entities")
        entities.append(
            TeleinfoInputEdDevice(
                controller,
                coordinator,
                input_number=2,
                input_name="t2",
                name=DEFAULT_T2_NAME,
                unit=UnitOfPower.WATT,
                device_class=SensorDeviceClass.POWER,
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:flash",
            )
        )
        if t2_hchp:
            entities.append(
                TeleinfoInputTotalHchpEdDevice(
                    controller,
                    coordinator,
                    input_number=2,
                    input_name="t2_total",
                    name=DEFAULT_T2_NAME + " Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
            entities.append(
                TeleinfoInputTotalHcEdDevice(
                    controller,
                    coordinator,
                    input_number=2,
                    input_name="t2_total_hc",
                    name=DEFAULT_T2_NAME + " HC Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
            entities.append(
                TeleinfoInputTotalHpEdDevice(
                    controller,
                    coordinator,
                    input_number=2,
                    input_name="t2_total_hp",
                    name=DEFAULT_T2_NAME + " HP Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
        else:
            entities.append(
                TeleinfoInputTotalEdDevice(
                    controller,
                    coordinator,
                    input_number=2,
                    input_name="t2_total",
                    name=DEFAULT_T2_NAME + " Total",
                    unit=UnitOfEnergy.WATT_HOUR,
                    device_class=SensorDeviceClass.ENERGY,
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:meter-electric",
                )
            )
    if c1_enabled:
        _LOGGER.debug("Add the meter 1 entities")
        entities.append(
            MeterInputEdDevice(
                controller,
                coordinator,
                input_number=1,
                input_name="c1",
                name=DEFAULT_C1_NAME,
                unit=options.get(
                    CONF_C1_UNIT_OF_MEASUREMENT, config.get(CONF_C1_UNIT_OF_MEASUREMENT)
                ),
                device_class=options.get(
                    CONF_C1_DEVICE_CLASS, config.get(CONF_C1_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:counter",
            )
        )
        entities.append(
            MeterInputDailyEdDevice(
                controller,
                coordinator,
                input_number=1,
                input_name="c1_daily",
                name=DEFAULT_C1_NAME + " Daily",
                unit=options.get(
                    CONF_C1_UNIT_OF_MEASUREMENT, config.get(CONF_C1_UNIT_OF_MEASUREMENT)
                ),
                device_class=options.get(
                    CONF_C1_DEVICE_CLASS, config.get(CONF_C1_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:counter",
            )
        )
        entities.append(
            MeterInputTotalEdDevice(
                controller,
                coordinator,
                input_number=1,
                input_name="c1_total",
                name=DEFAULT_C1_NAME + " Total",
                unit=options.get(
                    CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
                    config.get(
                        CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
                        config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                    ),
                ),
                device_class=options.get(
                    CONF_C1_DEVICE_CLASS, config.get(CONF_C1_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.TOTAL_INCREASING,
                icon="mdi:counter",
            )
        )
    if c2_enabled:
        _LOGGER.debug("Add the meter 2 entities")
        entities.append(
            MeterInputEdDevice(
                controller,
                coordinator,
                input_number=2,
                input_name="c2",
                name=DEFAULT_C2_NAME,
                unit=config.get(CONF_C2_UNIT_OF_MEASUREMENT),
                device_class=options.get(
                    CONF_C2_DEVICE_CLASS, config.get(CONF_C2_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:counter",
            )
        )
        entities.append(
            MeterInputDailyEdDevice(
                controller,
                coordinator,
                input_number=2,
                input_name="c2_daily",
                name=DEFAULT_C2_NAME + " Daily",
                unit=options.get(
                    CONF_C2_UNIT_OF_MEASUREMENT, config.get(CONF_C2_UNIT_OF_MEASUREMENT)
                ),
                device_class=options.get(
                    CONF_C2_DEVICE_CLASS, config.get(CONF_C2_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.MEASUREMENT,
                icon="mdi:counter",
            )
        )
        entities.append(
            MeterInputTotalEdDevice(
                controller,
                coordinator,
                input_number=2,
                input_name="c2_total",
                name=DEFAULT_C2_NAME + " Total",
                unit=options.get(
                    CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
                    config.get(
                        CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
                        config.get(CONF_C1_UNIT_OF_MEASUREMENT),
                    ),
                ),
                device_class=options.get(
                    CONF_C2_DEVICE_CLASS, config.get(CONF_C2_DEVICE_CLASS)
                ),
                state_class=SensorStateClass.TOTAL_INCREASING,
                icon="mdi:counter",
            )
        )

    if entities:
        async_add_entities(entities)


class EdDevice(CoordinatorEntity, SensorEntity):
    """Representation of a generic Eco-Devices sensor."""

    def __init__(
        self,
        controller,
        coordinator,
        input_number: int,
        input_name: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.controller = controller
        self._input_name = input_name
        self._input_number = input_number

        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_unique_id = slugify(
            "_".join(
                [
                    DOMAIN,
                    self.controller.mac_address,
                    "sensor",
                    self._input_name,
                ]
            )
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, controller.mac_address)},
            manufacturer="GCE Electronics",
            model="Eco-Devices",
            name=f"Eco-Devices {controller.host}:{str(controller.port)}",
            sw_version=controller.version,
            connections={(CONNECTION_NETWORK_MAC, controller.mac_address)},
            configuration_url=f"http://{controller.host}:{controller.port}",
        )

        self._state = None


class TeleinfoInputEdDevice(EdDevice):
    """Initialize the Teleinfo Input sensor."""

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.data[f"T{self._input_number}_PAPP"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                k: self.coordinator.data.get(f"T{self._input_number}_{v}")
                for k, v in TELEINFO_EXTRA_ATTR.items()
            }
        raise EcoDevicesIncorrectValueError("Data not received.")


class TeleinfoInputTotalEdDevice(EdDevice):
    """Initialize the Teleinfo Input Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_BASE"])) > 0:
            return value
        _LOGGER.warning("Total value for T1 not greater than 0, ignore")
        return None


class TeleinfoInputTotalHchpEdDevice(EdDevice):
    """Initialize the Teleinfo Input HCHP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        value_hc = float(self.coordinator.data[f"T{self._input_number}_HCHC"])
        value_hp = float(self.coordinator.data[f"T{self._input_number}_HCHP"])
        if (value := value_hc + value_hp) > 0:
            return value
        _LOGGER.warning(
            "Total value for Teleinfo Input %s not greater than 0, ignore",
            self._input_number,
        )
        return None


class TeleinfoInputTotalHcEdDevice(EdDevice):
    """Initialize the Teleinfo Input HC Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_HCHC"])) > 0:
            return value
        _LOGGER.warning(
            "Total value for Teleinfo Input %s not greater than 0, ignore",
            self._input_number,
        )
        return None


class TeleinfoInputTotalHpEdDevice(EdDevice):
    """Initialize the Teleinfo Input HP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_HCHP"])) > 0:
            return value
        _LOGGER.warning(
            "Total value for Teleinfo Input %s not greater than 0, ignore",
            self._input_number,
        )
        return None


class MeterInputEdDevice(EdDevice):
    """Initialize the meter input sensor."""

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.data[f"meter{self._input_number + 1}"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "total": self.coordinator.data[f"count{self._input_number - 1}"],
                "fuel": self.coordinator.data[f"c{self._input_number - 1}_fuel"],
            }
        raise EcoDevicesIncorrectValueError("Data not received.")


class MeterInputDailyEdDevice(EdDevice):
    """Initialize the meter input daily sensor."""

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.data[f"c{self._input_number - 1}day"]


class MeterInputTotalEdDevice(EdDevice):
    """Initialize the meter input total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (
            value := float(self.coordinator.data[f"count{self._input_number - 1}"])
        ) > 0:
            return value / 1000
        _LOGGER.warning(
            "Total value for meter input %s not greater than 0, ignore",
            self._input_number,
        )
        return None


class EcoDevicesIncorrectValueError(Exception):
    """Exception to indicate that the Eco-Device return an incorrect value."""
