"""Constants for integration_blueprint."""
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# Base component constants
NAME = "VRKnock Client"
DOMAIN = "vrknock"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = ""
ISSUE_URL = ""

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]

SERVICE_TRIGGER_KNOCK = "trigger_knock"
SCHEMA_SERVICE_TRIGGER_KNOCK = {vol.Optional("message"): cv.string}


# Configuration and options
CONF_ENABLED = "enabled"
CONF_HOST = "host"
CONF_CODE = "code"
CONF_MODE = "mode"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
