"""Switch platform for FireServiceRota integration."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN as FIRESERVICEROTA_DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up FireServiceRota switch based on a config entry."""
    coordinator = hass.data[FIRESERVICEROTA_DOMAIN][entry.entry_id]

    async_add_entities([ResponseSwitch(coordinator, entry)])


class ResponseSwitch(SwitchEntity):
    """Representation of an FireServiceRota switch."""

    def __init__(self, coordinator, entry):
        """Initialize."""
        self._coordinator = coordinator
        self._unique_id = entry.unique_id
        self._entry_id = entry.entry_id

        self._state = None
        self._state_attributes = {}

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return "Incident Response"

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:forum"

    @property
    def is_on(self) -> str:
        """Get the assumed state of the switch."""
        return self._state

    @property
    def state(self) -> str:
        """Return the state of the switch."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this switch."""
        return f"{self._unique_id}_Response"

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def device_state_attributes(self) -> object:
        """Return available attributes for switch."""
        attr = {}
        data = self._state_attributes

        if data:
            for value in (
                "user_name",
                "assigned_skill_ids",
                "responded_at",
                "start_time",
                "status",
                "reported_status",
                "arrived_at_station",
                "available_at_incident_creation",
                "active_duty_function_ids",
            ):
                if data.get(value):
                    attr[value] = data[value]

        return attr

    async def async_turn_on(self, **kwargs) -> None:
        """Send Acknowlegde response status."""
        await self._coordinator.async_set_response(True)
        await self.async_update()

    async def async_turn_off(self, **kwargs) -> None:
        """Send Reject response status."""
        await self._coordinator.async_set_response(False)
        await self.async_update()

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{FIRESERVICEROTA_DOMAIN}_{self._entry_id}_update",
                self.coordinator_update,
            )
        )

    async def coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self) -> None:
        """Update FireServiceRota response data."""
        response_data = await self._coordinator.async_response_update()

        if not response_data:
            return

        if "status" in response_data:
            if response_data["status"] == "acknowledged":
                self._state = STATE_ON
            else:
                self._state = STATE_OFF

            del response_data["user_photo"]
            self._state_attributes = response_data

            _LOGGER.debug("Set state of entity 'Response Switch' to '%s'", self._state)
