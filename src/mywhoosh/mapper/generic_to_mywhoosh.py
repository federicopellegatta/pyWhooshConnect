import re
from typing import List, Optional

from src.common.mapper.base import BaseMapper, PowerZonesOptions, MapperOptions
from src.common.model.generic_workout import GenericWorkout, GenericAtomicStep, GenericStepWithIntervals, \
    GenericIntervalStep
from src.common.model.generic_workout_step import GenericWorkoutStep, StepType
from src.mywhoosh.model.mywhoosh_workout_dto import MyWhooshWorkout, MyWhooshWorkoutStep


def _name(workout: GenericWorkout) -> str:
    formatted_schedule_date = workout.scheduled_date.strftime("%Y%m%d") if workout.scheduled_date else None
    formatted_name = re.sub(r'[^a-zA-Z0-9]', '', workout.name)

    return f"{formatted_schedule_date or ''} {formatted_name}"


class GenericToMyWhooshPowerMapper(BaseMapper[int, float]):
    def map(self, zone: int, options: Optional[PowerZonesOptions] = None) -> float:
        if not options.power_zones:
            raise RuntimeError("No power zones specified")

        floor, ceiling = options.power_zones.get_zone(zone)

        if zone == 7:  # ceiling == inf
            return floor * options.zone7_multiplier

        return floor + (ceiling - floor) * options.zone_weight


class GenericToMyWhooshStepMapper(BaseMapper[GenericWorkoutStep, MyWhooshWorkoutStep]):
    power_mapper = GenericToMyWhooshPowerMapper()

    def map(self, step: GenericWorkoutStep, options: Optional[MapperOptions] = None) -> List[MyWhooshWorkoutStep]:
        if isinstance(step, GenericAtomicStep) or isinstance(step, GenericIntervalStep):
            return [MyWhooshWorkoutStep(
                IntervalId=0,
                StepType="E_FreeRide" if step.type == StepType.FREE_RIDE else "E_Normal",
                Id=step.step_id,
                WorkoutMessage=[step.description] if step.description else [],
                Rpm=step.rpm if step.rpm else 0,
                Power=self.power_mapper.map(step.power_zone, options),
                Pace=0,
                StartPower=0,
                EndPower=0,
                Time=step.duration_in_seconds,
                IsManualGrade=False,
                ManualGradeValue=0,
                ShowAveragePower=True,
                FlatRoad=0
            )]
        if isinstance(step, GenericStepWithIntervals):
            return [
                interval
                for intervals in step.steps
                for interval in self.map(intervals, options)
            ]

        raise TypeError(f"{type(step)} not supported")


class GenericToMyWhooshWorkoutStepMapper(BaseMapper[GenericWorkout, MyWhooshWorkout]):
    step_mapper = GenericToMyWhooshStepMapper()

    def map(self, workout: GenericWorkout, options: Optional[MapperOptions] = None) -> MyWhooshWorkout:
        return MyWhooshWorkout(
            Name=_name(workout),
            Description=workout.description,
            WorkoutSteps=[
                substep
                for step in workout.steps
                for substep in self.step_mapper.map(step, options)
            ],
            StepCount=workout.number_of_intervals(),
            Time=int(workout.duration().total_seconds()),
            AuthorName="Garmin powered by pyWhooshGarmin"
        )
