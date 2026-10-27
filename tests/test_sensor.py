"""Tests of the sensors of the GCE Eco-Devices integration."""

from unittest.mock import MagicMock

from freezegun.api import FrozenDateTimeFactory
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    snapshot_platform,
)
from syrupy.assertion import SnapshotAssertion

from custom_components.ecodevices.const import CONF_T2_TYPE
from homeassistant.const import STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import DEVICE_DATA, ENTRY_DATA


@pytest.mark.parametrize("platform", [Platform.BINARY_SENSOR, Platform.SENSOR])
async def test_entities(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
    platform: Platform,
) -> None:
    """Test the entities and their states."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("custom_components.ecodevices.PLATFORMS", [platform])
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


async def test_off_peak_binary_sensor_per_input(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test an input with the base rate has no off-peak binary sensor."""
    entry = MockConfigEntry(
        domain="ecodevices",
        data=ENTRY_DATA | {CONF_T2_TYPE: "base"},
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    binary_sensors = [
        entity.unique_id
        for entity in er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        if entity.domain == Platform.BINARY_SENSOR
    ]
    assert binary_sensors == ["ecodevices_00_04_a3_00_00_01_binary_sensor_1_ptec"]


async def test_decreasing_total_ignored(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test a total lower than the previous one is ignored."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "sensor.eco_devices_192_168_1_10_80_meter_1_total"
    assert hass.states.get(entity_id).state == "1234.567"

    mock_ecodevices.global_get.return_value = DEVICE_DATA | {"count0": "1000"}
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_UNKNOWN

    mock_ecodevices.global_get.return_value = DEVICE_DATA | {"count0": "1300000"}
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "1300.0"
