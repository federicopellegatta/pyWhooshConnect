from abc import ABC, abstractmethod
from typing import TypeVar

from src.common.mapper.base import BaseMapper
from src.common.model.generic_workout import GenericWorkout, GenericAtomicStep, GenericStepWithIntervals
from src.common.model.generic_workout_step import GenericWorkoutStep
from src.garmin.model.garmin_workout_dto import GarminWorkout, GarminWorkoutStep

TStepTarget = TypeVar("TStepTarget", bound=GenericWorkoutStep)


class GarminToGenericStepMapper(BaseMapper[GarminWorkoutStep, TStepTarget], ABC):
    """Abstract mapper from GarminWorkoutStep to a GenericWorkoutStep implementation."""

    @abstractmethod
    def map(self, garmin: GarminWorkoutStep) -> TStepTarget:
        """Convert a Garmin step into a generic step."""
        ...

    @staticmethod
    def _calculate_step_duration_in_seconds(
            garmin: GarminWorkoutStep,
            lap_button_duration_seconds: int = 30,
    ) -> int:
        if garmin.endCondition.conditionTypeKey == "time":
            return int(garmin.endConditionValue)
        if garmin.endCondition.conditionTypeKey == "lap.button":
            return lap_button_duration_seconds
        raise ValueError(f"Unknown step condition type {garmin.endCondition}")


class GarminToGenericAtomicStepMapper(GarminToGenericStepMapper[GenericAtomicStep]):
    def map(self, garmin: GarminWorkoutStep) -> GenericAtomicStep:
        if garmin.workoutSteps:
            raise ValueError("Garmin step has intervals. You should use GarminToGenericStepWithIntervals")

        return GenericAtomicStep(
            step_id=garmin.stepOrder,
            _duration_in_seconds=self._calculate_step_duration_in_seconds(garmin),
            power_zone=garmin.zoneNumber,
            type=garmin.stepType.stepTypeKey.lower(),
            description=garmin.description,
            rpm=None
        )


class GarminToGenericStepWithIntervals(GarminToGenericStepMapper[GenericStepWithIntervals]):
    atomic_step_mapper = GarminToGenericAtomicStepMapper()

    def map(self, garmin: GarminWorkoutStep) -> GenericStepWithIntervals:
        if not garmin.workoutSteps:
            raise ValueError("Garmin step has not intervals. You should use GarminToGenericAtomicStepMapper")

        return GenericStepWithIntervals(
            step_id=garmin.stepOrder,
            type=garmin.stepType.stepTypeKey.lower(),
            description=garmin.description,
            iterations=self._get_number_of_iterations(garmin),
            steps=[
                self.atomic_step_mapper.map(interval)
                for interval in garmin.workoutSteps
            ]
        )

    @staticmethod
    def _get_number_of_iterations(garmin: GarminWorkoutStep):
        if not garmin.numberOfIterations:
            raise ValueError(f"Expected number of iterations for GarminWorkoutStep {garmin}")
        return garmin.numberOfIterations


class GarminToGenericWorkoutMapper(BaseMapper[GarminWorkout, GenericWorkout]):
    step_with_intervals_mapper = GarminToGenericStepWithIntervals()
    atomic_step_mapper = GarminToGenericAtomicStepMapper()

    def map(self, garmin: GarminWorkout) -> GenericWorkout:
        return GenericWorkout(
            name=garmin.workoutName,
            description=garmin.description,
            sport=garmin.sportType.sportTypeKey.lower(),
            steps=[
                self._select_step_mapper(step).map(step)
                for segment in garmin.workoutSegments
                for step in segment.workoutSteps
            ]
        )

    def _select_step_mapper(self, garmin_step: GarminWorkoutStep) -> GarminToGenericStepMapper:
        if garmin_step.workoutSteps:
            return self.step_with_intervals_mapper
        else:
            return self.atomic_step_mapper
