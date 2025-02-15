"""Support for the EPH Controls Ember themostats."""
from datetime import timedelta
import logging

from pyephember.pyephember import (
    EphEmber,
    ZoneMode,
    zone_current_temperature,
    zone_is_active,
    zone_is_boost_active,
    zone_is_hot_water,
    zone_mode,
    zone_name,
    zone_target_temperature,
)
import voluptuous as vol

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_AUX_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_USERNAME,
    TEMP_CELSIUS,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Return cached results if last scan was less then this time ago
SCAN_INTERVAL = timedelta(seconds=120)

OPERATION_LIST = [HVAC_MODE_HEAT_COOL, HVAC_MODE_HEAT, HVAC_MODE_OFF]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)

EPH_TO_HA_STATE = {
    "AUTO": HVAC_MODE_HEAT_COOL,
    "ON": HVAC_MODE_HEAT,
    "OFF": HVAC_MODE_OFF,
}

HA_STATE_TO_EPH = {value: key for key, value in EPH_TO_HA_STATE.items()}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the ephember thermostat."""
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    try:
        ember = EphEmber(username, password)
        zones = ember.get_zones()
        for zone in zones:
            add_entities([EphEmberThermostat(ember, zone)])
    except RuntimeError:
        _LOGGER.error("Cannot connect to EphEmber")
        return

    return


class EphEmberThermostat(ClimateEntity):
    """Representation of a EphEmber thermostat."""

    def __init__(self, ember, zone):
        """Initialize the thermostat."""
        self._ember = ember
        self._zone_name = zone_name(zone)
        self._zone = zone
        self._hot_water = zone_is_hot_water(zone)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        if self._hot_water:
            return SUPPORT_AUX_HEAT

        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_AUX_HEAT

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._zone_name

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return zone_current_temperature(self._zone)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return zone_target_temperature(self._zone)

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        if self._hot_water:
            return None

        return 0.5

    @property
    def hvac_action(self):
        """Return current HVAC action."""
        if zone_is_active(self._zone):
            return CURRENT_HVAC_HEAT

        return CURRENT_HVAC_IDLE

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        mode = zone_mode(self._zone)
        return self.map_mode_eph_hass(mode)

    @property
    def hvac_modes(self):
        """Return the supported operations."""
        return OPERATION_LIST

    def set_hvac_mode(self, hvac_mode):
        """Set the operation mode."""
        mode = self.map_mode_hass_eph(hvac_mode)
        if mode is not None:
            self._ember.set_mode_by_name(self._zone_name, mode)
        else:
            _LOGGER.error("Invalid operation mode provided %s", hvac_mode)

    @property
    def is_aux_heat(self):
        """Return true if aux heater."""

        return zone_is_boost_active(self._zone)

    def turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        self._ember.activate_boost_by_name(
            self._zone_name, zone_target_temperature(self._zone)
        )

    def turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        self._ember.deactivate_boost_by_name(self._zone_name)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        if self._hot_water:
            return

        if temperature == self.target_temperature:
            return

        if temperature > self.max_temp or temperature < self.min_temp:
            return

        self._ember.set_target_temperture_by_name(self._zone_name, temperature)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        # Hot water temp doesn't support being changed
        if self._hot_water:
            return zone_target_temperature(self._zone)

        return 5.0

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._hot_water:
            return zone_target_temperature(self._zone)

        return 35.0

    def update(self):
        """Get the latest data."""
        self._zone = self._ember.get_zone(self._zone_name)

    @staticmethod
    def map_mode_hass_eph(operation_mode):
        """Map from Safegate Pro mode to eph mode."""
        return getattr(ZoneMode, HA_STATE_TO_EPH.get(operation_mode), None)

    @staticmethod
    def map_mode_eph_hass(operation_mode):
        """Map from eph mode to Safegate Pro mode."""
        return EPH_TO_HA_STATE.get(operation_mode.name, HVAC_MODE_HEAT_COOL)
