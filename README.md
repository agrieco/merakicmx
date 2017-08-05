# merakicmx
Meraki CMX API device tracker for Home Assistant

# Description
This is an early version of a device tracker that uses Meraki's CMX API to track devices.

# How it works
The Meraki CMX API issues HTTP(s) POSTs to a URL of your chosing with all of the location data it has included in those HTTP posts per their documentation (http://developers.meraki.com/tagged/Scanning).   This includeds both WIFI and Bluetooh Low Energy devices.  

This code uses the Home Assistant device_tracker infrastructure to create a server for the REST POSTS to go and get processed and turned into devices being tracked within Home Assistant. 

This code only supports v2 of the CMX API.

# SECURITY
* Meraki does a good job with privacy in thier processing of the analytics data and representation of that data via the API.  That means that the best you will see from the Meraki CMX that uniquely idenitify a devices are a Unique MAC address.  You don't see pretty host names, etc.  You have to do that mapping in Home Assistant if you want.

* Meraki will send the REST calls over HTTPS or HTTP.  _USE HTTPS_.  PLEASE.  If you don't, your devices locations will be flying around the internet unencrypted, and or may or may not be going to a legit server in the middle. This requires you to setup HTTPS within Home Assistant and I would also encourage API Keys as well.  

# Prereqs
* This isn't ready for primetime and might not ever be if no one cares...so please only use if you have experience w/ HomeAssistant.
* Your Homeassistant Install must be accessable from the internet.  This can be done a number of ways- Port forwarding, DMZs, etc- but you need to expose the API interface of Home Assistant to the internet. 

# Setup

1. Grab merakicmx.py from github
2. Put it in the 'device_tracker' 'custom components' location appropriate for your install.  For mine it was: `/home/homeassistant/.homeassistant/custom_components/device_tracker`.
3. Configure access to the Meraki CMX API as per the following directions: https://meraki.cisco.com/technologies/location-analytics-api
3.1.  As you configure the URL for the POSTs to go through, you'll need to take care to add http(s) as configure as well as any Home Asssistant API password to the Meraki configuration (e.g. https://<blah.com>:8123/api/meraki?api_password=<yourHassAPIpassword>)
Note:  The API enpoint will always be /api/meraki 
4. Take the 'secret' and the 'validator' assocaited with this configuration and use it in the homeassistant configuration (configuration.yaml or wherever you've included for device trackers) as follows:

`
device_tracker:
 - platform: merakicmx
   secret: <insert your secret here>
   validator: <insert your validator here>
`
5.  Restart your homeassistant install
6.  Go back to the Meraki CMX API setup page and "validate" the URL provided.

At this point, you should see devices be brought onto the HASS web interface as the POST requests roll in.

# Troubleshooting

From the internet, if you can't type in the URL you put into the Meraki POST configuration and get back your 'validator', you have a setup problem on the HASS/Networking side.  Fix it.  This won't work until it shows you the validator.

# TODO

1.  Need to manage the devices more actively throught the API- as they come and go.  
2.  Document the code better
3.  If anyone cares, commit this to HASS upstream.
