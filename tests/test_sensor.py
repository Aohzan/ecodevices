"""Tests of the sensors of the GCE Eco-Devices integration."""

from typing import Any
from unittest.mock import MagicMock

from freezegun.api import FrozenDateTimeFactory
from pyecodevices import EcoDevicesCannotConnectError
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    mock_restore_cache,
    mock_restore_cache_with_extra_data,
    snapshot_platform,
)
from syrupy.assertion import SnapshotAssertion

from custom_components.ecodevices.const import (
    CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
    CONF_T2_TYPE,
    DOMAIN,
)
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    Platform,
)
from homeassistant.core import HomeAssistant, State
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
        domain=DOMAIN,
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


METER_TOTAL = "sensor.eco_devices_192_168_1_10_80_meter_1_total"


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Set up the entry."""
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def _poll(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_ecodevices: MagicMock,
    count0: str,
) -> str:
    """Return the state of the meter 1 total after an update with this index."""
    mock_ecodevices.global_get.return_value = DEVICE_DATA | {"count0": count0}
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    return hass.states.get(METER_TOTAL).state


async def test_lower_total_glitch_ignored(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    caplog: pytest.LogCaptureFixture,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test a total lower than the previous one on a few updates is ignored."""
    await _setup(hass, mock_config_entry)
    assert hass.states.get(METER_TOTAL).state == "1234.567"

    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1300000") == "1300.0"
    # A new episode needs to be confirmed again
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1300001") == "1300.001"
    # Logged once per episode
    assert caplog.text.count("lower than the previous one") == 2


async def test_lower_total_confirmed_accepted(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    caplog: pytest.LogCaptureFixture,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test a reset of the index is accepted once confirmed on 3 updates."""
    await _setup(hass, mock_config_entry)

    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    # A total equal to 0 is ignored and doesn't confirm the reset
    assert await _poll(hass, freezer, mock_ecodevices, "0") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1500") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "2000") == "2.0"
    assert await _poll(hass, freezer, mock_ecodevices, "2500") == "2.5"
    assert caplog.text.count("lower than the previous one") == 2
    assert "accepted as a reset of the index" in caplog.text


async def test_failed_update_does_not_confirm_reset(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the failed updates don't count the previous data again."""
    await _setup(hass, mock_config_entry)
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN

    mock_ecodevices.global_get.side_effect = EcoDevicesCannotConnectError
    for _ in range(3):
        freezer.tick(10)
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    assert hass.states.get(METER_TOTAL).state == STATE_UNAVAILABLE

    mock_ecodevices.global_get.side_effect = None
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN


@pytest.mark.parametrize(
    ("state", "extra_data"),
    [
        # Stored by this version
        (
            STATE_UNKNOWN,
            {
                "native_value": None,
                "native_unit_of_measurement": "m³",
                "last_total": 2000.0,
            },
        ),
        # Stored by the previous versions
        ("2000.0", {"native_value": 2000.0, "native_unit_of_measurement": "m³"}),
        ("2000.0", None),
    ],
)
async def test_restored_total(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
    state: str,
    extra_data: dict[str, Any] | None,
) -> None:
    """Test a total lower than the restored one is ignored."""
    if extra_data is None:
        mock_restore_cache(hass, [State(METER_TOTAL, state)])
    else:
        mock_restore_cache_with_extra_data(
            hass, [(State(METER_TOTAL, state), extra_data)]
        )
    await _setup(hass, mock_config_entry)

    assert hass.states.get(METER_TOTAL).state == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "2000001") == "2000.001"


async def test_restart_after_ignored_total(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the last accepted total is kept after a restart with an ignored one."""
    await _setup(hass, mock_config_entry)
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN

    assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(METER_TOTAL).state == STATE_UNKNOWN

    assert await _poll(hass, freezer, mock_ecodevices, "1000") == STATE_UNKNOWN
    assert await _poll(hass, freezer, mock_ecodevices, "1000") == "1.0"


@pytest.mark.parametrize(
    ("ptec", "demain", "color", "tomorrow_color"),
    [
        ("HPJB", "BLEU", "🔵", "🔵"),
        ("HCJW", "BLAN", "⚪", "⚪"),
        ("HPJR", "ROUG", "🔴", "🔴"),
        ("HCJB", "----", "🔵", "❓"),
        (None, None, "❓", "❓"),
    ],
)
async def test_tempo_colors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
    ptec: str | None,
    demain: str | None,
    color: str,
    tomorrow_color: str,
) -> None:
    """Test the Tempo colors of today and tomorrow."""
    mock_ecodevices.global_get.return_value = DEVICE_DATA | {
        "T1_PTEC": ptec,
        "T1_DEMAIN": demain,
    }
    await _setup(hass, mock_config_entry)

    assert (
        hass.states.get(
            "sensor.eco_devices_192_168_1_10_80_teleinfo_1_tempo_color"
        ).state
    ) == color
    assert (
        hass.states.get(
            "sensor.eco_devices_192_168_1_10_80_teleinfo_1_tempo_color_tomorrow"
        ).state
    ) == tomorrow_color


@pytest.mark.parametrize(
    ("total_unit", "expected_unit"),
    [(None, "m³"), ("L", "L")],
)
async def test_meter_total_unit(
    hass: HomeAssistant,
    mock_ecodevices: MagicMock,
    total_unit: str | None,
    expected_unit: str,
) -> None:
    """Test the total of a meter has the unit of the meter when it's cleared."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=ENTRY_DATA,
        options={CONF_C1_TOTAL_UNIT_OF_MEASUREMENT: total_unit},
        version=2,
    )
    await _setup(hass, entry)

    assert (
        hass.states.get(METER_TOTAL).attributes[ATTR_UNIT_OF_MEASUREMENT]
        == expected_unit
    )
