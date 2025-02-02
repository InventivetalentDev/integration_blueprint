"""Adds config flow for Blueprint."""
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from custom_components.vrknock_client.client import VRKnockClient

from .api import IntegrationBlueprintApiClient
from .const import (
    CONF_HOST,
    CONF_CODE,
    CONF_MODE,
    DOMAIN,
    PLATFORMS,
)


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}
        print("async_step_user")

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            err = await self._test_credentials(
                user_input[CONF_HOST], user_input[CONF_CODE]
            )
            if err is None:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )
            else:
                self._errors["base"] = err

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_HOST] = ""
        user_input[CONF_CODE] = ""
        user_input[CONF_MODE] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BlueprintOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        print("_show_config_form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_CODE, default=user_input[CONF_CODE]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, host, code):
        """Return None if credentials is valid."""
        print("_test_credentials")
        try:
            client = VRKnockClient(host, code)
            status = await client.get_status()
            print("query_status get_status")
            print(status)
            if status["status"] == 0:
                return None
            print("Error: " + status["msg"])
            return status["msg"]
        except Exception as err:
            raise
        return "unknown error"


class BlueprintOptionsFlowHandler(config_entries.OptionsFlow):
    """Blueprint config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_HOST), data=self.options
        )
