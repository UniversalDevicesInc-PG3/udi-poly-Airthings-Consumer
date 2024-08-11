

# Airthings Consumer Node Server Configuration

## Short Poll

The API is limited to 120 requests per hour as documented on the <a href="https://developer.airthings.com/docs/api-rate-limit-consumer/">Airthings Rate Limit</a>. The default short poll time is set 60 seconds which will be ok if you have 1 or 2 sensors, but you have more then you must increase it to 30 x number of sensors.  IF you change the value then you must restart the node server.

New Feature: The Controller has "Auto Set Short Poll" which will automatically set the short poll to the minimum value.  The minimum calculated value is 33 * num_sensors, really it should just be 30 * num_sensors but I found a small fudge factore is needed.   If disabled, you can manually set it with the driver "Short Poll" on the controller.  But if disabled, the current version of PG3X will reset
this to the default of 60 each time you install and update.  Hopefully that will be fixed soon. In the meantime I have added functionality that should keep the proper value for Auto Short Poll, and Short Poll as long as you set your short poll through IoX and not PG3 UI.

## Long Poll

A heartbeat is sent on each long poll.  TODO: Add link to monitoring heartbeat

## Custom Params

You must create a client on the <a href="https://dashboard.airthings.com/integrations/api-integration">Airthings API Integration</a>  Name it whatever you want and make sure to check the box next to "read:device:current_values".  The only option for Flow Type on consumer products is machine-to-machine.

### client_id

The client_id from your app

### client_secret

The client_secret from your app

### units

Set to US or Metric

### change_node_names

Set to true if you want the node names in PG3 and the ISY to always be changed to match the names of devices in the Airthings app when they are changed.  This is on done on node server startup.


