"""Config flow to configure the GCE Eco-Devices integration."""

from collections.abc import Iterable, Mapping
import logging
from typing import Any

import probatio
from pyecodevices import (
    EcoDevices,
    EcoDevicesCannotConnectError,
    EcoDevicesInvalidAuthError,
)

from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    DeviceClassSelector,
    DeviceClassSelectorConfig,
    Selector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    UnitOfMeasurementSelector,
    UnitOfMeasurementSelectorConfig,
)

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
    CONF_TI_TYPES,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import EcoDevicesConfigEntry, get_entry_config

_LOGGER = logging.getLogger(__name__)

USERNAME_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
)
PASSWORD_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
)
DEVICE_CLASS_SELECTOR = DeviceClassSelector(
    DeviceClassSelectorConfig(domain=Platform.SENSOR)
)
# Optional fields stored as None when left empty, so that the cleared value
# overrides the one from entry.data
CREDENTIALS_KEYS = (CONF_USERNAME, CONF_PASSWORD)


def _unit_selector(
    device_class_key: str,
) -> Selector[UnitOfMeasurementSelectorConfig]:
    """Return a unit selector filtered by the device class of the meter."""
    return UnitOfMeasurementSelector(
        UnitOfMeasurementSelectorConfig(
            context={"filter_device_class": device_class_key}
        )
    )


BASE_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_HOST): str,
        probatio.Required(CONF_PORT, default=80): int,
        probatio.Optional(CONF_USERNAME): USERNAME_SELECTOR,
        probatio.Optional(CONF_PASSWORD): PASSWORD_SELECTOR,
        probatio.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        probatio.Required(CONF_T1_ENABLED, default=False): bool,
        probatio.Required(CONF_T2_ENABLED, default=False): bool,
        probatio.Required(CONF_C1_ENABLED, default=False): bool,
        probatio.Required(CONF_C2_ENABLED, default=False): bool,
    }
)


CREDENTIALS_SCHEMA = probatio.Schema(
    {
        probatio.Optional(CONF_USERNAME): USERNAME_SELECTOR,
        probatio.Optional(CONF_PASSWORD): PASSWORD_SELECTOR,
    }
)
RECONFIGURE_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_HOST): str,
        probatio.Required(CONF_PORT): int,
    }
)


def _unique_id(host: str, port: int) -> str:
    """Return the unique ID of the config entry of an Eco-Devices."""
    return "_".join([DOMAIN, host, str(port)])


def _default_title(host: str, port: int) -> str:
    """Return the default title of the config entry of an Eco-Devices."""
    return f"Eco-Devices {host}:{port}"


class EcoDevicesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a eco-devices config flow."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize class variables."""
        self.base_input: dict[str, Any] = {}

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=BASE_SCHEMA, errors=errors
            )

        await self.async_set_unique_id(
            _unique_id(user_input[CONF_HOST], user_input[CONF_PORT])
        )
        self._abort_if_unique_id_configured()

        errors, _ = await _test_connection(self.hass, user_input)

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=BASE_SCHEMA, errors=errors
            )

        self.base_input = user_input
        return await self.async_step_params()

    async def async_step_params(self, user_input=None) -> ConfigFlowResult:
        """Handle the param flow to customize the device accordly to enabled inputs."""
        if user_input is not None:
            user_input.update(self.base_input)
            return self.async_create_entry(
                title=_default_title(user_input[CONF_HOST], user_input[CONF_PORT]),
                data=user_input,
            )

        return self.async_show_form(
            step_id="params",
            data_schema=probatio.Schema(_get_params(self.base_input, {})),
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle a rejected authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for new credentials."""
        return await self._async_step_update_entry(
            "reauth_confirm", CREDENTIALS_SCHEMA, user_input
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the address of the Eco-Devices."""
        return await self._async_step_update_entry(
            "reconfigure", RECONFIGURE_SCHEMA, user_input
        )

    async def _async_step_update_entry(
        self, step_id: str, schema: probatio.Schema, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Update the connection settings of the entry after testing them."""
        if self.source == SOURCE_REAUTH:
            entry = self._get_reauth_entry()
        else:
            entry = self._get_reconfigure_entry()
        config = get_entry_config(entry)
        errors: dict[str, str] = {}

        if user_input is not None:
            _fill_cleared(user_input, (key.schema for key in schema.schema))
            new_config = config | user_input
            unique_id = _unique_id(new_config[CONF_HOST], new_config[CONF_PORT])
            if unique_id != entry.unique_id:
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
            errors, mac_address = await _test_connection(self.hass, new_config)
            if not errors:
                if not _is_same_device(self.hass, entry, mac_address):
                    return self.async_abort(reason="wrong_device")
                title = entry.title
                if title == _default_title(config[CONF_HOST], config[CONF_PORT]):
                    title = _default_title(new_config[CONF_HOST], new_config[CONF_PORT])
                # Credentials changed here move from the options to the data
                return self.async_update_reload_and_abort(
                    entry,
                    title=title,
                    unique_id=unique_id,
                    data_updates=user_input,
                    options={
                        key: value
                        for key, value in entry.options.items()
                        if key not in user_input
                    },
                )

        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(
                schema, user_input or config
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: EcoDevicesConfigEntry,
    ) -> EcoDevicesOptionsFlowHandler:
        """Define the config flow to handle options."""
        return EcoDevicesOptionsFlowHandler()


class EcoDevicesOptionsFlowHandler(OptionsFlowWithReload):
    """Handle a EcoDevices options flow."""

    def __init__(self) -> None:
        """Initialize."""
        self.base_input: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors = {}
        if user_input is not None:
            user_input[CONF_HOST] = self.config_entry.data[CONF_HOST]
            user_input[CONF_PORT] = self.config_entry.data[CONF_PORT]
            _fill_cleared(user_input, CREDENTIALS_KEYS)
            errors, _ = await _test_connection(self.hass, user_input)
            if not errors:
                self.base_input = user_input
                return await self.async_step_params()

        config = self.config_entry.data
        options = self.config_entry.options

        scan_interval = options.get(CONF_SCAN_INTERVAL, config.get(CONF_SCAN_INTERVAL))
        username = options.get(CONF_USERNAME, config.get(CONF_USERNAME))
        password = options.get(CONF_PASSWORD, config.get(CONF_PASSWORD))
        t1_enabled = options.get(CONF_T1_ENABLED, config.get(CONF_T1_ENABLED))
        t2_enabled = options.get(CONF_T2_ENABLED, config.get(CONF_T2_ENABLED))
        c1_enabled = options.get(CONF_C1_ENABLED, config.get(CONF_C1_ENABLED))
        c2_enabled = options.get(CONF_C2_ENABLED, config.get(CONF_C2_ENABLED))

        options_schema = {
            probatio.Optional(CONF_USERNAME): USERNAME_SELECTOR,
            probatio.Optional(CONF_PASSWORD): PASSWORD_SELECTOR,
            probatio.Required(CONF_SCAN_INTERVAL, default=scan_interval): int,
            probatio.Required(CONF_T1_ENABLED, default=t1_enabled): bool,
            probatio.Required(CONF_T2_ENABLED, default=t2_enabled): bool,
            probatio.Required(CONF_C1_ENABLED, default=c1_enabled): bool,
            probatio.Required(CONF_C2_ENABLED, default=c2_enabled): bool,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                probatio.Schema(options_schema),
                {CONF_USERNAME: username, CONF_PASSWORD: password},
            ),
            errors=errors,
        )

    async def async_step_params(self, user_input=None) -> ConfigFlowResult:
        """Handle the param flow to customize the device accordly to enabled inputs."""
        if user_input is not None:
            params_schema = _get_params(self.base_input, {})
            _fill_cleared(
                user_input,
                [
                    key.schema
                    for key in params_schema
                    if isinstance(key, probatio.Optional)
                ],
            )
            user_input.update(self.base_input)
            return self.async_create_entry(data=user_input)

        config = self.config_entry.data
        options = self.config_entry.options

        base_params = {
            CONF_T1_TYPE: options.get(
                CONF_T1_TYPE,
                config.get(CONF_T1_TYPE, False),
            ),
            CONF_T2_TYPE: options.get(
                CONF_T2_TYPE,
                config.get(CONF_T2_TYPE, False),
            ),
            CONF_C1_DEVICE_CLASS: options.get(
                CONF_C1_DEVICE_CLASS, config.get(CONF_C1_DEVICE_CLASS)
            ),
            CONF_C1_UNIT_OF_MEASUREMENT: options.get(
                CONF_C1_UNIT_OF_MEASUREMENT, config.get(CONF_C1_UNIT_OF_MEASUREMENT)
            ),
            CONF_C1_DIVIDER_FACTOR: options.get(
                CONF_C1_DIVIDER_FACTOR, config.get(CONF_C1_DIVIDER_FACTOR, 1)
            ),
            CONF_C1_TOTAL_UNIT_OF_MEASUREMENT: options.get(
                CONF_C1_TOTAL_UNIT_OF_MEASUREMENT,
                config.get(CONF_C1_TOTAL_UNIT_OF_MEASUREMENT),
            ),
            CONF_C2_DEVICE_CLASS: options.get(
                CONF_C2_DEVICE_CLASS, config.get(CONF_C2_DEVICE_CLASS)
            ),
            CONF_C2_UNIT_OF_MEASUREMENT: options.get(
                CONF_C2_UNIT_OF_MEASUREMENT, config.get(CONF_C2_UNIT_OF_MEASUREMENT)
            ),
            CONF_C2_DIVIDER_FACTOR: options.get(
                CONF_C2_DIVIDER_FACTOR, config.get(CONF_C2_DIVIDER_FACTOR, 1)
            ),
            CONF_C2_TOTAL_UNIT_OF_MEASUREMENT: options.get(
                CONF_C2_TOTAL_UNIT_OF_MEASUREMENT,
                config.get(CONF_C2_TOTAL_UNIT_OF_MEASUREMENT),
            ),
        }

        return self.async_show_form(
            step_id="params",
            data_schema=self.add_suggested_values_to_schema(
                probatio.Schema(_get_params(self.base_input, base_params)), base_params
            ),
        )


async def _test_connection(
    hass: HomeAssistant, user_input: Mapping[str, Any]
) -> tuple[dict[str, str], str | None]:
    """Connect to the Eco-Devices, returning the errors of the form and its MAC."""
    controller = EcoDevices(
        user_input[CONF_HOST],
        user_input[CONF_PORT],
        user_input.get(CONF_USERNAME),
        user_input.get(CONF_PASSWORD),
        session=async_get_clientsession(hass, verify_ssl=False),
    )

    try:
        await controller.get_info()
    except EcoDevicesInvalidAuthError:
        return {"base": "invalid_auth"}, None
    except EcoDevicesCannotConnectError:
        return {"base": "cannot_connect"}, None
    except Exception:
        _LOGGER.exception("Unexpected error while connecting to the Eco-Devices")
        return {"base": "unknown"}, None
    return {}, controller.mac_address


def _is_same_device(
    hass: HomeAssistant, entry: EcoDevicesConfigEntry, mac_address: str | None
) -> bool:
    """Return False if the MAC address isn't the one of the device of the entry.

    The unique ID of the entry is based on the address, so the MAC address is
    compared with the identifier of the device, known once the entry was set up.
    """
    known_macs = {
        dr.format_mac(identifier)
        for device in dr.async_entries_for_config_entry(
            dr.async_get(hass), entry.entry_id
        )
        for domain, identifier in device.identifiers
        if domain == DOMAIN
    }
    return not known_macs or not mac_address or dr.format_mac(mac_address) in known_macs


def _fill_cleared(user_input: dict[str, Any], keys: Iterable[str]) -> None:
    """Store None for optional fields the frontend omitted because they were empty."""
    for key in keys:
        user_input.setdefault(key, None)


def _get_params(base_input, base_params):
    params_schema = {}
    if base_input[CONF_T1_ENABLED]:
        params_schema.update(
            {
                probatio.Required(
                    CONF_T1_TYPE,
                    default=base_params.get(CONF_T1_TYPE, CONF_TI_TYPE_BASE),
                ): probatio.All(str, probatio.Lower, probatio.In(CONF_TI_TYPES)),
            }
        )

    if base_input[CONF_T2_ENABLED]:
        params_schema.update(
            {
                probatio.Required(
                    CONF_T2_TYPE,
                    default=base_params.get(CONF_T2_TYPE, CONF_TI_TYPE_BASE),
                ): probatio.All(str, probatio.Lower, probatio.In(CONF_TI_TYPES)),
            }
        )

    if base_input[CONF_C1_ENABLED]:
        params_schema.update(
            {
                probatio.Required(
                    CONF_C1_DEVICE_CLASS, default=base_params.get(CONF_C1_DEVICE_CLASS)
                ): DEVICE_CLASS_SELECTOR,
                probatio.Optional(CONF_C1_UNIT_OF_MEASUREMENT): _unit_selector(
                    CONF_C1_DEVICE_CLASS
                ),
                probatio.Required(
                    CONF_C1_DIVIDER_FACTOR,
                    default=base_params.get(CONF_C1_DIVIDER_FACTOR, 1),
                ): int,
                probatio.Optional(CONF_C1_TOTAL_UNIT_OF_MEASUREMENT): _unit_selector(
                    CONF_C1_DEVICE_CLASS
                ),
            }
        )

    if base_input[CONF_C2_ENABLED]:
        params_schema.update(
            {
                probatio.Required(
                    CONF_C2_DEVICE_CLASS, default=base_params.get(CONF_C2_DEVICE_CLASS)
                ): DEVICE_CLASS_SELECTOR,
                probatio.Optional(CONF_C2_UNIT_OF_MEASUREMENT): _unit_selector(
                    CONF_C2_DEVICE_CLASS
                ),
                probatio.Required(
                    CONF_C2_DIVIDER_FACTOR,
                    default=base_params.get(CONF_C2_DIVIDER_FACTOR, 1),
                ): int,
                probatio.Optional(CONF_C2_TOTAL_UNIT_OF_MEASUREMENT): _unit_selector(
                    CONF_C2_DEVICE_CLASS
                ),
            }
        )

    return params_schema
