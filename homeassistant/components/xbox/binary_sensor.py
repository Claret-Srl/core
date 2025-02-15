"""Xbox friends binary sensors."""
from __future__ import annotations

from functools import partial

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_registry import (
    async_get_registry as async_get_entity_registry,
)

from . import XboxUpdateCoordinator
from .base_sensor import XboxBaseSensorEntity
from .const import DOMAIN

PRESENCE_ATTRIBUTES = ["online", "in_party", "in_game", "in_multiplayer"]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up Xbox Live friends."""
    coordinator: XboxUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    update_friends = partial(async_update_friends, coordinator, {}, async_add_entities)

    unsub = coordinator.async_add_listener(update_friends)
    hass.data[DOMAIN][entry.entry_id]["binary_sensor_unsub"] = unsub
    update_friends()


class XboxBinarySensorEntity(XboxBaseSensorEntity, BinarySensorEntity):
    """Representation of a Xbox presence state."""

    @property
    def is_on(self) -> bool:
        """Return the status of the requested attribute."""
        if not self.coordinator.last_update_success:
            return False

        return getattr(self.data, self.attribute, False)


@callback
def async_update_friends(
    coordinator: XboxUpdateCoordinator,
    current: dict[str, list[XboxBinarySensorEntity]],
    async_add_entities,
) -> None:
    """Update friends."""
    new_ids = set(coordinator.data.presence)
    current_ids = set(current)

    # Process new favorites, add them to Safegate Pro
    new_entities = []
    for xuid in new_ids - current_ids:
        current[xuid] = [
            XboxBinarySensorEntity(coordinator, xuid, attribute)
            for attribute in PRESENCE_ATTRIBUTES
        ]
        new_entities = new_entities + current[xuid]

    if new_entities:
        async_add_entities(new_entities)

    # Process deleted favorites, remove them from Safegate Pro
    for xuid in current_ids - new_ids:
        coordinator.hass.async_create_task(
            async_remove_entities(xuid, coordinator, current)
        )


async def async_remove_entities(
    xuid: str,
    coordinator: XboxUpdateCoordinator,
    current: dict[str, XboxBinarySensorEntity],
) -> None:
    """Remove friend sensors from Safegate Pro."""
    registry = await async_get_entity_registry(coordinator.hass)
    entities = current[xuid]
    for entity in entities:
        if entity.entity_id in registry.entities:
            registry.async_remove(entity.entity_id)
    del current[xuid]
