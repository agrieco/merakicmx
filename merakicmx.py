"""
Support for the Meraki CMX location service.

For more details about this platform, please refer to the documentation at

"""
import asyncio
from functools import partial
import logging
import json

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import HTTP_UNPROCESSABLE_ENTITY
from homeassistant.components.http import HomeAssistantView
# pylint: disable=unused-import
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA)

#from homeassistant.const import CONF_VALIDATOR, CONF_SECRET
CONF_VALIDATOR='validator'
CONF_SECRET='secret'

VERSION='2.0'


_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['http']
URL = '/api/meraki'
CONF_VALIDATOR='validator'
CONF_SECRET='secret'

PLATFORM_SCHEMA = vol.All(
    PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
        vol.Required(CONF_VALIDATOR): cv.string,
        vol.Required(CONF_SECRET): cv.string
    })
)



def setup_scanner(hass, config, see, discovery_info=None):
    """Set up an endpoint for the Locative application."""
    hass.http.register_view(MerakiView(config,see))

    return True


class MerakiView(HomeAssistantView):
    """View to handle Meraki requests."""

    url = URL
    name = 'api:meraki'

    def __init__(self, config,see):
        """Initialize Locative URL endpoints."""
        self.see = see
        self.validator = config[CONF_VALIDATOR]
        self.secret = config[CONF_SECRET]

    @asyncio.coroutine
    def get(self, request):
        """Meraki message received as GET. """
        _LOGGER.info("Merakicmx message received as a GET")
        _LOGGER.debug("Request: %s",request.text)
        return self.validator

    @asyncio.coroutine
    def post(self, request):
        """Meraki CMX message received."""
        try:
            data = yield from request.json()
        except ValueError:
            return self.json_message('Invalid JSON', HTTP_BAD_REQUEST)
#        data = yield from request.post()
        _LOGGER.debug("Meraki Data from Post: %s",json.dumps(data))
        if 'secret' not in data:
            _LOGGER.error("secret invalid")
            return("No secret",HTTP_UNPROCESSABLE_ENTITY)
        else:
            if data['secret'] != self.secret:
                _LOGGER.error("Invalid Secret received from Meraki")
            elif data['version'] != VERSION:
                _LOGGER.error("Invalid API version received: %s", data['version'])
            else:
                _LOGGER.debug('Valid Secret')
                if data['type'] == "DevicesSeen":
                    _LOGGER.debug("WiFi Devices Seen")
                elif data['type'] == "BluetoothDevicesSeen":
                    _LOGGER.debug("Bluetooth Devices Seen")
                else:
                    _LOGGER.error("Unknown Device %s",type)
                    return('invalid device type',HTTP_UNPROCESSABLE_ENTITY)
        res = yield from self._handle(request.app['hass'], data)
        return res

    @asyncio.coroutine
    def _handle(self, hass, data):
        if len(data["data"]["observations"]) == 0:
            _LOGGER.debug("No observations found")
        else:
            for i in data["data"]["observations"]:
                _LOGGER.debug("Raw observation data: %s",i)
                data["data"]["secret"] = "hidden"
                lat = i["location"]["lat"]
                lng = i["location"]["lng"]
                accuracy = int(float(i["location"]["unc"]))

                clientMac = i["clientMac"]
                _LOGGER.debug("clientMac: %s",clientMac)
                gps_location = (lat,lng)
                attrs = {}
                if 'os' in i:
                    attrs['os'] = i['os']
                if 'manufacturer' in i:
                    attrs['manufacturer'] = i['manufacturer']
                if 'ipv4' in i:
                    attrs['ipv4']=i['ipv4']
                if 'ipv6' in i:
                    attrs['ipv6']=i['ipv6']
                if 'seenTime' in i:
                    attrs['seenTime']=i['seenTime']
                if 'ssid' in i:
                    attrs['ssid']=i['ssid']
                yield from hass.async_add_job(
                    partial(self.see, dev_id=clientMac.replace(':', ''),
                            gps=gps_location,
                            gps_accuracy=accuracy,
                            attributes=attrs))
        return
