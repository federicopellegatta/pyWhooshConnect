from abc import ABC, abstractmethod
from typing import TypeVar, Optional

from pywhooshconnect.common.mapper.base import (
    BaseMapper,
    MapperOptions,
    PowerZonesOptions,
)
from pywhooshconnect.common.model.generic_workout import (
    GenericWorkout,
    GenericAtomicStep,
    GenericStepWithIntervals,
    GenericIntervalStep,
)
from pywhooshconnect.common.model.generic_workout_step import (
    GenericWorkoutStep,
    StepType,
)
from pywhooshconnect.garmin.model.garmin_scheduled_workout_dto import (
    GarminScheduledWorkout,
)
from pywhooshconnect.garmin.model.garmin_workout_dto import (
    GarminWorkout,
    GarminWorkoutStep,
)

TStepTarget = TypeVar("TStepTarget", bound=GenericWorkoutStep)


class GarminToGenericStepMapper(BaseMapper[GarminWorkoutStep, TStepTarget], ABC):
    """Abstract mapper from GarminWorkoutStep to a GenericWorkoutStep implementation."""

    @abstractmethod
    def map(
        self, garmin: GarminWorkoutStep, options: Optional[MapperOptions] = None
    ) -> TStepTarget:
        """Convert a Garmin step into a generic step."""

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


class GarminToStepTypeMapper(GarminToGenericStepMapper[StepType]):
    def map(
        self, garmin: GarminWorkoutStep, options: Optional[MapperOptions] = None
    ) -> StepType:
        if garmin.zoneNumber is None:
            return StepType.FREE_RIDE

        mapping = {
            "warmup": StepType.WARM_UP,
            "cooldown": StepType.COOL_DOWN,
            "recovery": StepType.RECOVERY,
            "repeat": StepType.INTERVAL,
            "interval": StepType.INTERVAL,
        }

        return mapping.get(
            garmin.stepType.stepTypeKey if garmin.stepType else None, StepType.INTERVAL
        )


class GarminToGenericAtomicStepMapper(GarminToGenericStepMapper[GenericAtomicStep]):
    def map(
        self, garmin: GarminWorkoutStep, options: Optional[PowerZonesOptions] = None
    ) -> GenericAtomicStep:
        if garmin.workoutSteps:
            raise ValueError(
                "Garmin step has intervals. You should use GarminToGenericStepWithIntervals"
            )

        duration_in_seconds = self._calculate_step_duration_in_seconds(
            garmin, int(options.config.get_lap_button_duration().total_seconds())
        )

        return GenericAtomicStep(
            step_id=garmin.stepOrder,
            duration_in_seconds=duration_in_seconds,
            power_zone=garmin.zoneNumber,
            type=GarminToStepTypeMapper().map(garmin),
            description=garmin.description,
            rpm=None,
        )


class GarminToGenericIntervalStepMapper(GarminToGenericStepMapper[GenericIntervalStep]):
    def map(
        self, garmin: GarminWorkoutStep, options: Optional[MapperOptions] = None
    ) -> GenericIntervalStep:
        if garmin.workoutSteps:
            raise ValueError(
                "Garmin step has intervals. You should use GarminToGenericStepWithIntervals"
            )

        return GenericIntervalStep(
            step_id=garmin.stepId,
            duration_in_seconds=self._calculate_step_duration_in_seconds(garmin),
            power_zone=garmin.zoneNumber,
            type=GarminToStepTypeMapper().map(garmin),
            description=garmin.description,
            rpm=None,
        )


class GarminToGenericStepWithIntervals(
    GarminToGenericStepMapper[GenericStepWithIntervals]
):
    atomic_step_mapper = GarminToGenericIntervalStepMapper()

    def map(
        self, garmin: GarminWorkoutStep, options: Optional[MapperOptions] = None
    ) -> GenericStepWithIntervals:
        if not garmin.workoutSteps:
            raise ValueError(
                "Garmin step has not intervals. You should use GarminToGenericAtomicStepMapper"
            )

        step = GenericStepWithIntervals(
            step_id=garmin.stepOrder,
            type=GarminToStepTypeMapper().map(garmin),
            description=garmin.description,
            iterations=self._get_number_of_iterations(garmin),
            steps=[
                self.atomic_step_mapper.map(interval)
                for interval in garmin.workoutSteps
            ],
        )
        step.reindex_steps()
        return step

    @staticmethod
    def _get_number_of_iterations(garmin: GarminWorkoutStep):
        if not garmin.numberOfIterations:
            raise ValueError(
                f"Expected number of iterations for GarminWorkoutStep {garmin}"
            )
        return garmin.numberOfIterations


class GarminToGenericWorkoutMapper(BaseMapper[GarminWorkout, GenericWorkout]):
    step_with_intervals_mapper = GarminToGenericStepWithIntervals()
    atomic_step_mapper = GarminToGenericAtomicStepMapper()

    def map(
        self, garmin: GarminWorkout, options: Optional[PowerZonesOptions] = None
    ) -> GenericWorkout:
        workout = GenericWorkout(
            name=garmin.workoutName,
            description=garmin.description,
            sport=garmin.sportType.sportTypeKey.lower(),
            steps=[
                self._select_step_mapper(step).map(step, options)
                for segment in garmin.workoutSegments
                for step in segment.workoutSteps
            ],
        )
        workout.reindex_steps()
        return workout

    def _select_step_mapper(
        self, garmin_step: GarminWorkoutStep
    ) -> GarminToGenericStepMapper:
        if garmin_step.workoutSteps:
            return self.step_with_intervals_mapper
        else:
            return self.atomic_step_mapper


class GarminToGenericScheduledWorkoutMapper(
    BaseMapper[GarminScheduledWorkout, GenericWorkout]
):
    workout_mapper = GarminToGenericWorkoutMapper()

    def map(
        self, garmin: GarminScheduledWorkout, options: Optional[MapperOptions] = None
    ) -> GenericWorkout:
        workout = self.workout_mapper.map(garmin.workout, options)
        workout.scheduled_date = garmin.calendarDate
        return workout
