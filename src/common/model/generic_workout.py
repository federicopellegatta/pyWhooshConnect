from dataclasses import dataclass
from typing import List, Optional

from src.common.model.generic_workout_step import GenericWorkoutStep
from src.common.model.workout_step_utils import StepContainerMixin


@dataclass
class GenericAtomicStep(GenericWorkoutStep):
    step_id: int
    _duration_in_seconds: int
    power_zone: int
    type: str
    description: Optional[str] = None
    rpm: Optional[int] = None

    @property
    def duration_in_seconds(self) -> int:
        return self._duration_in_seconds


@dataclass
class GenericStepWithIntervals(GenericWorkoutStep, StepContainerMixin):
    step_id: int
    type: str
    steps: List[GenericAtomicStep]
    iterations: int
    description: Optional[str] = None

    @property
    def duration_in_seconds(self) -> int:
        total = sum(i.duration_in_seconds for i in self.steps or [])
        return total * (self.iterations or 1)


@dataclass
class GenericWorkout(StepContainerMixin):
    name: str
    description: str
    steps: List[GenericWorkoutStep]
    sport: str = "cycling"
