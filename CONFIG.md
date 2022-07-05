

# Airthings Consumer Node Server Configuration

## Short Poll

The API is limited to 120 requests per hour as documented on the <a href="https://developer.airthings.com/docs/api-rate-limit-consumer/">Airthing Rate Limit</a>. The short poll time is set 60 seconds so this should not be an issue, but you can increase or decreas as desired.  IF you change the value then you must restart the node server.

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

