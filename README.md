# Eco-Devices integration for Home Assistant

This a _custom component_ for [Home Assistant](https://www.home-assistant.io/).
The `ecodevices` integration allows you to get information from [GCE Eco-Devices](http://gce-electronics.com/fr/carte-relais-ethernet-module-rail-din/409-teleinformation-ethernet-ecodevices.html) (/!\ not the RT2).

You will get two sensors by input enabled with all attributes availables.

## Installation

### HACS

HACS > Integrations > Explore & Add Repositories > GCE Eco-Devices > Install this repository

### Manually

Copy the `custom_components/ecodevices` folder into the config folder.

## Configuration

To add ecodevices to your installation, go to Configuration >> Integrations in the UI, click the button with + sign and from the list of integrations select GCE Eco-Devices.

## Example

![[Energy Dashboard]](.readme_content/ecodevices_energy.jpg)
![[Device page]](.readme_content/ecodevices_entities.jpg)
![[Options]](.readme_content/ecodevices_options.jpg)
![[Params]](.readme_content/ecodevices_params.jpg)
