# Eco-Devices component for Home Assistant
This a *custom component* for [Home Assistant](https://www.home-assistant.io/). 
The `ecodevices` integration allows you to get information from [GCE Eco-Devices](http://gce-electronics.com/fr/carte-relais-ethernet-module-rail-din/409-teleinformation-ethernet-ecodevices.html).

## Sensors

For the teleinfo inputs, you will get an instant consumption sensor.
For the counter inputs, you will get a daily sensor and a total sensor.

## Configuration

### Example
```yaml
# Example configuration.yaml entry
sensor:
  - platform: ecodevices
    host: "192.168.1.239"
    scan_interval: 5
    t1_name: Compteur Linky
    c1_name: Compteur panneau solaire
    c1_icon: mdi:solar-panel
    c1_unit_of_measurement: Wh
    c1_device_class: power
```

### List of configuration parameters
```yaml
{% configuration %}
host:
  description: Hostname or IP address for the Eco-Devices.
  required: true
  type: host
port:
  description: HTTP port for the Eco-Devices.
  required: false
  default: 80
  type: port
t1_name:
  description: Name of the teleinfo 1 input
  required: false
  type: string
t1_unit_of_measurement:
  description: Unit of measurement of the teleinfo 1 input
  required: false
  default: VA
  type: string
t2_name:
  description: Name of the teleinfo 2 input
  required: false
  type: string
t2_unit_of_measurement:
  description: Unit of measurement of the teleinfo 2 input
  required: false
  default: VA
  type: string
c1_name:
  description: Name of the counter 1 input
  required: false
  type: string
c1_unit_of_measurement:
  description: Unit of measurement of the counter 1 input
  required: false
  type: string
c1_device_class:
  description: Device class of the counter 1 input
  required: false
  type: string
c1_icon:
  description: Icon of the counter 1 input
  required: false
  type: string
c2_name:
  description: Name of the counter 2 input
  required: false
  type: string
c2_unit_of_measurement:
  description: Unit of measurement of the counter 2 input
  required: false
  type: string
c2_device_class:
  description: Device class of the counter 2 input
  required: false
  type: string
c2_icon:
  description: Icon of the counter 2 input
  required: false
  type: string
{% endconfiguration %}
```