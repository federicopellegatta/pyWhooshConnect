import json
from datetime import date
from pathlib import Path

import pytest

from src.common.model.generic_workout import (
    GenericAtomicStep,
    GenericStepWithIntervals,
    GenericIntervalStep,
    GenericWorkout
)
from src.garmin.mapper.garmin_to_generic_workout import GarminToGenericWorkoutMapper, GarminToGenericScheduledWorkoutMapper
from src.garmin.model.garmin_scheduled_workout_dto import GarminScheduledWorkout
from src.garmin.model.garmin_workout_dto import GarminWorkout, GarminWorkoutStep


def json_path(filename: str) -> Path:
    return Path(__file__).parents[2] / "resources" / "garmin" / filename


def load_garmin_workout(filename: str):
    with open(json_path(filename), encoding="utf-8") as f:
        data = json.load(f)
    return GarminWorkout(**data)


@pytest.fixture(params=["garmin_workout.json", "garmin_z2_workout.json"])
def garmin_workout(request):
    """Load GarminWorkout from JSON file."""
    return load_garmin_workout(request.param)


@pytest.fixture
def generic_workout(garmin_workout):
    """Map GarminWorkout to GenericWorkout."""
    return GarminToGenericWorkoutMapper().map(garmin_workout)


def _get_step_with_intervals(garmin: GarminWorkout, generic: GenericWorkout) -> tuple[None, None] | tuple[
    GarminWorkoutStep, GenericStepWithIntervals]:
    garmin_step_with_intervals = next((s for s in garmin.workoutSegments[0].workoutSteps if s.workoutSteps), None)
    if not garmin_step_with_intervals:
        return None, None

    generic_step_with_intervals = generic.get_step_by_id(garmin_step_with_intervals.stepOrder)
    assert isinstance(generic_step_with_intervals, GenericStepWithIntervals)

    return garmin_step_with_intervals, generic_step_with_intervals


class TestGarminToGenericWorkoutMapper:
    """Test suite for mapping Garmin workouts to generic workout format."""

    def test_workout_steps_count_matches(self, garmin_workout, generic_workout):
        """Test that the number of steps is preserved during mapping."""
        garmin_steps_count = len(garmin_workout.workoutSegments[0].workoutSteps)
        generic_steps_count = len(generic_workout.steps)

        assert generic_steps_count == garmin_steps_count

    def test_atomic_step_mapping(self, garmin_workout, generic_workout):
        """Test that a simple atomic step is correctly mapped."""
        first_garmin_step = garmin_workout.workoutSegments[0].workoutSteps[0]
        first_generic_step = generic_workout.steps[0]

        assert isinstance(first_generic_step, GenericAtomicStep)
        assert first_generic_step.step_id == 1
        assert first_generic_step.duration.total_seconds() == first_garmin_step.endConditionValue
        assert first_generic_step.power_zone == first_garmin_step.zoneNumber

    def test_step_with_intervals_mapping(self, garmin_workout, generic_workout):
        """Test that a step with intervals is correctly mapped."""
        garmin_step_with_intervals, generic_step_with_intervals = _get_step_with_intervals(garmin_workout,
                                                                                           generic_workout)
        if not garmin_step_with_intervals:
            return

        assert generic_step_with_intervals.step_id == garmin_step_with_intervals.stepOrder
        assert generic_step_with_intervals.iterations == garmin_step_with_intervals.numberOfIterations
        assert len(generic_step_with_intervals.steps) == len(garmin_step_with_intervals.workoutSteps)

    def test_interval_step_mapping(self, garmin_workout, generic_workout):
        """Test that individual interval steps within a repeat block are correctly mapped."""
        garmin_step_with_intervals, generic_step_with_intervals = _get_step_with_intervals(garmin_workout,
                                                                                           generic_workout)
        if not garmin_step_with_intervals:
            return

        garmin_interval_step = garmin_step_with_intervals.workoutSteps[1]
        generic_interval_step = generic_step_with_intervals.steps[1]

        assert isinstance(generic_interval_step, GenericIntervalStep)
        assert generic_interval_step.step_id == 2
        assert generic_interval_step.duration_in_seconds == garmin_interval_step.endConditionValue
        assert generic_interval_step.power_zone == garmin_interval_step.zoneNumber

    def test_scheduled_workout_mapping(self, garmin_workout, generic_workout):
        """Test that a scheduled workout is correctly mapped to generic workout."""
        garmin_scheduled_workout = GarminScheduledWorkout(
            workoutScheduleId=1,
            workout=garmin_workout,
            calendarDate=date(2025, 1, 1),
            createdDate=date(2024, 12, 1),
            ownerId=123
        )

        generic_scheduled_workout = GarminToGenericScheduledWorkoutMapper().map(garmin_scheduled_workout)

        generic_workout.scheduled_date = garmin_scheduled_workout.calendarDate
        assert generic_scheduled_workout.__eq__(garmin_workout)
