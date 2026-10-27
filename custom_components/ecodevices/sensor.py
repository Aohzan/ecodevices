"""Support for the GCE Eco-Devices."""

from collections.abc import Mapping
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    DEVICE_CLASS_STATE_CLASSES,
    RestoreSensor,
    SensorDeviceClass,
    SensorExtraStoredData,
    SensorStateClass,
)
from homeassistant.const import UnitOfApparentPower, UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

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

# Consecutive updates with a total lower than the last accepted one, after
# which the lower total is accepted as a reset of the index
TOTAL_RESET_CONFIRMATIONS = 3

# Symbol and name of the Tempo colors, by suffix of the current period
TEMPO_COLORS = {
    "JB": ("🔵", "Bleu"),
    "JW": ("⚪", "Blanc"),
    "JR": ("🔴", "Ro" + "uge"),  # bypass codespell
}
# Tempo color of tomorrow, by value of DEMAIN
TEMPO_TOMORROW_CODES = {"BLEU": "JB", "BLAN": "JW", "ROUG": "JR"}


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
                # A cleared unit is stored as None
                unit=config.get(total_unit_key) or unit,
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


@dataclass
class EdTotalExtraStoredData(SensorExtraStoredData):
    """Stored data of a total sensor, with the last accepted total."""

    last_total: float | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a dict representation of the stored data."""
        return super().as_dict() | {"last_total": self.last_total}


def _to_float(value: Any) -> float | None:
    """Return the value as a float, or None if it isn't a number."""
    try:
        return float(value)
    except TypeError, ValueError:
        return None


class EdTotalSensorEntity(EdSensorEntity):
    """Representation of an Eco-Devices total, which only increases.

    A total lower than the last accepted one is ignored as a glitch of the
    Eco-Devices, unless it's confirmed on consecutive updates (index reset,
    meter change). A total equal to 0 is always ignored.
    """

    _last_total: float | None = None
    _lower_count = 0

    async def async_added_to_hass(self) -> None:
        """Restore the last accepted total, to keep ignoring the lower ones."""
        await super().async_added_to_hass()

        candidates: list[Any] = []
        if (extra_data := await self.async_get_last_extra_data()) is not None:
            # last_total is missing in the data stored by the older versions
            restored = extra_data.as_dict()
            candidates.extend(
                (restored.get("last_total"), restored.get("native_value"))
            )
        if (last_state := await self.async_get_last_state()) is not None:
            candidates.append(last_state.state)
        self._last_total = next(
            (total for total in map(_to_float, candidates) if total is not None), None
        )
        self._update_total()

    @callback
    def async_entity_id_changed(self, old_entity_id: str) -> None:
        """Keep the entity on an entity ID change, the last total is kept."""
        super().async_entity_id_changed(old_entity_id)

    @property
    def extra_restore_state_data(self) -> EdTotalExtraStoredData:
        """Return the data to restore, with the last accepted total."""
        return EdTotalExtraStoredData(
            self.native_value, self.native_unit_of_measurement, self._last_total
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Check the new total, a failed update keeps the previous data."""
        if self.coordinator.last_update_success:
            self._update_total()
        super()._handle_coordinator_update()

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        raise NotImplementedError

    def _update_total(self) -> None:
        """Set the state to the total read, if it's accepted."""
        self._attr_native_value = self._accept_total(self._read_total())

    def _accept_total(self, value: float) -> float | None:
        """Return the total if it's accepted, otherwise None."""
        if value <= 0:
            _LOGGER.debug("Value for %s equal to 0, ignore", self.entity_id)
            return None
        if self._last_total is not None and value < self._last_total:
            self._lower_count += 1
            if self._lower_count < TOTAL_RESET_CONFIRMATIONS:
                if self._lower_count == 1:
                    _LOGGER.warning(
                        "Value %s for %s lower than the previous one %s, ignored "
                        "until it's confirmed on %s updates",
                        value,
                        self.entity_id,
                        self._last_total,
                        TOTAL_RESET_CONFIRMATIONS,
                    )
                return None
            _LOGGER.info(
                "Value %s for %s lower than the previous one %s on %s updates, "
                "accepted as a reset of the index",
                value,
                self.entity_id,
                self._last_total,
                TOTAL_RESET_CONFIRMATIONS,
            )
        self._lower_count = 0
        self._last_total = value
        return value


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


class TeleinfoInputTotalEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input Total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        return float(self.coordinator.data[f"T{self._input_number}_BASE"])


class TeleinfoInputTotalHchpEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input HCHP Total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        value_hc = float(self.coordinator.data[f"T{self._input_number}_HCHC"])
        value_hp = float(self.coordinator.data[f"T{self._input_number}_HCHP"])
        return value_hc + value_hp


class TeleinfoInputTotalHcEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input HC Total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        return float(self.coordinator.data[f"T{self._input_number}_HCHC"])


class TeleinfoInputTotalHpEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input HP Total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        return float(self.coordinator.data[f"T{self._input_number}_HCHP"])


class TeleinfoInputTotalTempoEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input Tempo Total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        return sum(
            float(self.coordinator.data[f"T{self._input_number}_{key}"])
            for key in TELEINFO_TEMPO_INDEXES
        )


class TeleinfoInputTempoEdDevice(EdTotalSensorEntity):
    """Initialize the Teleinfo Input Tempo sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices."""
        return float(self.coordinator.data[self._input_name.upper()])


class TeleinfoInputColor(EdSensorEntity):
    """Initialize the Teleinfo Input color sensor."""

    _attr_options = [
        "🔵",
        "⚪",
        "🔴",
        "❓",
    ]

    def _color(self) -> tuple[str, str]:
        """Return the symbol and the name of the color."""
        value = (self.coordinator.data.get(self._input_name) or "").strip()
        # The color of tomorrow is BLEU, BLAN, ROUG or ----, the current one
        # is the suffix of the period (HPJB...)
        code = TEMPO_TOMORROW_CODES.get(value[:4], value[-2:])
        return TEMPO_COLORS.get(code, ("❓", "inconnu"))

    @property
    def native_value(self) -> str:
        """Return the state."""
        return self._color()[0]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        return {"name": self._color()[1]}


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


class MeterInputTotalEdDevice(EdTotalSensorEntity):
    """Initialize the meter input total sensor."""

    def _read_total(self) -> float:
        """Return the total read from the Eco-Devices, in thousands."""
        # The restored total is in thousands too
        return float(self.coordinator.data[f"count{self._input_number - 1}"]) / 1000
