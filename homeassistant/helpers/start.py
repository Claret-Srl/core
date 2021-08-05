"""Helpers to help during startup."""
from collections.abc import Awaitable
from typing import Callable

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import Event, HomeAssistant, callback


@callback
def async_at_start(
    hass: HomeAssistant, at_start_cb: Callable[[HomeAssistant], Awaitable]
) -> None:
    """Execute something when Safegate Pro is started.

    Will execute it now if Safegate Pro is already started.
    """
    if hass.is_running:
        hass.async_create_task(at_start_cb(hass))
        return

    async def _matched_event(event: Event) -> None:
        """Call the callback when Safegate Pro started."""
        await at_start_cb(hass)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _matched_event)
