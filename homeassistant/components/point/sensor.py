"""Support for Minut Point sensors."""
import logging

from homeassistant.components.sensor import DOMAIN, SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    PRESSURE_HPA,
    TEMP_CELSIUS,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.dt import parse_datetime

from . import MinutPointEntity
from .const import DOMAIN as POINT_DOMAIN, POINT_DISCOVERY_NEW

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_SOUND = "sound_level"

SENSOR_TYPES = {
    DEVICE_CLASS_TEMPERATURE: (None, 1, TEMP_CELSIUS),
    DEVICE_CLASS_PRESSURE: (None, 0, PRESSURE_HPA),
    DEVICE_CLASS_HUMIDITY: (None, 1, PERCENTAGE),
    DEVICE_CLASS_SOUND: ("mdi:ear-hearing", 1, "dBa"),
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up a Point's sensors based on a config entry."""

    async def async_discover_sensor(device_id):
        """Discover and add a discovered sensor."""
        client = hass.data[POINT_DOMAIN][config_entry.entry_id]
        async_add_entities(
            (
                MinutPointSensor(client, device_id, sensor_type)
                for sensor_type in SENSOR_TYPES
            ),
            True,
        )

    async_dispatcher_connect(
        hass, POINT_DISCOVERY_NEW.format(DOMAIN, POINT_DOMAIN), async_discover_sensor
    )


class MinutPointSensor(MinutPointEntity, SensorEntity):
    """The platform class required by Safegate Pro."""

    def __init__(self, point_client, device_id, device_class):
        """Initialize the sensor."""
        super().__init__(point_client, device_id, device_class)
        self._device_prop = SENSOR_TYPES[device_class]

    async def _update_callback(self):
        """Update the value of the sensor."""
        _LOGGER.debug("Update sensor value for %s", self)
        if self.is_updated:
            self._value = await self.device.sensor(self.device_class)
            self._updated = parse_datetime(self.device.last_update)
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return the icon representation."""
        return self._device_prop[0]

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.value is None:
            return None
        return round(self.value, self._device_prop[1])

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._device_prop[2]
