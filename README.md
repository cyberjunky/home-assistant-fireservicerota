[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# FireServiceRota / BrandweerRooster Sensor Component
This is a Custom Component for Home-Assistant (https://home-assistant.io) that tracks incidents from BrandweerRooster.nl and FireServiceRota.co.uk

## Disclamer

This is expermimental software **in beta stage**, please read below License before installing it.

<pre>
MIT License

Copyright (c) 2020 Ron Klinkien

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
</pre>

## Installation

- Copy directory `custom_components/fireservicerota` to your `<config dir>/custom_components` directory.
- Restart Home-Assistant.
- Goto Configuration -> Integrations, search for FireServiceRota and complete account data.

NOTE: You need to have an account for BrandweerRooster.nl or FireServiceRota.co.uk which are availability, scheduling and dispatching systems for firefighters.

NOTE: This is still work in progress, some issues and features need to be implemented.

## FireServiceRota / BrandweerRooster Dashboard

This is my experimental config for related sensors, switches etc.

If you want to have your browser to function as audio player, and have screen control you need to install the 'browser_mod' integration (via HACS)

Set the device alias below to match your media player id.

You also need to install the following plugin for lovelace (HACS is again your friend)
- 'custom:layout-card'
- 'custom:bignumber-card'
- 'custom:vertical-stack-in-card'
- 'custom:home-feed-card'

If you have a better layout without/or less custom plugins, please let me know.

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

Example Lovelace Dashboard

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


If you want to cast it to a Nest Hub or other ChromeCast capable device, you need a Nabu Casa subscription or use Catt to Cast.
Home Assistant Cast can be a bit buggy, custom cards or map may stop working sometimes.

Below is the result of above code, an audio player via browser_mod player, screen gets enabled when an incident arrives, and goes dark after 2 minutes. You can toggle TTS and screen display on and off.

I have muted the announcements outside 23:00-6:30h using a automation condition, if you are on duty, that's something to remove.


## Screenshots

![alt text](https://github.com/cyberjunky/home-assistant-brandweerrooster/blob/master/screenshots/bwr-nesthub-dash.png?raw=true "Screenshot BrandweerRooster Dashboard")

My Nest Hub 'at work'

![alt text](https://github.com/cyberjunky/home-assistant-brandweerrooster/blob/master/screenshots/nesthub.jpg?raw=true "Photo Nest Hub at work")


## Debugging
If you experience unexpected behavior please create an GitHub issue.
Post some debug log info or share this privately.
You can obtain this information by adding the following lines to your config and restart homeassistant.


```
logger:
  default: info
  logs:
      custom_components.fireservicerota: debug
      fireservicerota: debug
```
