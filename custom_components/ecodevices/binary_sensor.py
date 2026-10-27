"""Support for the GCE Eco-Devices binary sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_HCHP,
    CONF_TI_TYPE_TEMPO,
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

    entities: list[BinarySensorEntity] = []

    for input_number, enabled_key, type_key in (
        (1, CONF_T1_ENABLED, CONF_T1_TYPE),
        (2, CONF_T2_ENABLED, CONF_T2_TYPE),
    ):
        if config.get(enabled_key) and config.get(type_key) in (
            CONF_TI_TYPE_HCHP,
            CONF_TI_TYPE_TEMPO,
        ):
            _LOGGER.debug("Add the teleinfo %s binary_sensor entities", input_number)
            entities.append(
                TeleinfoInputHeuresCreuses(
                    coordinator, input_number=input_number, input_name="PTEC"
                )
            )

    async_add_entities(entities)


class TeleinfoInputHeuresCreuses(EcoDevicesEntity, BinarySensorEntity):
    """Representation of a Eco-Devices HC binary sensor."""

    def __init__(
        self,
        coordinator: EcoDevicesCoordinator,
        input_number: int,
        input_name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(
            coordinator,
            unique_id_suffix=f"binary_sensor_{input_number}_{input_name}",
            translation_key="off_peak",
            input_number=input_number,
        )
        self._input_name = input_name

    @property
    def is_on(self) -> bool | None:
        """Return the state."""
        if type_heure := self.coordinator.data.get(
            f"T{self._input_number}_{self._input_name}"
        ):
            return type_heure.startswith("HC")
        return None
