"""Support for the GCE Eco-Devices binary sensors."""

import logging

from pyecodevices import EcoDevices

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    CONF_TI_TYPE_HCHP,
    CONF_TI_TYPE_TEMPO,
    CONTROLLER,
    COORDINATOR,
    DEFAULT_T1_NAME,
    DEFAULT_T2_NAME,
    DOMAIN,
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

    entities: list[BinarySensorEntity] = []

    for input_number in (1, 2):
        if t1_enabled and input_number == 1 or t2_enabled and input_number == 2:
            _LOGGER.debug("Add the teleinfo %s binary_sensor entities", input_number)
            if t1_type in (CONF_TI_TYPE_HCHP, CONF_TI_TYPE_TEMPO) or t2_type in (
                CONF_TI_TYPE_HCHP,
                CONF_TI_TYPE_TEMPO,
            ):
                prefix_name = DEFAULT_T1_NAME if input_number == 1 else DEFAULT_T2_NAME
                entities.append(
                    TeleinfoInputHeuresCreuses(
                        controller,
                        coordinator,
                        input_number=input_number,
                        input_name="PTEC",
                        name=f"{prefix_name} Heures Creuses",
                    )
                )

    if entities:
        async_add_entities(entities)


class TeleinfoInputHeuresCreuses(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Eco-Devices HC binary sensor."""

    _attr_icon = "mdi:cash-clock"

    def __init__(
        self,
        controller: EcoDevices,
        coordinator: DataUpdateCoordinator,
        input_number: int,
        input_name: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.controller = controller
        self._input_number = input_number
        self._input_name = input_name
        self._attr_name = name
        self._attr_unique_id = slugify(
            f"{DOMAIN}_{self.controller.mac_address}_binary_sensor_{self._input_number}_{self._input_name}"
        )
        self._attr_device_info = get_device_info(self.controller)

    @property
    def is_on(self) -> bool | None:
        """Return the state."""
        if type_heure := self.coordinator.data.get(
            f"T{self._input_number}_{self._input_name}"
        ):
            if type_heure.startswith("HC"):
                return True
            return False
        return None
