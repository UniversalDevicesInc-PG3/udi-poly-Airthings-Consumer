# Polyglot V2 ELK Nodeserver

## Important Notices

I am not responsible for any issues related to this nodeserver.

## Help

If you have any issues are questions you can ask on [PG3 AirThings SubForum](https://forum.universal-devices.com/forum/309-airthings/) or report an issue at [PG3 ELK Github issues](https://github.com/UniversalDevicesInc-PG3/udi-poly-Airthings-Consumer/issues).

## Installation

Install from the Polyglot store.

### Configuration

Open the Configuration Page for the Nodeserver in the Polyglot UI and view the [Configuration Help](/POLYGLOT_CONFIG.md) available on that page.

## Requirements

TBD

## Using this Node Server

### General notes

TBD

### Nodes

#### Controller

This has the following status:
- NodeServer Online
  - Nodeserver up and running

#### Sensor Node

TBD

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
- 0.0.0: 06/063033
  - Started
