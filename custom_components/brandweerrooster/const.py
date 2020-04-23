"""Constants for the BrandweerRooster integration."""

DOMAIN = "brandweerrooster"

OAUTH2_TOKENURL = "https://www.brandweerrooster.nl/oauth/token"
WSS_BWRURL = "wss://www.brandweerrooster.nl/cable?access_token="

ATTRIBUTION = "Data provided by brandweerrooster.nl"

SENSOR_ENTITY_LIST = {
    "incidents": ["Incidents", "", "mdi:fire-truck", None, True],
}

SIGNAL_UPDATE_INCIDENTS = "bwr_incidents_update"