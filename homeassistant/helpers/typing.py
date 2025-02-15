"""Typing Helpers for Safegate Pro."""
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple, Union

import homeassistant.core

GPSType = Tuple[float, float]
ConfigType = Dict[str, Any]
ContextType = homeassistant.core.Context
DiscoveryInfoType = Dict[str, Any]
EventType = homeassistant.core.Event
ServiceDataType = Dict[str, Any]
StateType = Union[None, str, int, float]
TemplateVarsType = Optional[Mapping[str, Any]]

# Custom type for recorder Queries
QueryType = Any


class UndefinedType(Enum):
    """Singleton type for use with not set sentinel values."""

    _singleton = 0


UNDEFINED = UndefinedType._singleton  # pylint: disable=protected-access

# The following types should not used and
# are not present in the core code base.
# They are kept in order not to break custom integrations
# that may rely on them.
# In due time they will be removed.
HomeAssistantType = homeassistant.core.HomeAssistant
ServiceCallType = homeassistant.core.ServiceCall
