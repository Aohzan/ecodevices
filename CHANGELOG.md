# Changelog

## [5.4.0](https://github.com/Aohzan/ecodevices/compare/5.3.1...5.4.0) (2025-04-23)

### Features

* add release ([ee5345c](https://github.com/Aohzan/ecodevices/commit/ee5345c3aa510857331082169ecd66885bd8e338))

## 5.3.1

* Fix error when last state was unavailable

## 5.3.0

* Fix deprecations
* Bump pyecodevices

## 5.2.0

* Compare total sensors with previous value when possible to avoid wrong values

## 5.1.0

* Add binary sensor in Tempo and HCHP modes to know if currently in HC or not
* Add sensor in Tempo mode to know today and tomorrow colors
* Teleinfo instant power is now in VA instead of W
* Remove warning message for HCHP and Tempo total entity when equal to 0

## 5.0.0

* Add Tempo support
* Add Teleinfo type input: `base`, `hchp` or `tempo` (automatic migration during upgrade)

## 4.8.0

* Add divider factor for both meters to allow user to choose a compatible unit of measurement (example, m³ for gas instead of dm³ with a divider factor of 1000)
* Update translation

## 4.7.0

* add some teleinfo attributes: `Avertissement depassement`, `Conso instant general`, `Puissance apparente`
* code enhancement
* bump dependencies

## 4.6.1

* fix DeviceInfo for HA 2023.8 release

## 4.6.0

* bump pyecodevices (force xml encoding)

## 4.5.0

* fix T2 attributes
* do not raise error when total value not greater than 0, just warning message

## 4.4.0

* Add `type_heures_demain` info on teleinfo inputs

## 4.3.2

* Fix coordinator data keys

## 4.3.1

* Fix values assignments

## 4.3.0

* Add support of teleinfo "jours bleu,blanc,rouge"
* Fix deprecation types and various improvments

## 4.2.2

* Remove wrong old code

## 4.2.1

* Fix incrementation

## 4.2.0

* Replace deprecated async_get_registry method

## 4.1.0

* Add instant entity for counters

## 4.0.0

* You have to delete the integration before upgrade, and make installation again
* Handle multiple Eco-Device on the same hostname but different port
* Change default teleinfo unit from `VA` to `W`
* Change entity and device unique id

## 3.1.0

* Add HC/HP maangements for teleinfo inputs
* Set static units for teleinfo inputs
* Code improvments

## 3.0.2

* Fix empty dict in config flow

## 3.0.1

* Fix optional keys error in config flow

## 3.0.0

* /!\ Need Home-Assistant version 202111 at least
* /!\ Breaking : the total value is now the same that display on Eco-Devices Web UI, and no more multiplied by 1000, watch the unit of measurement which can change (example: Wh => kWh, dm³ => m³)
* Full configuration since options UI
* Add device configuration link

## 2.5.0

* Allow to set a different unit of measurement for counters total sensors [issue#12](https://github.com/Aohzan/ecodevices/issues/12)
* Don't report 0 for total sensors [issue#13](https://github.com/Aohzan/ecodevices/issues/13)

## 2.4.0

* Remove name parameters
* Use new sensor properties

## 2.3.1

* Fix total for c1

## 2.3.0

* /!\ Need Home-Assistant version 202109 at least
* Add entities for total
* Add state class property and adjust default classes for Energy dashboard compatibility

## 2.2.0

* Add HACS manifest

## 2.1.0

* Add attributes for teleinfo inputs

## 2.0.0

* Major rewrite: remove old entry and entities before upgrade
* Use updated async api calls
* Add attributes to sensor to get all informations from Eco Devices

## 1.0.0

* Initial release
