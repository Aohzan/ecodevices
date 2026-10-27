"""Tests of the config flow of the GCE Eco-Devices integration."""

from unittest.mock import MagicMock

from pyecodevices import EcoDevicesCannotConnectError, EcoDevicesInvalidAuthError
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ecodevices.const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_DIVIDER_FACTOR,
    CONF_C1_ENABLED,
    CONF_C2_ENABLED,
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import HOST, PORT

USER_INPUT = {
    CONF_HOST: HOST,
    CONF_PORT: PORT,
    CONF_SCAN_INTERVAL: 10,
    CONF_T1_ENABLED: True,
    CONF_T2_ENABLED: False,
    CONF_C1_ENABLED: True,
    CONF_C2_ENABLED: False,
}
PARAMS_INPUT = {
    CONF_T1_TYPE: "base",
    CONF_C1_DEVICE_CLASS: "water",
    CONF_C1_DIVIDER_FACTOR: 1,
}


async def test_user_flow(hass: HomeAssistant, mock_ecodevices: MagicMock) -> None:
    """Test the creation of an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "params"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], PARAMS_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Eco-Devices {HOST}:{PORT}"
    assert result["data"] == USER_INPUT | PARAMS_INPUT
    assert result["result"].unique_id == f"{DOMAIN}_{HOST}_{PORT}"


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (EcoDevicesCannotConnectError, "cannot_connect"),
        (EcoDevicesInvalidAuthError, "invalid_auth"),
        (RuntimeError, "unknown"),
    ],
)
async def test_user_flow_errors(
    hass: HomeAssistant,
    mock_ecodevices: MagicMock,
    exception: type[Exception],
    error: str,
) -> None:
    """Test the connection errors, and the recovery."""
    mock_ecodevices.get_info.side_effect = exception
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    mock_ecodevices.get_info.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["step_id"] == "params"


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test an Eco-Devices can only be configured once."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the options update the entry and reload it."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["step_id"] == "init"
    # The empty credentials are not sent by the frontend
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_SCAN_INTERVAL: 30,
            CONF_T1_ENABLED: True,
            CONF_T2_ENABLED: False,
            CONF_C1_ENABLED: False,
            CONF_C2_ENABLED: False,
        },
    )
    assert result["step_id"] == "params"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_T1_TYPE: "hchp"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[CONF_SCAN_INTERVAL] == 30
    assert mock_config_entry.options[CONF_T1_TYPE] == "hchp"
    assert mock_config_entry.options[CONF_USERNAME] is None
    assert mock_config_entry.options[CONF_PASSWORD] is None
    # Reloaded with the new options
    assert mock_config_entry.runtime_data.update_interval.total_seconds() == 30


async def test_reauth_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the new credentials replace the ones of the options."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_USERNAME: "old", CONF_PASSWORD: "old"}
    )

    result = await mock_config_entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"

    mock_ecodevices.get_info.side_effect = EcoDevicesInvalidAuthError
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_USERNAME: "admin", CONF_PASSWORD: "wrong"}
    )
    assert result["errors"] == {"base": "invalid_auth"}

    mock_ecodevices.get_info.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_USERNAME: "admin", CONF_PASSWORD: "new"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_PASSWORD] == "new"
    assert CONF_PASSWORD not in mock_config_entry.options


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the address of the Eco-Devices can be changed."""
    mock_config_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.20", CONF_PORT: 8080}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_HOST] == "192.168.1.20"
    assert mock_config_entry.data[CONF_PORT] == 8080
    assert mock_config_entry.unique_id == f"{DOMAIN}_192.168.1.20_8080"
    # The default title follows the address
    assert mock_config_entry.title == "Eco-Devices 192.168.1.20:8080"


async def test_reconfigure_flow_same_device(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the set up Eco-Devices can be reconfigured, keeping a custom title."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(mock_config_entry, title="Garage")
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.20", CONF_PORT: 80}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_HOST] == "192.168.1.20"
    assert mock_config_entry.title == "Garage"


async def test_reconfigure_flow_wrong_device(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the address of another Eco-Devices is refused."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await mock_config_entry.start_reconfigure_flow(hass)
    mock_ecodevices.mac_address = "00:04:A3:00:00:02"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.20", CONF_PORT: 80}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert mock_config_entry.data[CONF_HOST] == HOST
    assert mock_config_entry.unique_id == f"{DOMAIN}_{HOST}_{PORT}"


async def test_reconfigure_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_ecodevices: MagicMock,
) -> None:
    """Test the address of another configured Eco-Devices is refused."""
    mock_config_entry.add_to_hass(hass)
    MockConfigEntry(
        domain=DOMAIN, unique_id=f"{DOMAIN}_192.168.1.20_80", data={}
    ).add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.20", CONF_PORT: 80}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
