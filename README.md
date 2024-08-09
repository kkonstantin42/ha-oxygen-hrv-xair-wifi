# Oxygen HRV X-Air Home Assistant Integration

Custom integration for Oxygen Heat Recovery Ventilation (HRV) (https://oxygen.lt/).
Integration can only be used with Oxygen X-Air models 
with [Smart WiFi Controller](https://oxygen.lt/en/produktas/ismanusis-wifi-valdiklis/).

**Note: not compatible with newer Oxygen Easy models**

Disclaimer: this is **not** an official integration and is not maintained by
Oxygen employees. As such compatibility with your HRV is not guaranteed.

## Setup

Integration can be installed using [HACS](https://hacs.xyz/).

* Add this repository as a "Custom repository" in HACS. More details [here](https://hacs.xyz/docs/faq/custom_repositories).
* Restart Home Assistant
* Add "Oxygen HRV X-Air WiFi" integration in Home Assistant Settings menu.
* Popup will appear prompting IP address of your Oxygen WiFi Controller. One way to find the IP address is by checking the 
list of connected devices in the web interface of you router. Look for a device named similar to "ESP-858B8B".
* A new device and a number of entities will be added to the Home Assistant.

## Entities

Integration exposes the following entities:

* Climate (**climate.oxygen_hrv_xair_wifi**) - allows controlling target temperature and flow (aka fan speed) as well as
switching device on and off. Also provides information about the current indoors temperature.
* Fan (**fan.oxygen_hrv_xair_wifi)** - allows controlling flow and switching device on and off. While the same functionality
can also be achieved with the Climate entity, it's sometimes easier to control the Fan entity. E.g. when exposing entities to voice assistant
* Boost Flow (**number.oxygen_hrv_xair_wifi_boost_flow**) - allows setting desired boost flow. Changing this entity on its own does 
not activate the bust. Use switch.oxygen_hrv_xair_wifi_boost_enabled in order to activate boost.
* Boost Time (**number.oxygen_hrv_xair_wifi_boost_time**) - allows setting desired boost time in minutes.
* Boost Enabled (**switch.oxygen_hrv_xair_wifi_boost_enabled**) - allows enabling and disabling boost. Boost will run for the number of minutes
specified in number.oxygen_hrv_xair_wifi_boost_time.



**Work in progress**


