"""Platform for BrandweerRooster integration."""
import logging
from typing import Any, Dict
import threading
import json

from fireservicerota import FireServiceRotaOAuth, FireServiceRotaOauthError, FireServiceRotaIncidentsListener

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_ID, CONF_USERNAME, CONF_PASSWORD, CONF_URL
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect

from .const import DOMAIN, ATTRIBUTION, WSS_BWRURL, OAUTH2_TOKENURL, SENSOR_ENTITY_LIST, SIGNAL_UPDATE_INCIDENTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up BrandweerRooster sensor based on a config entry."""

    try:
        oauth = FireServiceRotaOAuth(
            OAUTH2_TOKENURL.format(entry.data[CONF_URL]),
            "",
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )

        token_info = oauth.get_access_token()
    except FireServiceRotaOauthError:
        token_info = None

    if not token_info:
        _LOGGER.error("Failed to get oauth access token")
        return False

    wsurl = WSS_BWRURL.format(entry.data[CONF_URL], token_info['access_token'])

    try:
        incidents_data = IncidentsDataProvider(hass, wsurl)
    except Exception:
        _LOGGER.error("Error while starting incidents listener")
        return False

    fireservice_data = entry.entry_id
    unique_id = entry.unique_id

    entities = []
    for (
        sensor_type,
        (name, unit, icon, device_class, enabled_by_default),
    ) in SENSOR_ENTITY_LIST.items():

        _LOGGER.debug(
            "Registering entity: %s, %s, %s, %s, %s, %s",
            sensor_type,
            name,
            unit,
            icon,
            device_class,
            enabled_by_default,
        )
        entities.append(
            IncidentsSensor(
                incidents_data,
                unique_id,
                sensor_type,
                name,
                unit,
                icon,
                device_class,
                enabled_by_default,
            )
        )

    async_add_entities(entities, True)


class IncidentsDataProvider:
    """Open a websocket connection to BrandweerRooster to get incidents data."""
    def __init__(self, hass, wsurl):

        self._wsurl = wsurl
        self._hass = hass

        self._data = None
        self.listener = None
        self.thread = threading.Thread(target=self.incidents_listener)
        self.thread.daemon = True
        self.thread.start()

    def on_incident(self, data):
        """Update the current data."""
        _LOGGER.debug("Got data from listener: %s", data)
        self._data = data

        """Signal hass to update sensor value."""
        async_dispatcher_send(self._hass, SIGNAL_UPDATE_INCIDENTS)

    @property
    def data(self):
        """Return the current data."""
        return self._data

    def incidents_listener(self):
        """Spawn a new Listener and link it to self.on_incident."""

        _LOGGER.debug("Starting incidents listener forever")
        self.listener = FireServiceRotaIncidentsListener(url=self._wsurl, on_incident=self.on_incident)

        while True:
            try:
                self.listener.run_forever()
            except:
                pass


class IncidentsSensor(Entity):
    """Representation of BrandweerRooster incidents sensor."""
    def __init__(
        self,
        data,
        unique_id,
        sensor_type,
        name,
        unit,
        icon,
        device_class,
        enabled_default: bool = True,
    ):
        """Initialize."""
        self._data = data
        self._unique_id = unique_id
        self._type = sensor_type
        self._name = name
        self._unit = unit
        self._icon = icon
        self._device_class = device_class
        self._enabled_default = enabled_default
        self._available = True
        self._state = None
        self._state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return f"{self._unique_id}_{self._type}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return available attributes for sensor."""
        attr = {}
        data = self._state_attributes

        if data:
            for value in ("id", "state", "created_at", "start_time", "location", "message_to_speech_url",
                    "prio", "type", "responder_mode", "can_respond_until"):
                if data.get(value):
                    attr[value] = data[value]

            try: 
                for address_value in ("address_line1", "address_line2", "street_name", "house_number", "postcode",
                        "city", "country", "state", "latitude", "longitude", "address_type", "formatted_address"):
                    attr[address_value] = data.get("address").get(address_value)
            except:
                pass

            attr[ATTR_ATTRIBUTION] = ATTRIBUTION
            return attr

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": f"{self._name} Sensor",
            "manufacturer": "BrandweerRooster",
        }

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    async def async_added_to_hass(self):
        """Register update callback."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE_INCIDENTS, self.async_on_demand_update
            )
        )

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    async def async_on_demand_update(self):
        """Update state."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        """Update using BrandweerRooster data."""
        if not self.enabled:
            return

        try:
            self._state = self._data.data["body"]
            self._state_attributes = self._data.data
        except (KeyError, TypeError):
            pass

        _LOGGER.debug(
            "Entity state changed to: %s", self._state
        )
