"""Support for the GCE Eco-Devices."""

from collections.abc import Mapping
import logging
from typing import Any

from pyecodevices import EcoDevices

from homeassistant.components.sensor import (
    DEVICE_CLASS_STATE_CLASSES,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfApparentPower, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_DIVIDER_FACTOR,
    CONF_C1_ENABLED,
    CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
    CONF_C1_UNIT_OF_MEASUREMENT,
    CONF_C2_DEVICE_CLASS,
    CONF_C2_DIVIDER_FACTOR,
    CONF_C2_ENABLED,
    CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
    CONF_C2_UNIT_OF_MEASUREMENT,
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_BASE,
    CONF_TI_TYPE_HCHP,
    CONF_TI_TYPE_TEMPO,
    CONTROLLER,
    COORDINATOR,
    DEFAULT_C1_NAME,
    DEFAULT_C2_NAME,
    DEFAULT_T1_NAME,
    DEFAULT_T2_NAME,
    DOMAIN,
    TELEINFO_EXTRA_ATTR,
    TELEINFO_TEMPO_ATTR,
)
from .entity import get_device_info

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
    t1_type = options.get(CONF_T1_TYPE, config.get(CONF_T1_TYPE))
    t2_enabled = options.get(CONF_T2_ENABLED, config.get(CONF_T2_ENABLED))
    t2_type = options.get(CONF_T2_TYPE, config.get(CONF_T2_TYPE))
    c1_enabled = options.get(CONF_C1_ENABLED, config.get(CONF_C1_ENABLED))
    c2_enabled = options.get(CONF_C2_ENABLED, config.get(CONF_C2_ENABLED))

    entities: list[EdSensorEntity] = []

    for ti_input_number in (1, 2):
        if t1_enabled and ti_input_number == 1 or t2_enabled and ti_input_number == 2:
            _LOGGER.debug("Add the teleinfo %s sensor entities", ti_input_number)
            default_name = DEFAULT_T1_NAME if ti_input_number == 1 else DEFAULT_T2_NAME
            ti_type = t1_type if ti_input_number == 1 else t2_type

            entities.append(
                TeleinfoInputEdDevice(
                    controller,
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}",
                    name=default_name,
                    unit=UnitOfApparentPower.VOLT_AMPERE,
                    device_class=SensorDeviceClass.POWER,
                    state_class=SensorStateClass.MEASUREMENT,
                    icon="mdi:flash",
                )
            )
            if ti_type == CONF_TI_TYPE_BASE:
                entities.append(
                    TeleinfoInputTotalEdDevice(
                        controller,
                        coordinator,
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_total",
                        name=default_name + " Total",
                        unit=UnitOfEnergy.WATT_HOUR,
                        device_class=SensorDeviceClass.ENERGY,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                        icon="mdi:meter-electric",
                    )
                )
            elif ti_type == CONF_TI_TYPE_HCHP:
                entities.append(
                    TeleinfoInputTotalHchpEdDevice(
                        controller,
                        coordinator,
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_total",
                        name=default_name + " Total",
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
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_total_hc",
                        name=default_name + " HC Total",
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
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_total_hp",
                        name=default_name + " HP Total",
                        unit=UnitOfEnergy.WATT_HOUR,
                        device_class=SensorDeviceClass.ENERGY,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                        icon="mdi:meter-electric",
                    )
                )
            elif ti_type == CONF_TI_TYPE_TEMPO:
                entities.append(
                    TeleinfoInputTotalTempoEdDevice(
                        controller,
                        coordinator,
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_total",
                        name=default_name + " Total",
                        unit=UnitOfEnergy.WATT_HOUR,
                        device_class=SensorDeviceClass.ENERGY,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                        icon="mdi:meter-electric",
                    )
                )
                for desc, key in TELEINFO_TEMPO_ATTR.items():
                    entities.append(
                        TeleinfoInputTempoEdDevice(
                            controller,
                            coordinator,
                            input_number=ti_input_number,
                            input_name=f"T{ti_input_number}_{key}",
                            name=default_name + " " + desc + " Total",
                            unit=UnitOfEnergy.WATT_HOUR,
                            device_class=SensorDeviceClass.ENERGY,
                            state_class=SensorStateClass.TOTAL_INCREASING,
                            icon="mdi:meter-electric",
                        )
                    )
                entities.append(
                    TeleinfoInputColor(
                        controller,
                        coordinator,
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_PTEC",
                        name=default_name + " Tempo Couleur",
                        icon="mdi:palette",
                        device_class=SensorDeviceClass.ENUM,
                    )
                )
                entities.append(
                    TeleinfoInputColor(
                        controller,
                        coordinator,
                        input_number=ti_input_number,
                        input_name=f"T{ti_input_number}_DEMAIN",
                        name=default_name + " Tempo Couleur Demain",
                        icon="mdi:palette",
                        device_class=SensorDeviceClass.ENUM,
                    )
                )
    for ci_input_number in (1, 2):
        if c1_enabled and ci_input_number == 1 or c2_enabled and ci_input_number == 2:
            _LOGGER.debug("Add the meter %s sensor entities", ci_input_number)
            default_name = DEFAULT_C1_NAME if ci_input_number == 1 else DEFAULT_C2_NAME
            ci_unit = (
                CONF_C1_UNIT_OF_MEASUREMENT
                if ci_input_number == 1
                else CONF_C2_UNIT_OF_MEASUREMENT
            )
            ci_total_unit = (
                CONF_C1_TOTAL_UNIT_OF_MEASUREMENT
                if ci_input_number == 1
                else CONF_C2_TOTAL_UNIT_OF_MEASUREMENT
            )
            ci_device_class = (
                CONF_C1_DEVICE_CLASS if ci_input_number == 1 else CONF_C2_DEVICE_CLASS
            )
            ci_divider_factor = (
                CONF_C1_DIVIDER_FACTOR
                if ci_input_number == 1
                else CONF_C2_DIVIDER_FACTOR
            )

            entities.append(
                MeterInputEdDevice(
                    controller,
                    coordinator,
                    input_number=ci_input_number,
                    input_name=f"c{ci_input_number}",
                    name=default_name,
                    unit=options.get(ci_unit, config.get(ci_unit)),
                    device_class=options.get(
                        ci_device_class, config.get(ci_device_class)
                    ),
                    state_class=SensorStateClass.MEASUREMENT
                    if (
                        SensorStateClass.MEASUREMENT
                        in (
                            DEVICE_CLASS_STATE_CLASSES.get(
                                options.get(
                                    ci_device_class, config.get(ci_device_class)
                                ),
                                {},
                            )
                        )
                    )
                    else None,
                    icon="mdi:counter",
                    divider_factor=options.get(
                        ci_divider_factor, config.get(ci_divider_factor)
                    ),
                )
            )
            entities.append(
                MeterInputDailyEdDevice(
                    controller,
                    coordinator,
                    input_number=ci_input_number,
                    input_name=f"c{ci_input_number}_daily",
                    name=default_name + " Daily",
                    unit=options.get(ci_unit, config.get(ci_unit)),
                    device_class=options.get(
                        ci_device_class, config.get(ci_device_class)
                    ),
                    state_class=SensorStateClass.TOTAL,
                    icon="mdi:counter",
                    divider_factor=options.get(
                        ci_divider_factor, config.get(ci_divider_factor)
                    ),
                )
            )
            entities.append(
                MeterInputTotalEdDevice(
                    controller,
                    coordinator,
                    input_number=ci_input_number,
                    input_name=f"c{ci_input_number}_total",
                    name=default_name + " Total",
                    unit=options.get(
                        ci_total_unit,
                        config.get(
                            ci_total_unit,
                            config.get(ci_unit),
                        ),
                    ),
                    device_class=options.get(
                        ci_device_class, config.get(ci_device_class)
                    ),
                    state_class=SensorStateClass.TOTAL_INCREASING,
                    icon="mdi:counter",
                )
            )

    if entities:
        async_add_entities(entities)


class EdSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a generic Eco-Devices sensor."""

    def __init__(
        self,
        controller: EcoDevices,
        coordinator: DataUpdateCoordinator,
        input_number: int,
        input_name: str,
        name: str,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
        divider_factor: float | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.controller = controller
        self._input_name = input_name
        self._input_number = input_number
        self._divider_factor = divider_factor

        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_unique_id = slugify(
            f"{DOMAIN}_{self.controller.mac_address}_sensor_{self._input_name}"
        )
        self._attr_device_info = get_device_info(self.controller)

        self._state = None


class TeleinfoInputEdDevice(EdSensorEntity):
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


class TeleinfoInputTotalEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_BASE"])) > 0:
            return value
        _LOGGER.warning("Total value for T1 not greater than 0, ignore")
        return None


class TeleinfoInputTotalHchpEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HCHP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        value_hc = float(self.coordinator.data[f"T{self._input_number}_HCHC"])
        value_hp = float(self.coordinator.data[f"T{self._input_number}_HCHP"])
        if (value := value_hc + value_hp) > 0:
            return value
        return None


class TeleinfoInputTotalHcEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HC Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_HCHC"])) > 0:
            return value
        return None


class TeleinfoInputTotalHpEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[f"T{self._input_number}_HCHP"])) > 0:
            return value
        return None


class TeleinfoInputTotalTempoEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Tempo Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        value = 0.0
        for key in TELEINFO_TEMPO_ATTR.values():
            value += float(self.coordinator.data[f"T{self._input_number}_{key}"])
        if value > 0:
            return value
        return None


class TeleinfoInputTempoEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Tempo sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        if (value := float(self.coordinator.data[self._input_name.upper()])) > 0:
            return value
        return None


class TeleinfoInputColor(EdSensorEntity):
    """Initialize the Teleinfo Input color sensor."""

    _attr_options = [
        "🔵",
        "⚪",
        "🔴",
        "❓",
    ]

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if type_heure := self.coordinator.data.get(self._input_name):
            if type_heure.endswith("JB"):
                return "🔵"
            if type_heure.endswith("JW"):
                return "⚪"
            if type_heure.endswith("JR"):
                return "🔴"
        return "❓"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        color_name = "inconnu"
        if type_heure := self.coordinator.data.get(self._input_name):
            if type_heure.endswith("JB"):
                color_name = "Bleu"
            if type_heure.endswith("JW"):
                color_name = "Blanc"
            if type_heure.endswith("JR"):
                color_name = "Ro" + "uge"  # bypass codespell
        return {"name": color_name}


class MeterInputEdDevice(EdSensorEntity):
    """Initialize the meter input sensor."""

    @property
    def native_value(self) -> float:
        """Return the state."""
        value = int(self.coordinator.data[f"meter{self._input_number + 1}"])
        if self._divider_factor:
            return value / self._divider_factor
        return value

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "total": self.coordinator.data[f"count{self._input_number - 1}"],
                "fuel": self.coordinator.data[f"c{self._input_number - 1}_fuel"],
            }
        raise EcoDevicesIncorrectValueError("Data not received.")


class MeterInputDailyEdDevice(EdSensorEntity):
    """Initialize the meter input daily sensor."""

    @property
    def native_value(self) -> float:
        """Return the state."""
        value = int(self.coordinator.data[f"c{self._input_number - 1}day"])
        if self._divider_factor:
            return value / self._divider_factor
        return value


class MeterInputTotalEdDevice(EdSensorEntity):
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
