# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.1] - 2026-06-28

### Fixed

- **Startup notices:** Custom-param notices (e.g. missing `client_id`) no longer flash and disappear on initial node-server startup. Removed `Notices.clear()` from startup, unified on `poly.Notices`, and re-sync notices after startup completes.

## [1.3.0] - 2026-06-28

### Added

- **PM measurements ([#24](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/24)):** PM1, PM2.5, and PM10 drivers (`GV7`–`GV9`, µg/m³) parsed from the Airthings consumer API.
- **Mold risk ([#8](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/8)):** Mold risk index driver (`GV10`, 0–10) for devices such as Wave Mini.

### Fixed

- **Rate limit polling:** Skip remaining sensor polls for the current shortPoll cycle when API rate-limit backoff is active.
- **`datetime.now()` typo** in rate-limit wait handling.

### Changed

- **PG3 release Makefile:** `make release`, `make beta`, and `make production` targets (Standard edition zip only).
- Version **1.3.0** — `nodes/__init__.py` **`VERSION`**.

---

## [1.2.7] - 2024-08-15

### Fixed

- **Client limit backoff:** “Wait 5 minutes” now applies correctly after `INVALID_REQUEST_CLIENTS_LIMIT_EXCEEDED`, not only after rate-limit error 1070.

---

## [1.2.6] - 2024-08-14

### Fixed

- **Short poll notice:** Clear the “short poll too small” PG3 notice when the configured interval becomes valid again.

---

## [1.2.5] - 2024-08-13

### Fixed

- **Short poll notice:** Additional logic to clear the “short poll too small” error when conditions improve.

---

## [1.2.4] - 2024-08-11

### Fixed

- **Poll settings persistence:** Restore “Auto Set Short Poll” and “Short Poll” values from the PG3 database on startup.

---

## [1.2.3] - 2024-07-29

### Changed

- **Long poll:** Increase `longPoll` automatically when it is less than `shortPoll`.

---

## [1.2.2] - 2024-07-23

### Fixed

- **Server errors:** Crash after an Airthings API/server error response.

---

## [1.2.1] - 2024-07-20

### Fixed

- **Existing installs:** Set proper initial values for “Auto Set Short Poll” = True on upgrade.

---

## [1.2.0] - 2024-07-20

### Added

- **Short poll control ([#23](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/23)):** Controller drivers “Auto Set Short Poll” (automatic minimum interval from polled sensor count) and “Short Poll” (manual override).

---

## Earlier releases

The following entries were migrated from `README.md` (original wording and dates preserved).

### 1.1.3 - 06/04/2024
- Force pushing values to IoX on manual query
- Don't poll device if authorization fails
- If rate limit is exceeded, wait 5 minutes before polling again

### 1.1.2 - 05/31/2024
- Better tracking of polling device count
- Fix [Do not allow multiple concurrent queries](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/22)

### 1.1.1 - 05/25/2024
- Track Total Sensors, and Sensors actively polled. Uses the later to calculate what the minimum polling time should be.
- Added driver names so they show up on the PG3 Nodes page.

### 1.1.0 - 05/24/2024
- Fix [Add ability to turn off polling for some device](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/21)
- Fix [Add IoX timestamp drive and/or second since update](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/20)
- Fix crash if airthings session is slow to start
- Switch to new PG versioning method

### 1.0.2 - 01/10/2023
- Fix [Fatal error when printing error received](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/17)

### 1.0.1 - 12/12/2022
- Force udi_interface to 3.0.51
- Fix crash on initial startup if not authorized

### 1.0.0 - 12/11/2022
- Been around long enough to be 1.0.0
- Fixed [Crash when trying to print error message](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/15)
- Fixed [Server Status is integer in program reference, should be boolean](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/16)
- Enhancement [Add ability to rename nodes](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/14)
- For [Check why rate limit is being hit](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/13)
  - Add warning and PG3 UI notice if users shortPoll is to low
- Fixed [Send all data on a query](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/12)
- Documented [Confirm what the time value is from Airthings API](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/11)

### 0.0.6 - 07/05/2022
- Fixed [Crash on query](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/6)

### 0.0.5 - 07/04/2022
- Fixed [Can not use nodes in programs](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/5)

### 0.0.4 - 07/04/2022
- Fixed discover which was broken in 0.0.2

### 0.0.2 - 07/04/2022
- Fixed profile errors
- Fixed [Refresh Token bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/4)
- Fixed [Properly trap errors bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/3)
- Fixed [CONFIG doc not being loaded bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/2)
- Fixed [Must restart node server after setting client id and secret bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/1)

### 0.0.1 - 07/03/2022
- Initial release
