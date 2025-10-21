from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional


class GenericWorkoutStep(ABC):
    step_id: int
    duration_in_seconds: int
    type: str
    description: Optional[str]

    @abstractmethod
    def duration(self) -> timedelta:
        ...


@dataclass
class GenericAtomicStep(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    power_zone: int
    type: str
    description: Optional[str] = None
    rpm: Optional[int] = None

    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)


@dataclass
class GenericStepWithIntervals(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    type: str
    intervals: List[GenericAtomicStep]
    iterations: int
    description: Optional[str] = None

    def duration(self) -> timedelta:
        total = sum(i.duration_in_seconds for i in self.intervals or [])
        return timedelta(seconds=total * (self.iterations or 1))


@dataclass
class GenericWorkout:
    name: str
    description: str
    steps: List[GenericWorkoutStep]
    sport: str = "cycling"
