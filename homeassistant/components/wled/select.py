"""Support for LED selects."""
from __future__ import annotations

from functools import partial

from wled import Preset

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WLEDDataUpdateCoordinator
from .helpers import wled_exception_handler
from .models import WLEDEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WLED select based on a config entry."""
    coordinator: WLEDDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([WLEDPresetSelect(coordinator)])

    update_segments = partial(
        async_update_segments,
        coordinator,
        set(),
        async_add_entities,
    )
    coordinator.async_add_listener(update_segments)
    update_segments()


class WLEDPresetSelect(WLEDEntity, SelectEntity):
    """Defined a WLED Preset select."""

    _attr_icon = "mdi:playlist-play"

    def __init__(self, coordinator: WLEDDataUpdateCoordinator) -> None:
        """Initialize WLED ."""
        super().__init__(coordinator=coordinator)

        self._attr_name = f"{coordinator.data.info.name} Preset"
        self._attr_unique_id = f"{coordinator.data.info.mac_address}_preset"
        self._attr_options = [preset.name for preset in self.coordinator.data.presets]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return len(self.coordinator.data.presets) > 0 and super().available

    @property
    def current_option(self) -> str | None:
        """Return the current selected preset."""
        if not isinstance(self.coordinator.data.state.preset, Preset):
            return None
        return self.coordinator.data.state.preset.name

    @wled_exception_handler
    async def async_select_option(self, option: str) -> None:
        """Set WLED segment to the selected preset."""
        await self.coordinator.wled.preset(preset=option)


class WLEDPaletteSelect(WLEDEntity, SelectEntity):
    """Defines a WLED Palette select."""

    _attr_icon = "mdi:palette-outline"
    _segment: int
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: WLEDDataUpdateCoordinator, segment: int) -> None:
        """Initialize WLED ."""
        super().__init__(coordinator=coordinator)

        # Segment 0 uses a simpler name, which is more natural for when using
        # a single segment / using WLED with one big LED strip.
        self._attr_name = (
            f"{coordinator.data.info.name} Segment {segment} Color Palette"
        )
        if segment == 0:
            self._attr_name = f"{coordinator.data.info.name} Color Palette"

        self._attr_unique_id = f"{coordinator.data.info.mac_address}_palette_{segment}"
        self._attr_options = [
            palette.name for palette in self.coordinator.data.palettes
        ]
        self._segment = segment

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        try:
            self.coordinator.data.state.segments[self._segment]
        except IndexError:
            return False

        return super().available

    @property
    def current_option(self) -> str | None:
        """Return the current selected color palette."""
        return self.coordinator.data.state.segments[self._segment].palette.name

    @wled_exception_handler
    async def async_select_option(self, option: str) -> None:
        """Set WLED segment to the selected color palette."""
        await self.coordinator.wled.segment(segment_id=self._segment, palette=option)


@callback
def async_update_segments(
    coordinator: WLEDDataUpdateCoordinator,
    current_ids: set[int],
    async_add_entities,
) -> None:
    """Update segments."""
    segment_ids = {segment.segment_id for segment in coordinator.data.state.segments}

    new_entities = []

    # Process new segments, add them to Safegate Pro
    for segment_id in segment_ids - current_ids:
        current_ids.add(segment_id)
        new_entities.append(WLEDPaletteSelect(coordinator, segment_id))

    if new_entities:
        async_add_entities(new_entities)
