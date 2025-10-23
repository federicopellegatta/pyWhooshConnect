from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional

from src.common.model.generic_workout_step import GenericWorkoutStep
from src.common.model.workout_step_utils import StepContainerMixin


@dataclass
class GenericAtomicStep(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    type: str
    power_zone: Optional[int] = None # None means free ride
    description: Optional[str] = None
    rpm: Optional[int] = None

    @property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)


@dataclass
class GenericIntervalStep(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    power_zone: int
    type: str
    description: Optional[str] = None
    rpm: Optional[int] = None

    @property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)


@dataclass
class GenericStepWithIntervals(GenericWorkoutStep, StepContainerMixin):
    step_id: int
    type: str
    steps: List[GenericIntervalStep]
    iterations: int
    description: Optional[str] = None

    @property
    def duration_in_seconds(self) -> int:
        total = sum(i.duration_in_seconds for i in self.steps or [])
        return total * (self.iterations or 1)

    @property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)

    def get_interval_by_id(self, interval_id: int) -> GenericIntervalStep:
        return next(step for step in self.steps if step.step_id == interval_id)


@dataclass
class GenericWorkout(StepContainerMixin):
    name: str
    description: str
    steps: List[GenericWorkoutStep]
    sport: str = "cycling"

    def get_step_by_id(self, step_id: int) -> GenericWorkoutStep:
        return next(step for step in self.steps if step.step_id == step_id)
