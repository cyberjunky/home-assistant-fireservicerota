[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# FireServiceRota / BrandweerRooster integration

NOTE: This code will be released in Home Assistant 1.0, you can try the beta version, or install it via the steps below.

FireServiceRota is a powerful and flexible availability, scheduling and dispatching system for firefighters.
It's the international brand of the Dutch [BrandweerRooster](https://www.brandweerrooster.nl), which is in use by more than 200 fire stations in The Netherlands.

The FireServiceRota integration provides you real-time information about incidents (emergency calls) from your local fire station and the ability to send a response depending on your duty schedule.

You will need a FireServiceRota or BrandweerRooster account.

<div class='note'>

A word of caution: Do not solely rely on this integration for your emergency calls!

</div>

## Installation

- Copy the directory `custom_components/fireservicerota` to your `<config dir>/custom_components` directory.
- Restart Home-Assistant.
- Goto Configuration -> Integrations, search for FireServiceRota and complete account data.


This integration provides the following platforms:

- Sensor: Incoming emergency calls. Metadata contains _among other data_ the location of the incident and a text-to-speech URL. The integration uses a WebSocket client connection with the service to ensure a minimum delay.
- Binary Sensor: Your current duty status (as scheduled via the FireServiceRota mobile app and/or website).
- Switch: Enabled for 30 minutes after an emergency call. ‘on’ represents a confirmed response. Use this to automate your emergency call response and save valuable seconds.

On how to write automations using these platform read the 'Advanced Configuration' section below.

## Configuration

1. From Home Assistant, navigate to ‘Configuration’ then ‘Integrations’. Click the plus icon and type/select ‘FireServiceRota’.
1. Choose your platform `BrandweerRooster` or `FireServiceRota`.
1. Enter your login credentials.

1. Click the Save button.

## Entities

The following entity types are created:

### Incidents Sensor

This is the main entity of the integration containing the incident message as it's `value`, it has several attributes which are described below.

| Attribute | Description |
| --------- | ----------- |
| `trigger` | Type of trigger, `new` or `update`.|
| `state` | The state of the incident. |
| `created_at` | Date and time when incident was created.|
| `message_to_speech_url` | The URL of the mp3 file containing the spoken text of the incident.|
| `prio` | Priority of the incident, `a1`, `a2`, `b1` or `b2`.|
| `type` | Type of incident, e.g. `incident_alert`.|
| `responder_mode` | Modes of response, e.g. `available_in_schedule_is_acknowledgment`.|
| `can_respond_until` | Date and time until response is accepted.|
| `latitude` | The Latitude of the incident.|
| `longitude` | The Longitude of the incident.|
| `address_type` | Type of address, e.g. `home`.|
| `formatted_address` | Address in string format.|

### Duty Binary Sensor

This entity reflects the duty you have scheduled, the value can be `on` = on duty, `off` = no duty. When you have no duty the response switch is disabled which means you cannot respond to a call.

| Attribute | Description |
| --------- | ----------- |
| `start_time` | Start date and time of duty schedule.|
| `end_time` | End date and time of duty schedule.|
| `available` | `true` or `false`.|
| `active` | `true` or `false`.|
| `assigned_function_ids` | Function id's, e.g. `540`.|
| `skill_ids` | Skill id's, e.g. `6, 8`.|
| `type` | Type, e.g. `standby_duty`.|
| `assigned function` | Assigned function, e.g. `Chauffeur`.|

### Incident Response Switch

With this switch you can respond to a incident, either by manually controlling the switch via the GUI, or by using an automation action.
It gets reset to `unknown` value with every incident received. Switching it to `on` means you send a response acknowledgement, switching it back `off` sends a response rejected.

The following attributes are available:

| Attribute | Description |
| --------- | ----------- |
| `user_name` | Your username.|
| `assigned_skill_ids` | Assigned skill ID's.|
| `responded_at` | Time you responded.|
| `start_time` | Incident response start time.|
| `status` | Status of response, e.g., `pending`.|
| `reported_status` | Reported status, e.g., `shown_up`.|
| `arrived_at_station` | `true` or `false`.|
| `available_at_incident_creation` | `true` or `false`.|
| `active_duty_function_ids` | Active function ID's, e.g., `540`.|

## Advanced Configuration

With Automation you can configure one or more of the following useful actions:

1. Sound an alarm and/or switch on lights when an emergency incident is received.
1. Use text to speech to play incident details via a media player while getting dressed.
1. Respond with a response acknowledgment using a door-sensor when leaving the house or by pressing a button to let your teammates know you are underway.
1. Cast a FireServiceRota dashboard to a Chromecast device. (this requires a Nabu Casa subscription)

These are documented below.

### Example Automation

```yaml
automation:
  - alias: 'Switch on a light when incident is received'
    trigger:
      platform: state
      entity_id: sensor.incidents
    action:
      service: light.turn_on
      entity_id: light.bedroom

  - alias: 'Play TTS incident details when incident is received'
    trigger:
      platform: state
      entity_id: sensor.incidents
      attribute: message_to_speech_url
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: sensor.incidents
            attribute: message_to_speech_url
            state: None
    action:
      - service: media_player.play_media
        data_template:
          entity_id: media_player.nest_hub_bedroom
          media_content_id: >
              {{ state_attr('sensor.incidents','message_to_speech_url') }}
          media_content_type: 'audio/mp4'

  - alias: 'Send response acknowledgement when a button is pressed'
    trigger:
      platform: state
      entity_id: switch.response_button
    action:
      service: homeassistant.turn_on
      entity_id: switch.incident_response

  - alias: 'Cast FireServiceRota dashboard to Nest Hub'
    trigger: 
      platform: homeassistant
      event: start
    action:
      service: cast.show_lovelace_view
      data: 
        entity_id: media_player.nest_hub_bedroom
        view_path: fsr
```


### Example Lovelace Dashboard

Without custom frontend components:

```yaml
panel: true
title: Home
views:
  - badges: []
    cards:
      - entity: sensor.incidents
        type: entity
      - cards:
          - cards:
              - default_zoom: 15
                entities:
                  - entity: sensor.incidents
                hours_to_show: 0
                type: map
            type: vertical-stack
          - cards:
              - entities:
                  - entity: sensor.incidents
                hours_to_show: 1
                refresh_interval: 0
                type: history-graph
            type: vertical-stack
        type: horizontal-stack
      - content: |
          {{ states('sensor.incidents') }}
        title: Incident
        type: markdown
      - entities:
          - entity: binary_sensor.duty
          - entity: switch.incident_response
        type: entities
    path: fsr
    title: FireServiceRota
    type: horizontal-stack
```

With custom components and frontend items:

If you want to have your browser to function as audio player, and have screen control you need to install the 'browser_mod' integration (via HACS)

Set the device alias below to match your media player id.

You also need to install the following plugin for lovelace (HACS is again your friend)
- 'custom:layout-card'
- 'custom:bignumber-card'
- 'custom:vertical-stack-in-card'
- 'custom:home-feed-card'

If you have a better layout without/or less custom plugins, please let me know.

If you want to cast it to a Nest Hub or other ChromeCast capable device, you need a Nabu Casa subscription or use Catt to Cast.
Home Assistant Cast can be a bit buggy, custom cards or map may stop working sometimes.

Below is the result of above code, an audio player via browser_mod player, screen gets enabled when an incident arrives, and goes dark after 2 minutes. You can toggle TTS and screen display on and off.

I have muted the announcements outside 23:00-6:30h using a automation condition, if you are on duty, that's something to remove.

### Example Automation with custom components

```
browser_mod:
  devices:
    3184e47f_bac9b576:  # <--- change this
      name: bwr-nesthub

sensor:
  - platform: template
    sensors:
      incidents_speech:
        value_template: "{{ state_attr('sensor.incidents', 'message_to_speech_url') }}"
        friendly_name: "Speech Sensor"

input_boolean:
  bwr_tts:
    name: Text to Speech
    icon: mdi:text-to-speech

homeassistant:
  customize:
    light.bwr_nesthub:
      friendly_name: 'Display On/Off'

automation:
  - alias: Play Incident Speech
    trigger:
      platform: state
      entity_id: sensor.incidents
    action:
      - service: media_player.play_media
        data_template:
          entity_id: media_player.bwr_nesthub
          media_content_id: >
            {{ states('sensor.incidents_speech') }}
          media_content_type: 'audio/mp4'
      - service: homeassistant.turn_on
        data_template: 
          entity_id: >
              light.bwr_nesthub
      - service: timer.start
        data:
          entity_id: timer.bwr_nesthub
    condition:
      condition: and
      conditions:
      - condition: time
        after: '06:30:00'
        before: '23:00:00'
      - condition: template
        value_template: "{{ not is_state('sensor.incidents_speech', 'None') }}"
      - condition: state
        entity_id: input_boolean.bwr_tts
        state: 'on'

  - alias: Turn off Nest Hub screen 2 minutes after trigger
    trigger:
      platform: event
      event_type: timer.finished
      event_data:
        entity_id: timer.bwr_nesthub
    action:
      service: light.turn_off
      data:
        entity_id:
          - light.bwr_nesthub

  - alias: Cast to Nest Hub
    trigger: 
      platform: homeassistant
      event: start
    action:
      service: cast.show_lovelace_view
      data: 
        entity_id: media_player.nest_hub_slaapkamer
        view_path: bwr

timer:
  bwr_nesthub:
    duration: '00:02:00'
    name: Nest Hub Screen Timer
```

### Example Lovelace Dashboard with custom components

```
title: BWR
path: bwr
panel: true
icon: mdi:fire-truck
cards:
  - type: 'custom:layout-card'
    cards:
      - type: 'custom:bignumber-card'
        entity: sensor.incidents
        scale: 15px
      - type: map
        entities:
          - entity: sensor.incidents
        hours_to_show: 0
        default_zoom: 15
      - type: 'custom:vertical-stack-in-card'
        cards:
          - type: history-graph
            entities:
              - entity: sensor.incidents
            hours_to_show: 1
            refresh_interval: 0
          - type: 'custom:home-feed-card'
            show_empty: false
            entities:
              - entity: sensor.incidents
                max_history: 3
                include_history: true
          - type: entities
            show_header_toggle: false
            entities:
              - input_boolean.bwr_tts
              - light.bwr_nesthub
          - type: 'custom:bignumber-card'
            entity: sensor.time
            scale: 25px
```



### Screenshots

This screenshot shows what a FireServiceRota dashboard can look like.

![alt text](https://github.com/cyberjunky/home-assistant-brandweerrooster/blob/master/screenshots/bwr-nesthub-dash.png?raw=true "Screenshot BrandweerRooster Dashboard")

My Nest Hub 'at work'.

![alt text](https://github.com/cyberjunky/home-assistant-brandweerrooster/blob/master/screenshots/nesthub.jpg?raw=true "Photo Nest Hub at work")

## Debugging

The FireServiceRota integration will log additional information about WebSocket incidents received, response and duty status gathered, and other messages when the log level is set to `debug`. Add the relevant lines below to the `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    homeassistant.components.fireservicerota: debug
    pyfireservicerota: debug
```
