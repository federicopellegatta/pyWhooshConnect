from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TSource = TypeVar('TSource')
TTarget = TypeVar('TTarget')


class BaseMapper(ABC, Generic[TSource, TTarget]):
    """Base class for workout converters."""

    @abstractmethod
    def map(self, source: TSource) -> TTarget:
        """Convert source format to target format."""
        ...
