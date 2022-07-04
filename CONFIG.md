

# Airthings Consumer Node Server Configuration

## Short Poll

The API is limited to 120 requests per hour per the <a href="https://developer.airthings.com/docs/api-rate-limit-consumer/">Airthing Rate Limit</a>. So short poll time is set 30 seconds which is 120 times and hour.  To reduce traffic to your ISY you can increase the short poll time in the configuration and restart the node server.

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

