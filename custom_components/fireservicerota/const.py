"""Constants for the BrandweerRooster integration."""

DOMAIN = "brandweerrooster"

OAUTH2_TOKENURL = "https://{0}/oauth/token"
WSS_BWRURL = "wss://{0}/cable?access_token={1}"
URL_LIST = ["www.brandweerrooster.nl", "www.fireservicerota.co.uk"]

ATTRIBUTION = "Data provided by brandweerrooster.nl"

SENSOR_ENTITY_LIST = {
    "incidents": ["Incidents", "", "mdi:fire-truck", None, True],
}

SIGNAL_UPDATE_INCIDENTS = "bwr_incidents_update"
