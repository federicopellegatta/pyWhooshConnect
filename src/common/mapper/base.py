from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

from src.common.model.power_zones import PowerZones

TSource = TypeVar('TSource')
TTarget = TypeVar('TTarget')


class MapperOptions(ABC):
    """Base class for mapper options."""
    ...


@dataclass
class PowerZonesOptions(MapperOptions):
    power_zones: PowerZones
    zone_weight: float = 0.5
    zone7_multiplier: float = 1.1

    def __post_init__(self):
        if not 0.0 <= self.zone_weight <= 1.0:
            raise ValueError(f"zone_weight must be between 0.0 and 1.0, got {self.zone_weight}")

        if self.zone7_multiplier < 1:
            raise ValueError(f"zone7_multiplier must be greater than or equal to 1, got {self.zone7_multiplier}")


class BaseMapper(ABC, Generic[TSource, TTarget]):
    """Base class for workout converters."""

    @abstractmethod
    def map(self, source: TSource, options: Optional[MapperOptions] = None) -> TTarget:
        """Convert source format to target format."""
        ...
