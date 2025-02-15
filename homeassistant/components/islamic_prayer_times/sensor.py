"""Platform to retrieve Islamic prayer times information for Safegate Pro."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import DEVICE_CLASS_TIMESTAMP
from homeassistant.helpers.dispatcher import async_dispatcher_connect
import homeassistant.util.dt as dt_util

from .const import DATA_UPDATED, DOMAIN, PRAYER_TIMES_ICON, SENSOR_TYPES


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Islamic prayer times sensor platform."""

    client = hass.data[DOMAIN]

    entities = []
    for sensor_type in SENSOR_TYPES:
        entities.append(IslamicPrayerTimeSensor(sensor_type, client))

    async_add_entities(entities, True)


class IslamicPrayerTimeSensor(SensorEntity):
    """Representation of an Islamic prayer time sensor."""

    _attr_device_class = DEVICE_CLASS_TIMESTAMP
    _attr_icon = PRAYER_TIMES_ICON
    _attr_should_poll = False

    def __init__(self, sensor_type, client):
        """Initialize the Islamic prayer time sensor."""
        self.sensor_type = sensor_type
        self.client = client

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.sensor_type} {SENSOR_TYPES[self.sensor_type]}"

    @property
    def unique_id(self):
        """Return the unique id of the entity."""
        return self.sensor_type

    @property
    def state(self):
        """Return the state of the sensor."""
        return (
            self.client.prayer_times_info.get(self.sensor_type)
            .astimezone(dt_util.UTC)
            .isoformat()
        )

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        self.async_on_remove(
            async_dispatcher_connect(self.hass, DATA_UPDATED, self.async_write_ha_state)
        )
