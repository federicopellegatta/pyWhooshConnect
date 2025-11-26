from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

from pywhooshconnect.common.model.power_zones import PowerZones
from pywhooshconnect.mywhoosh.mapper.power_zones_config import PowerZoneConfig

TSource = TypeVar("TSource")
TTarget = TypeVar("TTarget")


class MapperOptions(ABC):
    """Base class for mapper options."""


@dataclass
class PowerZonesOptions(MapperOptions):
    power_zones: PowerZones
    config: PowerZoneConfig = PowerZoneConfig()


class BaseMapper(ABC, Generic[TSource, TTarget]):
    """Base class for workout converters."""

    @abstractmethod
    def map(self, source: TSource, options: Optional[MapperOptions] = None) -> TTarget:
        """Convert source format to target format."""
        ...
