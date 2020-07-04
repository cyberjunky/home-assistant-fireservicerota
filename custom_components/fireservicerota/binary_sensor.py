"""Platform for FireServiceRota integration."""
from typing import Any, Dict

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_OCCUPANCY
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.const import ATTR_ATTRIBUTION

from .const import _LOGGER, DOMAIN, BINARY_SENSOR_ENTITY_LIST, ATTRIBUTION

async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up FireServiceRota binary sensors based on a config entry."""

    data = hass.data[DOMAIN]
    unique_id = entry.unique_id

    entities = []
    for (
        sensor_type,
        (name, unit, icon, device_class, enabled_by_default),
    ) in BINARY_SENSOR_ENTITY_LIST.items():

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
            FSRBinarySensor(
                data,
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


class DutySwitchDataProvider:
    """Open a websocket connection to FireServiceRota to get incidents data."""
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
        self.listener = FireServiceRotaIncidents(url=self._wsurl, on_incident=self.on_incident)

        while True:
            try:
                self.listener.run_forever()
            except:
                pass



class FSRBinarySensor(BinarySensorEntity):
    """Representation of an FireServiceRota sensor."""
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
        """Return the state of the binary sensor."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this binary sensor."""
        return f"{self._unique_id}_{self._type}"

    @property
    def device_state_attributes(self):
        """Return available attributes for binary sensor."""
        attr = {}
        attr = self._state_attributes
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": f"{self._name} Binary Sensor",
            "manufacturer": "FireServiceRota",
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
        """Return the device class of the binary sensor."""
        return self._device_class

    @property
    def is_on(self):
        """Return the status of the binary sensor."""
        return self._state

    @property
    def should_poll(self) -> bool:
        """Polling needed."""
        return True

    async def async_on_demand_update(self):
        """Update state."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        """Update using FireServiceRota data."""
        if not self.enabled:
            return

        await self._data.update()
        _LOGGER.debug("DATA: %s", self._data.data)
        try:
            if self._data.data:
                state =  self._data.data['available']
                if state:
                    self._state = 'on'
                else:
                    self._state = 'off'
                self._state_attributes = self._data.data
            else:
                self._state = 'off'
        except (KeyError, TypeError) as err:
            _LOGGER.debug(
                "Error while updating %s device state: %s", self._name, err
            )

        _LOGGER.debug(
            "Entity %s state changed to: %s", self._name, self._state
        )
