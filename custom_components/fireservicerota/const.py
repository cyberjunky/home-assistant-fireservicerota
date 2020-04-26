"""Constants for the FireServiceRota integration."""

DOMAIN = "fireservicerota"

OAUTH2_TOKENURL = "https://{0}/oauth/token"
WSS_BWRURL = "wss://{0}/cable?access_token={1}"
URL_LIST = ["www.brandweerrooster.nl", "www.fireservicerota.co.uk"]

ATTRIBUTION = "Data provided by FireServiceRota"

SENSOR_ENTITY_LIST = {
    "incidents": ["Incidents", "", "mdi:fire-truck", None, True],
}

SIGNAL_UPDATE_INCIDENTS = "fsr_incidents_update"