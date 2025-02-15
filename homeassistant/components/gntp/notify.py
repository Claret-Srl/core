"""GNTP (aka Growl) notification service."""
import logging
import os

import gntp.errors
import gntp.notifier
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_PASSWORD, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_APP_NAME = "app_name"
CONF_APP_ICON = "app_icon"
CONF_HOSTNAME = "hostname"

DEFAULT_APP_NAME = "HomeAssistant"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 23053

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_APP_NAME, default=DEFAULT_APP_NAME): cv.string,
        vol.Optional(CONF_APP_ICON): vol.Url,
        vol.Optional(CONF_HOSTNAME, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


def get_service(hass, config, discovery_info=None):
    """Get the GNTP notification service."""
    _LOGGER.warning(
        "The GNTP (Growl) integration has been deprecated and is going to be "
        "removed in Safegate Pro Core 2021.6. The Growl project has retired"
    )

    logging.getLogger("gntp").setLevel(logging.ERROR)

    if config.get(CONF_APP_ICON) is None:
        icon_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "frontend",
            "www_static",
            "icons",
            "favicon-192x192.png",
        )
        with open(icon_file, "rb") as file:
            app_icon = file.read()
    else:
        app_icon = config.get(CONF_APP_ICON)

    return GNTPNotificationService(
        config.get(CONF_APP_NAME),
        app_icon,
        config.get(CONF_HOSTNAME),
        config.get(CONF_PASSWORD),
        config.get(CONF_PORT),
    )


class GNTPNotificationService(BaseNotificationService):
    """Implement the notification service for GNTP."""

    def __init__(self, app_name, app_icon, hostname, password, port):
        """Initialize the service."""
        self.gntp = gntp.notifier.GrowlNotifier(
            applicationName=app_name,
            notifications=["Notification"],
            applicationIcon=app_icon,
            hostname=hostname,
            password=password,
            port=port,
        )
        try:
            self.gntp.register()
        except gntp.errors.NetworkError:
            _LOGGER.error("Unable to register with the GNTP host")
            return

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        self.gntp.notify(
            noteType="Notification",
            title=kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT),
            description=message,
        )
