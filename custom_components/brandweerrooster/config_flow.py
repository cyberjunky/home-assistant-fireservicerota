"""Config flow for BrandweerRooster."""
from fireservicerota import FireServiceRotaOAuth, FireServiceRotaOauthError

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TOKEN, CONF_URL

from .const import DOMAIN , OAUTH2_TOKENURL, URL_LIST # pylint: disable=unused-import


class FireServiceRotaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a BrandweerRooster config flow."""

    def __init__(self):
        """Initialize the config flow."""
        self.data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_URL, default="www.brandweerrooster.nl"): vol.In(URL_LIST),
            }
        )

    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow."""
        if not user_input:
            return await self._show_form()

        await self.async_set_unique_id(user_input[CONF_USERNAME])
        self._abort_if_unique_id_configured()

        try:
            oauth = FireServiceRotaOAuth(
                OAUTH2_TOKENURL.format(user_input[CONF_URL]), "", user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            token_info = oauth.get_access_token()
        except FireServiceRotaOauthError:
            return await self._show_form(errors={"base": "invalid_credentials"})

        return self.async_create_entry(
            title=user_input[CONF_USERNAME],
            data={
                "auth_implementation": DOMAIN,
                CONF_USERNAME: user_input[CONF_USERNAME],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
                CONF_URL: user_input[CONF_URL],
                CONF_TOKEN: token_info
            },
        )
