[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# BrandweerRooster Sensor Component
This is a Custom Component for Home-Assistant (https://home-assistant.io) that tracks incidents from BrandweerRooster.nl

## Installation

- Copy directory `custom_components/brandweerrooster` to your `<config dir>/custom_components` directory.
- Restart Home-Assistant.
- Goto Configuration -> Integrations, search for and add BrandweerRooster.

NOTE: You need for account for BrandweerRooster.nl which is an availability, scheduling and dispatching system for firefighters.

NOTE: This is still work in progress, some issues and features need to be implemented.

TODO:
- Update entities in realtime (force device state update)
- Handle Oauth token refresh
- Reconnect websocket when connection is dropped
