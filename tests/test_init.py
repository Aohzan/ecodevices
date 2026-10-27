"""Tests of the setup of the GCE Eco-Devices integration."""

from unittest.mock import MagicMock, patch

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
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
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


async def test_options_with_connection_settings(
    hass: HomeAssistant, mock_ecodevices: MagicMock
) -> None:
    """Test an entry of the older versions, with the address in the options.

    The options flow of the older versions stored the host, port and
    credentials in the options, which override the data.
    """
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=f"{DOMAIN}_{HOST}_{PORT}",
        data={
            CONF_HOST: HOST,
            CONF_PORT: PORT,
            CONF_SCAN_INTERVAL: 5,
            CONF_T1_ENABLED: True,
            "t1_hchp": False,
        },
        options={
            CONF_HOST: HOST,
            CONF_PORT: PORT,
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
            CONF_SCAN_INTERVAL: 10,
            CONF_T1_ENABLED: True,
            "t1_hchp": True,
        },
        version=1,
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.ecodevices.coordinator.EcoDevices",
        return_value=mock_ecodevices,
    ) as mock_class:
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert entry.options[CONF_T1_TYPE] == "hchp"
        assert mock_class.call_args.args == (HOST, PORT, "admin", "secret")
        assert entry.runtime_data.update_interval.total_seconds() == 10

        # The new address replaces the one of the options
        result = await entry.start_reconfigure_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "192.168.1.20", CONF_PORT: 80}
        )
        await hass.async_block_till_done()

        assert result["reason"] == "reconfigure_successful"
        assert entry.data[CONF_HOST] == "192.168.1.20"
        assert CONF_HOST not in entry.options
        assert mock_class.call_args.args == ("192.168.1.20", 80, "admin", "secret")
