# Changelog

## [5.6.0](https://github.com/Aohzan/ecodevices/compare/5.5.1...5.6.0) (2026-10-27)

### Features

* modernize the integration for Home Assistant 2026.10 ([ee5e6dd](https://github.com/Aohzan/ecodevices/commit/ee5e6dd1c586effd434ccf0ff735f74babbaff27))

### Bug Fixes

* accept a lower total once it's confirmed on 3 updates ([9501be3](https://github.com/Aohzan/ecodevices/commit/9501be31810cf031a1504f361ffddadbd1a6a151))
* **deps:** bump pyecodevices to 1.7.1 ([2c5c810](https://github.com/Aohzan/ecodevices/commit/2c5c810037861708433a534315eac0a1b550e932))
* **deps:** bump pyecodevices to 1.7.2 ([04d528a](https://github.com/Aohzan/ecodevices/commit/04d528a479913c0d32246e7929f163cea8dd8408))
* read the Tempo color of tomorrow from the values of DEMAIN ([5e500b3](https://github.com/Aohzan/ecodevices/commit/5e500b36c108c5c300628b440c0cd7fc7e663664))
* redact the MAC address in the diagnostics ([d835036](https://github.com/Aohzan/ecodevices/commit/d83503626d8b3625ffa1f05059e2e2f85c0e6c74))
* refuse to reconfigure the entry with another Eco-Devices ([1814b45](https://github.com/Aohzan/ecodevices/commit/1814b456e9d4e1dc7fe5ed372b4de5657f3d26c0))
* remove the off-peak binary sensor of an input with the base rate ([8fa4cfb](https://github.com/Aohzan/ecodevices/commit/8fa4cfba6aa7e4c5855131bebb7de3425c359603))
* use the unit of the meter when the unit of its total is cleared ([213b797](https://github.com/Aohzan/ecodevices/commit/213b797e2113ed68f360fcfbf11a0981542ec658))

## [5.5.1](https://github.com/Aohzan/ecodevices/compare/5.5.0...5.5.1) (2026-10-27)

### Bug Fixes

* **config_flow:** allow clearing optional fields and default divider factor ([eca0efc](https://github.com/Aohzan/ecodevices/commit/eca0efcbfa1d9bb2bb55250795ebbad1fff9b3a5))
* **options:** allow empty username/password in options flow ([7dd2a28](https://github.com/Aohzan/ecodevices/commit/7dd2a2817fa978248d326ba03c4aa85d1f80bbd9))

## [5.5.0](https://github.com/Aohzan/ecodevices/compare/5.4.2...5.5.0) (2026-10-20)

### Features

* add local brand assets ([f211a8b](https://github.com/Aohzan/ecodevices/commit/f211a8b216e1a3bc37446670021b93613d2dfbb7))

## [5.4.2](https://github.com/Aohzan/ecodevices/compare/5.4.1...5.4.2) (2026-10-03)

### Bug Fixes

* bump xmltodict to 1.0.4 for HA compatibility ([11c94ed](https://github.com/Aohzan/ecodevices/commit/11c94ed2e7c569a8045e7cba445dfa7d6a89245b))
* use minimum version for xmltodict requirement ([374b774](https://github.com/Aohzan/ecodevices/commit/374b774b42caa11e2e20d11c96c30db4199d43e1))

## [5.4.1](https://github.com/Aohzan/ecodevices/compare/5.4.0...5.4.1) (2026-01-30)

### Bug Fixes

* new error when opening option configflow ([7a7250d](https://github.com/Aohzan/ecodevices/commit/7a7250d26b7a798121e53eb0c348725321575028))
* new error when opening option configflow ([2d01e1b](https://github.com/Aohzan/ecodevices/commit/2d01e1b3e4cabbeb19e5b53b4cb30d670560091c))

## [5.4.0](https://github.com/Aohzan/ecodevices/compare/5.3.1...5.4.0) (2025-09-05)

### Features

* add release ([ee5345c](https://github.com/Aohzan/ecodevices/commit/ee5345c3aa510857331082169ecd66885bd8e338))

### Bug Fixes

* use SensorDeviceClass.APPARENT_POWER for teleinfo instant sensor ([5eede19](https://github.com/Aohzan/ecodevices/commit/5eede1938e38d736262959b995201f74ff19ea70))

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
