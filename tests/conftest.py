"""Fixtures of the GCE Eco-Devices tests."""

from collections.abc import Generator
from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

from custom_components.ecodevices.const import (
    CONF_C1_DEVICE_CLASS,
    CONF_C1_DIVIDER_FACTOR,
    CONF_C1_ENABLED,
    CONF_C1_UNIT_OF_MEASUREMENT,
    CONF_C2_ENABLED,
    CONF_T1_ENABLED,
    CONF_T1_TYPE,
    CONF_T2_ENABLED,
    CONF_T2_TYPE,
    DOMAIN,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

HOST = "192.168.1.10"
PORT = 80
MAC = "00:04:A3:00:00:01"

ENTRY_DATA = {
    CONF_HOST: HOST,
    CONF_PORT: PORT,
    CONF_USERNAME: "admin",
    CONF_PASSWORD: "secret",
    CONF_SCAN_INTERVAL: 5,
    CONF_T1_ENABLED: True,
    CONF_T1_TYPE: "tempo",
    CONF_T2_ENABLED: True,
    CONF_T2_TYPE: "hchp",
    CONF_C1_ENABLED: True,
    CONF_C1_DEVICE_CLASS: "gas",
    CONF_C1_DIVIDER_FACTOR: 100,
    CONF_C1_UNIT_OF_MEASUREMENT: "m³",
    CONF_C2_ENABLED: False,
}

# Values returned by EcoDevices.global_get
DEVICE_DATA: dict[str, Any] = {
    "config_mac": MAC,
    "version": "3.00.02",
    "meter2": "1520",
    "count0": "1234567",
    "c0_fuel": "123",
    "c0day": "250",
    "T1_PAPP": "1250",
    "T1_PTEC": "HPJB",
    "T1_DEMAIN": "BLANC",
    "T1_ADCO": "021728123456",
    "T1_ISOUSC": "45",
    "T1_BBRHCJB": "1000",
    "T1_BBRHPJB": "2000",
    "T1_BBRHCJW": "300",
    "T1_BBRHPJW": "400",
    "T1_BBRHCJR": "50",
    "T1_BBRHPJR": "60",
    "T2_PAPP": "780",
    "T2_PTEC": "HC..",
    "T2_ADCO": "021728654321",
    "T2_BASE": "11000",
    "T2_HCHC": "5000",
    "T2_HCHP": "7000",
}


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return the snapshot assertion with the Home Assistant serializer."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable the custom integrations in every test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the config entry of an Eco-Devices."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"Eco-Devices {HOST}:{PORT}",
        unique_id=f"{DOMAIN}_{HOST}_{PORT}",
        data=ENTRY_DATA,
        version=2,
    )


@pytest.fixture
def mock_ecodevices() -> Generator[MagicMock]:
    """Mock the Eco-Devices API client."""
    client = MagicMock()
    client.host = HOST
    client.port = PORT
    client.mac_address = MAC
    client.version = "3.00.02"
    client.get_info = AsyncMock()
    client.global_get = AsyncMock(return_value=deepcopy(DEVICE_DATA))
    with (
        patch(
            "custom_components.ecodevices.coordinator.EcoDevices", return_value=client
        ),
        patch(
            "custom_components.ecodevices.config_flow.EcoDevices", return_value=client
        ),
    ):
        yield client
