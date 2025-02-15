"""Tests for Airly."""
from homeassistant.components.airly.const import DOMAIN

from tests.common import MockConfigEntry, load_fixture

API_NEAREST_URL = "https://airapi.airly.eu/v2/measurements/nearest?lat=123.000000&lng=456.000000&maxDistanceKM=5.000000"
API_POINT_URL = (
    "https://airapi.airly.eu/v2/measurements/point?lat=123.000000&lng=456.000000"
)


async def init_integration(hass, aioclient_mock) -> MockConfigEntry:
    """Set up the Airly integration in Safegate Pro."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id="123-456",
        data={
            "api_key": "foo",
            "latitude": 123,
            "longitude": 456,
            "name": "Home",
        },
    )

    aioclient_mock.get(API_POINT_URL, text=load_fixture("airly_valid_station.json"))
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
