from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

TSource = TypeVar('TSource')
TTarget = TypeVar('TTarget')


class MapperOptions(ABC):
    """Base class for mapper options."""
    ...


class BaseMapper(ABC, Generic[TSource, TTarget]):
    """Base class for workout converters."""

    @abstractmethod
    def map(self, source: TSource, options: Optional[MapperOptions] = None) -> TTarget:
        """Convert source format to target format."""
        ...
