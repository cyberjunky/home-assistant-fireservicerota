"""The FireServiceRota integration."""
import asyncio
import voluptuous as vol
from datetime import timedelta

from pyfireservicerota import FireServiceRota, ExpiredTokenError, InvalidTokenError, InvalidAuthError
from homeassistant.const import CONF_URL, CONF_TOKEN

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle

from .const import DOMAIN, PLATFORMS, _LOGGER, NOTIFICATION_AUTH_TITLE, NOTIFICATION_AUTH_ID

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the FireServiceRota component."""

    hass.data[DOMAIN] = {}

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up FireServiceRota from a config entry."""

    data = FireServiceRotaData(hass, entry)
    await data.update()

    hass.data[DOMAIN] = data

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


class FireServiceRotaData:
    """
    Handle getting the latest data from fireservicerota so platforms can use it.
    Also handle refreshing tokens and updating config entry with refreshed tokens.
    """

    def __init__(self, hass, entry):
        """Initialize the data object."""
        self._hass = hass
        self._entry = entry
        self._url = entry.data[CONF_URL]
        self._tokens = entry.data[CONF_TOKEN]

        self.fsr = FireServiceRota(
            base_url = f"https://{self._url}",
            token_info = self._tokens
        )
        self.data = None


    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update(self):
        """Get the latest data from fireservicerota."""
        try:
            self.data = await self._hass.async_add_executor_job(self.fsr.update)
            _LOGGER.debug("Updating fireservicerota data")
        except ExpiredTokenError:
            _LOGGER.debug("Refreshing expired tokens")
            await self.refresh()

    async def refresh(self) -> bool:
        """Refresh tokens and update config entry."""
        _LOGGER.debug("Refreshing tokens and updating config entry")
        try:
            token_info = await self._hass.async_add_executor_job(self.fsr.refresh_tokens)
        except InvalidAuthError: 
            _LOGGER.error("Error occurred while refreshing authentication tokens")
            self._hass.components.persistent_notification.async_create(
                f"Cannot refresh authentication tokens, you need to re-add this integration and login to generate new ones.",
                title=NOTIFICATION_AUTH_TITLE,
                notification_id=NOTIFICATION_AUTH_ID,
            )
            return False

        if token_info:
            self._hass.config_entries.async_update_entry(
                self._entry,
                data={
                    "auth_implementation": DOMAIN,
                    CONF_URL: self._url,
                    CONF_TOKEN: token_info
                }
            )
            return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    hass.data.pop(DOMAIN)

    tasks = []
    for platform in PLATFORMS:
        tasks.append(
            hass.config_entries.async_forward_entry_unload(entry, platform)
        )

    return all(await asyncio.gather(*tasks))
