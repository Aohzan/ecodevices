# Changelog

## 3.0.0

- /!\ Breaking : the total value is now the same that display on Eco-Devices Web UI, and no more multiplied by 1000, watch the unit of measurement which can change (example: Wh => kWh, dm³ => m³)
- Full configuration since options UI
- Add device configuration link

## 2.5.0

- Allow to set a different unit of measurement for counters total sensors (https://github.com/Aohzan/ecodevices/issues/12)
- Don't report 0 for total sensors (https://github.com/Aohzan/ecodevices/issues/13)

## 2.4.0

- Remove name parameters
- Use new sensor properties

## 2.3.1

- Fix total for c1

## 2.3.0

- /!\ Need Home-Assistant version 202109 at least
- Add entities for total
- Add state class property and adjust default classes for Energy dashboard compatibility

## 2.2.0

- Add HACS manifest

## 2.1.0

- Add attributes for teleinfo inputs

## 2.0.0

- Major rewrite: remove old entry and entities before upgrade
- Use updated async api calls
- Add attributes to sensor to get all informations from Eco Devices

## 1.0.0

- Initial release
