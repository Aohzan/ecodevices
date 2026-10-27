"""Tests of the setup of the GCE Eco-Devices integration."""

from unittest.mock import MagicMock

from pyecodevices import EcoDevicesCannotConnectError, EcoDevicesInvalidAuthError
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ecodevices.const import (
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .conftest import HOST, PORT


async def test_setup_and_unload(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the setup and unload of an entry."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.runtime_data.data["T1_PAPP"] == "1250"

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize(
    ("method", "state"),
    [
        ("get_info", ConfigEntryState.SETUP_RETRY),
        ("global_get", ConfigEntryState.SETUP_RETRY),
    ],
)
async def test_setup_cannot_connect(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
    method: str,
    state: ConfigEntryState,
) -> None:
    """Test the setup is retried when the Eco-Devices is unreachable."""
    getattr(mock_ecodevices, method).side_effect = EcoDevicesCannotConnectError
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is state


async def test_setup_invalid_auth(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test a rejected authentication starts a reauth flow."""
    mock_ecodevices.get_info.side_effect = EcoDevicesInvalidAuthError
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert [flow["context"]["source"] for flow in flows] == [SOURCE_REAUTH]


async def test_migrate_from_version_1(
    hass: HomeAssistant, mock_ecodevices: MagicMock
) -> None:
    """Test the teleinfo HC/HP flags of version 1 become teleinfo types."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=f"{DOMAIN}_{HOST}_{PORT}",
        data={
            CONF_HOST: HOST,
            CONF_PORT: PORT,
            CONF_SCAN_INTERVAL: 5,
            CONF_T1_ENABLED: True,
            "t1_hchp": True,
            CONF_T2_ENABLED: True,
            "t2_hchp": False,
        },
        version=1,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.version == 2
    assert entry.options[CONF_T1_TYPE] == "hchp"
    assert entry.options[CONF_T2_TYPE] == "base"
