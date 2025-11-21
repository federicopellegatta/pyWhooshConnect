from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Optional


class StepType(Enum):
    WARM_UP = 1
    COOL_DOWN = 2
    RECOVERY = 3
    INTERVAL = 4
    FREE_RIDE = 5


class GenericWorkoutStep(ABC):
    step_id: int
    type: StepType
    description: Optional[str]

    @property
    @abstractmethod
    def duration(self) -> timedelta: ...
