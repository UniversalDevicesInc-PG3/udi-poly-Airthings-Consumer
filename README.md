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
- PM1
  - driver: GV7
  - Particulate matter less than 1 µm (µg/m³)
- PM2.5
  - driver: GV8
  - Particulate matter less than 2.5 µm (µg/m³)
- PM10
  - driver: GV9
  - Particulate matter less than 10 µm (µg/m³)
- Mold Risk
  - driver: GV10
  - Mold risk index from Airthings (0-10)

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

## Changelog

Release notes now live in [`CHANGELOG.md`](CHANGELOG.md).
