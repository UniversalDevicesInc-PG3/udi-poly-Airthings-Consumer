# Polyglot V3 Airthings Nodeserver

## Important Notices

I am not responsible for any issues related to this nodeserver.

## Help

If you have any issues are questions you can ask on [PG3 AirThings-C SubForum](https://forum.universal-devices.com/forum/385-airthings-c/) or report an issue at [PG3 Airthings Consumer Github issues](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues).

## Installation

Install from the Polyglot store.

### Configuration

Open the Configuration Page for the Nodeserver in the Polyglot UI and view the [Configuration Help](/CONFIG.md) available on that page.

## Requirements

This supports consumer devices from <a href="https://www.airthings.com/">Airthings</a>.  It has only been tested with a Wave Plus device, but is currently built in a generic way to support any sensor.  But, if that sensor doesn't support everything the Wave Plus does then you will see those drivers with empty values.  I will work on resolving this withough requiring customizing the interface for each device.

## Using this Node Server

### General notes

### Nodes

#### Controller

This has the following status:
- NodeServer Online
  - Nodeserver up and running, this is managed by PG3 and will be Disconnected, Connected, or Failed
- Authroized
  - If the Authorization to the Airthings Servics is currently valid
- Server Status
  - If the last connection to Airthing Server was successful, if there is a communcation problem to their service this will go False, or one of the other known error values, and when service is restored it will go back to True.
- Sensors
  - The number of Airthings devices

#### Sensor Node

This node has the following status

##### Status

- Active
  - driver: ST
  - The device is currently active
- Poll Device
  - driver: GV6
  - Enable/Disable polling of sensor
- Battery Level
  - driver: BATLVL
  - The battery level percentage
- C02 Level
  - driver: CO2LVL
  - The CO2 level
- Humidity
  - driver: CLIHUM
  - The Humidity level
- Barometric Pressure
  - driver: BARPRES
  - The Barometric Pressure
- Radon
  - driver: GV1
  - The Radon level https://help.airthings.com/en/collections/2683690-understanding-radon-and-iaq#vocs
- RSSI
  - driver: GV3
  - The RSSI level
- Temperature
  - driver: CLITEMP
  - The Temperature
- Time
  - driver: GV2
  - The time of device measurment, epoch value which is not currently useful in the ISY except to watch it change
- Seconds Since Update
  - driver: GV5
  - Number of seconds since the device reported.  This is based on the timestamp returned by the Airthings API in relation to the time on the local machine.
- VOC
  - driver: GV4
  - The VOC measurement https://www.airthings.com/what-is-voc
- VOC Level
  - driver: VOCLVL
  - The text description of the VOC

##### Commands

- Set Poll Device
  - Enable or disable polling of this device

## Using the Nodeserver

Following are examples have usages for this nodeserver.

### Notifications

To include any information about a Sensor in a notification you can use any if these drivers:
```
Sensor: ${sys.node.n004_s_2930020110.name}
 Active:              ${sys.node.n004_s_2930020110.ST}
 Battery:             ${sys.node.n004_s_2930020110.BATLVL}
 Temperature:         ${sys.node.n004_s_2930020110.CLITEMP}
 ...
```
and of course if the notification is triggered by a program from a change in the sensor just replace 'n004_s_2930020110' with '#'.

## TODO and issues

https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues

## Release Notes
- 1.2.2: 07/23/2024
  - Fix crash after Airthings server error
- 1.2.1: 07/20/2024
  - Try to set proper initial values on existing installs for Auto Short Poll = True
- 1.2.0: 07/20/2024
  - [Add driver for short poll interval](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/23)
  New Feature: The Controller has "Auto Set Short Poll" which will automatically set the short poll to the minimum value.  If disabled, you can manually set it with the driver "Short Poll" on the controller.
- 1.1.3: 06/04/2024
  - Force pushing values to IoX on manual query
  - Don't poll device if authorization fails
  - If rate limit is exceeded, wait 5 minutes before polling again
- 1.1.2: 05/31/2024
  - Better tracking of polling device count
  - Fix [Do not allow multiple concurrent queries](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/22)
- 1.1.1: 05/25/2024
  - Track Total Sensors, and Sensors actively polled.  Uses the later to calculate what the minimum polling time should be.
  - Added driver names so they show up on the PG3 Nodes page.
- 1.1.0: 05/24/2024
  - Fix [Add ability to turn off polling for some device](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/21)
  - Fix [Add IoX timestamp drive and/or second since update](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/20)
  - Fix crash if airthings session is slow to start
  - Switch to new PG versioning method
- 1.0.2: 01/10/2023
  - Fix [Fatal error when printing error received](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/17)
- 1.0.1: 12/12/2022
  - Force udi_interface to 3.0.51
  - Fix crash on initial startup if not authorized
- 1.0.0: 12/11/2022
  Been around long enough to be 1.0.0
  - Fixed [Crash when trying to print error message](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/15)
  - Fixed [Server Status is integer in program reference, should be boolean](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/16)
  - Enhancement [Add ability to rename nodes](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/14)
  - For [Check why rate limit is being hit](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/13)
    - Add warning and PG3 UI notice if users shortPoll is to low
  - Fixed [Send all data on a query](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/12)
  - Documented [Confirm what the time value is from Airthings API](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/11)
- 0.0.6: 07/05/2022
  - Fixed [Crash on query](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/6)
- 0.0.5: 07/04/2022
  - Fixed [Can not use nodes in programs](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/5)
- 0.0.4: 07/04/2022
  - Fixed discover which was broken in 0.0.2
- 0.0.2: 07/04/2022
  - Fixed profile errors
  - Fixed [Refresh Token bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/4)
  - Fixed [Properly trap errors bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/3)
  - Fixed [CONFIG doc not being loaded bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/2)
  - Fixed [Must restart node server after setting client id and secret bug](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues/1)
- 0.0.1: 07/03/2022
  - Initial release
