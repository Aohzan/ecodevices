"""Config flow to configure the eco-devices integration."""
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)

from .const import (
    CONF_C1_ENABLED,
    CONF_C1_NAME,
    CONF_C2_ENABLED,
    CONF_C2_NAME,
    CONF_T1_ENABLED,
    CONF_T1_NAME,
    CONF_T1_UNIT_OF_MEASUREMENT,
    CONF_T2_ENABLED,
    CONF_T2_NAME,
    CONF_T2_UNIT_OF_MEASUREMENT,
    CONFIG,
    CONTROLLER,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default="Eco-Devices"): str,
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Required(CONF_T1_ENABLED, default=False): bool,
        vol.Required(CONF_T2_ENABLED, default=False): bool,
        vol.Required(CONF_C1_ENABLED, default=False): bool,
        vol.Required(CONF_C2_ENABLED, default=False): bool,
    }
)

# @config_entries.HANDLERS.register(DOMAIN)
class EcodevicesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a eco-devices config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_import(self, user_input=None):
        """Handle configuration by yaml file."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            entry = await self.async_set_unique_id(
                f"{DOMAIN}, {user_input.get(CONF_HOST)}"
            )

            if entry:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_HOST), data=user_input
            )

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
