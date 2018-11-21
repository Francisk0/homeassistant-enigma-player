"""
Support for Enigma2 set-top boxes.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/enigma/
"""

import asyncio
from datetime import timedelta
import logging
from urllib.error import HTTPError, URLError
import urllib.parse
import urllib.request

import voluptuous as vol

from homeassistant.const import (
    CONF_DEVICES, CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_TIMEOUT,
    CONF_USERNAME, STATE_OFF, STATE_ON, STATE_UNKNOWN)
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.entity import Entity

# REQUIREMENTS
REQUIREMENTS = ['beautifulsoup4==4.6.3']

# LOGGING
_LOGGER = logging.getLogger(__name__)

# DOMAIN
DOMAIN = 'enigma'

# Supported domains
SUPPORTED_DOMAINS = ['media_player']

# Local confs
CONF_HOST = 'host'

# DEFAULTS
DEFAULT_PORT = 80
DEFAULT_NAME = "Enigma2 Satelite"
DEFAULT_TIMEOUT = 30
DEFAULT_USERNAME = 'root'
DEFAULT_PASSWORD = ''
DEFAULT_BOUQUET = 'bouquet'
DEFAULT_PICON = 'picon'

# Local
CONF_BOUQUET = 'bouquet'
CONF_PICON = 'picon'

ENIGMA_CONFIG = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.socket_timeout,
    vol.Optional(CONF_BOUQUET, default=DEFAULT_BOUQUET): cv.string,
    vol.Optional(CONF_PICON, default=DEFAULT_PICON): cv.string,
    })


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES):
            vol.All(cv.ensure_list, [
                vol.Schema({
                    vol.Required(CONF_HOST): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME):\
                                 cv.string,
                    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD):\
                                 cv.string,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT):\
                                 cv.socket_timeout,
                    vol.Optional(CONF_BOUQUET, default=DEFAULT_BOUQUET):\
                                 cv.string,
                    vol.Optional(CONF_PICON, default=DEFAULT_PICON):\
                                 cv.string,
                }),
            ]),
        })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Initialize the Enigma device."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = []

    _LOGGER.info("Initializing enigma devices")

    enigma_list = []

    configured_devices = config[DOMAIN].get(CONF_DEVICES)
    for device in configured_devices:
        enigma = EnigmaDevice(device.get(CONF_HOST),
                              device.get(CONF_PORT),
                              device.get(CONF_NAME),
                              device.get(CONF_USERNAME),
                              device.get(CONF_PASSWORD),
                              device.get(CONF_TIMEOUT),
                              device.get(CONF_BOUQUET),
                              device.get(CONF_PICON))

        _LOGGER.debug("Enigma device %s configured", device.get(CONF_HOST))
        enigma_list.append(enigma)

    hass.data[DOMAIN] = enigma_list

    if not enigma_list:
        _LOGGER.info("No enigma devices configured")
        return False

    _LOGGER.debug("Configured %s enigmas", len(enigma_list))

    for domain in SUPPORTED_DOMAINS:
        hass.async_create_task(
            discovery.async_load_platform(hass, domain, DOMAIN, {}, config))
    return True


class EnigmaDevice(Entity):
    """Representation of a Enigma device."""

    def __init__(self, host, port, name, username, password, timeout,
                 bouquet, picon):
        """Initialize the Enigma device."""
        self._host = host
        self._port = port
        self._name = name
        self._username = username
        self._password = password
        self._timeout = timeout
        self._bouquet = bouquet
        self._picon = picon
        self._pwstate = True
        self._volume = 0
        self._muted = False
        self._selected_source = ''
        self._picon_url = None
        self._source_names = {}
        self._sources = {}
        # Opener for http connection
        self._opener = False

        # Check if is password enabled
        if self._password is not None:
            # Handle HTTP Auth
            mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            mgr.add_password(None, self._host+":"+str(self._port),
                             self._username, self._password)
            handler = urllib.request.HTTPBasicAuthHandler(mgr)
            self._opener = urllib.request.build_opener(handler)
            self._opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        else:
            handler = urllib.request.HTTPHandler()
            self._opener = urllib.request.build_opener(handler)
            self._opener.addheaders = [('User-agent', 'Mozilla/5.0')]
