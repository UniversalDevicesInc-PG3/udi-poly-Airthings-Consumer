# Polyglot V3 Airthings Nodeserver

## Important Notices

I am not responsible for any issues related to this nodeserver.

## Help

If you have any issues are questions you can ask on [PG3 AirThings SubForum](https://forum.universal-devices.com/forum/309-airthings/) or report an issue at [PG3 Airthings Consumer Github issues](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues).

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
  - Nodeserver up and running
- Sensor Count

#### Sensor Node

TBD

https://www.airthings.com/what-is-voc
https://help.airthings.com/en/collections/2683690-understanding-radon-and-iaq#vocs

## Using the Nodeserver

Following are examples have usages for this nodeserver.

### Notifications

TBD, update to this nodeservers drivers...

To include any information about a Zone in a notification you can use any if these drivers:
```
Area: ${sys.node.n004_area_1.name}
 Alarm Status:        ${sys.node.n004_area_1.ST}
 Armed Status:        ${sys.node.n004_area_1.GV0}
 Arm Up State:        ${sys.node.n004_area_1.GV1}
 Last Violated Zone:  ${sys.node.n004_area_1.GV8}
 Last Triggered Zone: ${sys.node.n004_area_1.GV9}
 Chime Mode:          ${sys.node.n004_area_1.GV2}
 Zones Violated:      ${sys.node.n004_area_1.GV3}
 Zones Bypassed:      ${sys.node.n004_area_1.GV4}
 Last user:           ${sys.node.n004_area_1.GV6}
 Last Keypad:         ${sys.node.n004_area_1.GV7}

${sys.node.n004_zone_1.name} ${sys.node.n004_zone_1.status}
${sys.node.n004_zone_2.name} ${sys.node.n004_zone_2.status}
...
```

## TODO and issues

https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues

## Release Notes
- 0.0.2: 07/04/2022
  - Fixed profile errors
- 0.0.1: 07/03/2022
  - Initial release

