from src.common.mapper.base import BaseMapper
from src.common.model.generic_workout import GenericWorkout, GenericAtomicStep, GenericStepWithIntervals
from src.common.model.generic_workout_step import GenericWorkoutStep
from src.garmin.model.garmin_workout_dto import GarminWorkout, GarminWorkoutStep


class GarminToGenericAtomicStepMapper(BaseMapper[GarminWorkoutStep, GenericAtomicStep]):
    def map(self, garmin: GarminWorkoutStep) -> GenericAtomicStep:
        if garmin.workoutSteps:
            raise ValueError("Garmin step has intervals. You should use GarminToGenericStepWithIntervals")

        return GenericAtomicStep(
            step_id=garmin.stepId,
            _duration_in_seconds=int(garmin.endConditionValue),  # TODO manage using endCondition.conditionTypeKey
            power_zone=garmin.zoneNumber,
            type=garmin.stepType.stepTypeKey.lower(),
            description=garmin.description,
            rpm=None
        )


class GarminToGenericStepWithIntervals(BaseMapper[GarminWorkoutStep, GenericStepWithIntervals]):
    atomic_step_mapper = GarminToGenericAtomicStepMapper()

    def map(self, garmin: GarminWorkoutStep) -> GenericStepWithIntervals:
        if not garmin.workoutSteps:
            raise ValueError("Garmin step has not intervals. You should use GarminToGenericAtomicStepMapper")

        return GenericStepWithIntervals(
            step_id=garmin.stepId,
            type=garmin.stepType.stepTypeKey.lower(),
            description=garmin.description,
            iterations=int(garmin.endConditionValue),  # TODO manage using endCondition.conditionTypeKey
            steps=[
                self.atomic_step_mapper.map(interval)
                for interval in garmin.workoutSteps
            ]
        )


class GarminToGenericStepMapper(BaseMapper[GarminWorkoutStep, GenericWorkoutStep]):
    step_with_intervals_mapper = GarminToGenericStepWithIntervals()
    atomic_step_mapper = GarminToGenericAtomicStepMapper()

    def map(self, garmin: GarminWorkoutStep) -> GenericWorkoutStep:
        if garmin.workoutSteps:
            return self.step_with_intervals_mapper.map(garmin)
        else:
            return self.atomic_step_mapper.map(garmin)


class GarminToGenericWorkoutMapper(BaseMapper[GarminWorkout, GenericWorkout]):
    step_mapper = GarminToGenericStepMapper()

    def map(self, garmin: GarminWorkout) -> GenericWorkout:
        return GenericWorkout(
            name=garmin.workoutName,
            description=garmin.description,
            sport=garmin.sportType.sportTypeKey.lower(),
            steps=[
                self.step_mapper.map(step)
                for segment in garmin.workoutSegments
                for step in segment.workoutSteps
            ]
        )
