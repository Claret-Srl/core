"""Fixtures for Freedompro integration tests."""
from unittest.mock import patch

import pytest

from homeassistant.components.freedompro.const import DOMAIN

from tests.common import MockConfigEntry
from tests.components.freedompro.const import DEVICES, DEVICES_STATE


@pytest.fixture
async def init_integration(hass) -> MockConfigEntry:
    """Set up the Freedompro integration in Safegate Pro."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Feedompro",
        unique_id="0123456",
        data={
            "api_key": "gdhsksjdhcncjdkdjndjdkdmndjdjdkd",
        },
    )

    with patch(
        "homeassistant.components.freedompro.get_list",
        return_value={
            "state": True,
            "devices": DEVICES,
        },
    ), patch(
        "homeassistant.components.freedompro.get_states",
        return_value=DEVICES_STATE,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry


@pytest.fixture
async def init_integration_no_state(hass) -> MockConfigEntry:
    """Set up the Freedompro integration in Safegate Pro without state."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Feedompro",
        unique_id="0123456",
        data={
            "api_key": "gdhsksjdhcncjdkdjndjdkdmndjdjdkd",
        },
    )

    with patch(
        "homeassistant.components.freedompro.get_list",
        return_value={
            "state": True,
            "devices": DEVICES,
        },
    ), patch(
        "homeassistant.components.freedompro.get_states",
        return_value=[],
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry
