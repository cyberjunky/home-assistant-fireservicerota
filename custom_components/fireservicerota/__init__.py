"""The FireServiceRota integration."""
import asyncio
import voluptuous as vol
from datetime import timedelta

from pyfireservicerota import FireServiceRota, ExpiredTokenError, InvalidTokenError
from homeassistant.const import CONF_URL, CONF_TOKEN

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle

from .const import DOMAIN, PLATFORMS, _LOGGER

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
            # TODO await self._hass.async_add_executor_job(self.fsr.update)
            self.data = await self._hass.async_add_executor_job(self.fsr.update)
            _LOGGER.debug("Updating fireservicerota data")
        except ExpiredTokenError:
            _LOGGER.debug("Refreshing expired tokens")
            await self.refresh()

    async def refresh(self) -> bool:
        """Refresh tokens and update config entry."""
        _LOGGER.debug("Refreshing tokens and updating config entry")
        token_info = await self._hass.async_add_executor_job(self.fsr.refresh_tokens)
        # except notify if refresh token is invalid
        
        if token_info:
            self._hass.config_entries.async_update_entry(
                self._entry,
                data={CONF_TOKEN: token_info}
            )

            # TODO: restart websocket
            return True

        _LOGGER.error("Error refreshing tokens")
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    hass.data.pop(DOMAIN)

    tasks = []
    for platform in PLATFORMS:
        tasks.append(
            hass.config_entries.async_forward_entry_unload(config_entry, platform)
        )

    return all(await asyncio.gather(*tasks))
