"""Support for the GCE Eco-Devices."""

from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.components.sensor import (
    DEVICE_CLASS_STATE_CLASSES,
    RestoreSensor,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfApparentPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

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
    TELEINFO_EXTRA_ATTR,
    TELEINFO_TEMPO_INDEXES,
)
from .coordinator import EcoDevicesConfigEntry, EcoDevicesCoordinator, get_entry_config
from .entity import EcoDevicesEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EcoDevicesConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the GCE Eco-Devices platform."""
    coordinator = entry.runtime_data
    config = get_entry_config(entry)

    entities: list[EdSensorEntity] = []

    for ti_input_number, enabled_key, type_key in (
        (1, CONF_T1_ENABLED, CONF_T1_TYPE),
        (2, CONF_T2_ENABLED, CONF_T2_TYPE),
    ):
        if not config.get(enabled_key):
            continue
        _LOGGER.debug("Add the teleinfo %s sensor entities", ti_input_number)
        ti_type = config.get(type_key)
        energy = {
            "unit": UnitOfEnergy.WATT_HOUR,
            "device_class": SensorDeviceClass.ENERGY,
            "state_class": SensorStateClass.TOTAL_INCREASING,
        }

        entities.append(
            TeleinfoInputEdDevice(
                coordinator,
                input_number=ti_input_number,
                input_name=f"T{ti_input_number}",
                translation_key="teleinfo",
                unit=UnitOfApparentPower.VOLT_AMPERE,
                device_class=SensorDeviceClass.APPARENT_POWER,
                state_class=SensorStateClass.MEASUREMENT,
            )
        )
        if ti_type == CONF_TI_TYPE_BASE:
            entities.append(
                TeleinfoInputTotalEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_total",
                    translation_key="teleinfo_total",
                    **energy,
                )
            )
        elif ti_type == CONF_TI_TYPE_HCHP:
            entities.append(
                TeleinfoInputTotalHchpEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_total",
                    translation_key="teleinfo_total",
                    **energy,
                )
            )
            entities.append(
                TeleinfoInputTotalHcEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_total_hc",
                    translation_key="teleinfo_total_hc",
                    **energy,
                )
            )
            entities.append(
                TeleinfoInputTotalHpEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_total_hp",
                    translation_key="teleinfo_total_hp",
                    **energy,
                )
            )
        elif ti_type == CONF_TI_TYPE_TEMPO:
            entities.append(
                TeleinfoInputTotalTempoEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_total",
                    translation_key="teleinfo_total",
                    **energy,
                )
            )
            entities.extend(
                TeleinfoInputTempoEdDevice(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_{key}",
                    translation_key=translation_key,
                    **energy,
                )
                for key, translation_key in TELEINFO_TEMPO_INDEXES.items()
            )
            entities.append(
                TeleinfoInputColor(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_PTEC",
                    translation_key="tempo_color",
                    device_class=SensorDeviceClass.ENUM,
                )
            )
            entities.append(
                TeleinfoInputColor(
                    coordinator,
                    input_number=ti_input_number,
                    input_name=f"T{ti_input_number}_DEMAIN",
                    translation_key="tempo_color_tomorrow",
                    device_class=SensorDeviceClass.ENUM,
                )
            )

    for (
        ci_input_number,
        enabled_key,
        unit_key,
        total_unit_key,
        class_key,
        factor_key,
    ) in (
        (
            1,
            CONF_C1_ENABLED,
            CONF_C1_UNIT_OF_MEASUREMENT,
            CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
            CONF_C1_DEVICE_CLASS,
            CONF_C1_DIVIDER_FACTOR,
        ),
        (
            2,
            CONF_C2_ENABLED,
            CONF_C2_UNIT_OF_MEASUREMENT,
            CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
            CONF_C2_DEVICE_CLASS,
            CONF_C2_DIVIDER_FACTOR,
        ),
    ):
        if not config.get(enabled_key):
            continue
        _LOGGER.debug("Add the meter %s sensor entities", ci_input_number)
        unit = config.get(unit_key)
        device_class = config.get(class_key)
        divider_factor = config.get(factor_key)

        entities.append(
            MeterInputEdDevice(
                coordinator,
                input_number=ci_input_number,
                input_name=f"c{ci_input_number}",
                translation_key="meter",
                unit=unit,
                device_class=device_class,
                state_class=SensorStateClass.MEASUREMENT
                if SensorStateClass.MEASUREMENT
                in DEVICE_CLASS_STATE_CLASSES.get(device_class, {})
                else None,
                divider_factor=divider_factor,
            )
        )
        entities.append(
            MeterInputDailyEdDevice(
                coordinator,
                input_number=ci_input_number,
                input_name=f"c{ci_input_number}_daily",
                translation_key="meter_daily",
                unit=unit,
                device_class=device_class,
                state_class=SensorStateClass.TOTAL,
                divider_factor=divider_factor,
            )
        )
        entities.append(
            MeterInputTotalEdDevice(
                coordinator,
                input_number=ci_input_number,
                input_name=f"c{ci_input_number}_total",
                translation_key="meter_total",
                unit=config.get(total_unit_key, unit),
                device_class=device_class,
                state_class=SensorStateClass.TOTAL_INCREASING,
            )
        )

    async_add_entities(entities)


class EdSensorEntity(EcoDevicesEntity, RestoreSensor):
    """Representation of a generic Eco-Devices sensor."""

    def __init__(
        self,
        coordinator: EcoDevicesCoordinator,
        input_number: int,
        input_name: str,
        translation_key: str,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        divider_factor: float | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            unique_id_suffix=f"sensor_{input_name}",
            translation_key=translation_key,
            input_number=input_number,
        )
        self._input_name = input_name
        self._divider_factor = divider_factor

        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

        self._last_state: StateType | None = None

    async def async_added_to_hass(self) -> None:
        """Restore the last value on startup, to ignore decreasing totals."""
        await super().async_added_to_hass()

        if (
            last_sensor_data := await self.async_get_last_sensor_data()
        ) is not None and last_sensor_data.native_value is not None:
            self._last_state = last_sensor_data.native_value
        elif (last_state := await self.async_get_last_state()) is not None and (
            last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
        ):
            self._last_state = last_state.state

    @callback
    def async_entity_id_changed(self, old_entity_id: str) -> None:
        """Keep the entity on an entity ID change, the restored value is kept."""
        super().async_entity_id_changed(old_entity_id)

    def _increasing_total(self, value: float) -> float | None:
        """Return the total if it's greater than 0 and not lower than the last one."""
        if value <= 0:
            _LOGGER.debug("Value for %s equal to 0, ignore", self.entity_id)
            return None
        if self._last_state is None or value >= float(self._last_state):
            self._last_state = value
            return value
        _LOGGER.warning(
            "Value %s for %s not greater or equal to the previous one %s, ignore",
            value,
            self.entity_id,
            self._last_state,
        )
        return None


class TeleinfoInputEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input sensor."""

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.data[f"T{self._input_number}_PAPP"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        if not self.coordinator.data:
            return None
        return {
            k: self.coordinator.data.get(f"T{self._input_number}_{v}")
            for k, v in TELEINFO_EXTRA_ATTR.items()
        }


class TeleinfoInputTotalEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        return self._increasing_total(
            float(self.coordinator.data[f"T{self._input_number}_BASE"])
        )


class TeleinfoInputTotalHchpEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HCHP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        value_hc = float(self.coordinator.data[f"T{self._input_number}_HCHC"])
        value_hp = float(self.coordinator.data[f"T{self._input_number}_HCHP"])
        return self._increasing_total(value_hc + value_hp)


class TeleinfoInputTotalHcEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HC Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        return self._increasing_total(
            float(self.coordinator.data[f"T{self._input_number}_HCHC"])
        )


class TeleinfoInputTotalHpEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input HP Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        return self._increasing_total(
            float(self.coordinator.data[f"T{self._input_number}_HCHP"])
        )


class TeleinfoInputTotalTempoEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Tempo Total sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        return self._increasing_total(
            sum(
                float(self.coordinator.data[f"T{self._input_number}_{key}"])
                for key in TELEINFO_TEMPO_INDEXES
            )
        )


class TeleinfoInputTempoEdDevice(EdSensorEntity):
    """Initialize the Teleinfo Input Tempo sensor."""

    @property
    def native_value(self) -> float | None:
        """Return the total value if it's greater than 0."""
        return self._increasing_total(
            float(self.coordinator.data[self._input_name.upper()])
        )


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
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        if not self.coordinator.data:
            return None
        return {
            "total": self.coordinator.data[f"count{self._input_number - 1}"],
            "fuel": self.coordinator.data[f"c{self._input_number - 1}_fuel"],
        }


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
        """Return the total value in thousands, if it's greater than 0."""
        # The restored value is in thousands too
        return self._increasing_total(
            float(self.coordinator.data[f"count{self._input_number - 1}"]) / 1000
        )
