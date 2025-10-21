from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional


class GenericWorkoutStep(ABC):
    step_id: int
    type: str
    description: Optional[str]

    @property
    @abstractmethod
    def duration_in_seconds(self) -> int:
        ...

    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)
