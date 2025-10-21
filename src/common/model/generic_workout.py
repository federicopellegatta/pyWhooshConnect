from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional


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


@dataclass
class GenericAtomicStep(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    power_zone: int
    type: str
    description: Optional[str] = None
    rpm: Optional[int] = None


@dataclass
class GenericStepWithIntervals(GenericWorkoutStep):
    step_id: int
    type: str
    intervals: List[GenericAtomicStep]
    iterations: int
    description: Optional[str] = None

    @property
    def duration_in_seconds(self) -> int:
        total = sum(i.duration_in_seconds for i in self.intervals or [])
        return total * (self.iterations or 1)


@dataclass
class GenericWorkout:
    name: str
    description: str
    steps: List[GenericWorkoutStep]
    sport: str = "cycling"
