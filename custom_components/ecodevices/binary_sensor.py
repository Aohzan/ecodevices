"""Support for the GCE Eco-Devices binary sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_HCHP,
    CONF_TI_TYPE_TEMPO,
    DOMAIN,
)
from .coordinator import EcoDevicesConfigEntry, EcoDevicesCoordinator, get_entry_config
from .entity import EcoDevicesEntity, entity_unique_id

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

    entity_registry = er.async_get(hass)
    entities: list[BinarySensorEntity] = []

    for input_number, enabled_key, type_key in (
        (1, CONF_T1_ENABLED, CONF_T1_TYPE),
        (2, CONF_T2_ENABLED, CONF_T2_TYPE),
    ):
        if not config.get(enabled_key):
            continue
        if config.get(type_key) in (CONF_TI_TYPE_HCHP, CONF_TI_TYPE_TEMPO):
            _LOGGER.debug("Add the teleinfo %s binary_sensor entities", input_number)
            entities.append(
                TeleinfoInputHeuresCreuses(
                    coordinator, input_number=input_number, input_name="PTEC"
                )
            )
        # An input with the base rate has no off-peak hours: remove the entity
        # created by the older versions, or before a change of the rate
        elif entity_id := entity_registry.async_get_entity_id(
            Platform.BINARY_SENSOR,
            DOMAIN,
            entity_unique_id(
                coordinator.controller.mac_address,
                _off_peak_unique_id_suffix(input_number),
            ),
        ):
            _LOGGER.debug("Remove the off-peak binary sensor %s", entity_id)
            entity_registry.async_remove(entity_id)

    async_add_entities(entities)


def _off_peak_unique_id_suffix(input_number: int, input_name: str = "PTEC") -> str:
    """Return the suffix of the unique ID of an off-peak binary sensor."""
    return f"binary_sensor_{input_number}_{input_name}"


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
            unique_id_suffix=_off_peak_unique_id_suffix(input_number, input_name),
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
