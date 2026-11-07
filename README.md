# Eco-Devices integration for Home Assistant

![GitHub release (with filter)](https://img.shields.io/github/v/release/aohzan/ecodevices) ![GitHub](https://img.shields.io/github/license/aohzan/ecodevices) [![Donate](https://img.shields.io/badge/$-support-ff69b4.svg?style=flat)](https://github.com/sponsors/Aohzan) [![Marketplace](https://img.shields.io/badge/Marketplace-Default-41BDF5.svg)](https://www.home-assistant.io/integrations/marketplace/)

This a _custom component_ for [Home Assistant](https://www.home-assistant.io/).
The `ecodevices` integration allows you to get information from [GCE Eco-Devices](http://gce-electronics.com/fr/carte-relais-ethernet-module-rail-din/409-teleinformation-ethernet-ecodevices.html) (/!\ not the RT2).

You will get two sensors by input enabled with all attributes availables.

## Installation

### Marketplace

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=Aohzan&repository=ecodevices&category=integration)

Settings > Marketplace > search for "GCE Eco-Devices" > Install.

### Manually

Copy the `custom_components/ecodevices` folder into the config folder.

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ecodevices)

Or go to Settings > Devices & services > Add integration and select GCE Eco-Devices.

## Example

![[Energy Dashboard]](.readme_content/ecodevices_energy.jpg)
![[Device page]](.readme_content/ecodevices_entities.jpg)
![[Options]](.readme_content/ecodevices_options.jpg)
![[Params]](.readme_content/ecodevices_params.jpg)

## More entities

If you want individual entities for more informations, you can get it from main sensor attributes, for example:

```yaml
template:
  - sensor:
    - name: "Intensité phase 1"
      unique_id: intensity_phase_1
      unit_of_measurement: "A"
      state: "{{ state_attr('sensor.compteur_linky', 'intensite_now_ph1') | int }}"
```
