from dataclasses import dataclass
from datetime import timedelta, date
from typing import List, Optional

from src.common.model.generic_workout_step import GenericWorkoutStep, StepType
from src.common.model.workout_step_utils import StepContainerMixin


@dataclass
class GenericAtomicStep(GenericWorkoutStep):
    step_id: int
    duration_in_seconds: int
    type: StepType
    power_zone: Optional[int] = None  # None means free ride
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
    type: StepType
    description: Optional[str] = None
    rpm: Optional[int] = None

    @property
    def duration(self) -> timedelta:
        return timedelta(seconds=self.duration_in_seconds)


@dataclass
class GenericStepWithIntervals(GenericWorkoutStep, StepContainerMixin):
    step_id: int
    type: StepType
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
    scheduled_date: Optional[date] = None

    def get_step_by_id(self, step_id: int) -> GenericWorkoutStep:
        return next(step for step in self.steps if step.step_id == step_id)

    def duration(self) -> timedelta:
        return sum((step.duration for step in self.steps), timedelta())

    def number_of_intervals(self):
        return sum(
            (
                len(step.steps) * step.iterations
                if isinstance(step, GenericStepWithIntervals)
                else 1
            )
            for step in self.steps
        )

    def flatten_steps(self) -> List[GenericWorkoutStep]:
        """
        Returns a flat list of all atomic/interval steps with expanded repetitions.
        Steps with intervals are expanded according to their iteration count.
        """
        self.reindex_steps()

        flat_steps = []
        for step in self.steps:
            if isinstance(step, GenericStepWithIntervals):
                for _ in range(step.iterations):
                    flat_steps.extend(step.steps)
            else:
                flat_steps.append(step)
        return flat_steps
