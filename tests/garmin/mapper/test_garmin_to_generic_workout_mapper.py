import json
from pathlib import Path

import pytest

from src.common.model.generic_workout import (
    GenericAtomicStep,
    GenericStepWithIntervals,
    GenericIntervalStep
)
from src.garmin.mapper.garmin_to_generic import GarminToGenericWorkoutMapper
from src.garmin.model.garmin_workout_dto import GarminWorkout


@pytest.fixture
def garmin_workout_json_path():
    """Path to the Garmin workout JSON test file."""
    return Path(__file__).parents[2] / "resources" / "garmin_workout.json"


@pytest.fixture
def garmin_workout(garmin_workout_json_path):
    """Load GarminWorkout from JSON file."""
    with open(garmin_workout_json_path, encoding="utf-8") as f:
        workout_data = json.load(f)
    return GarminWorkout(**workout_data)


@pytest.fixture
def generic_workout(garmin_workout):
    """Map GarminWorkout to GenericWorkout."""
    mapper = GarminToGenericWorkoutMapper()
    return mapper.map(garmin_workout)


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
        assert first_generic_step.type == first_garmin_step.stepType.stepTypeKey
        assert first_generic_step.power_zone == first_garmin_step.zoneNumber

    def test_step_with_intervals_mapping(self, garmin_workout, generic_workout):
        """Test that a step with intervals is correctly mapped."""
        garmin_step_with_intervals = garmin_workout.workoutSegments[0].workoutSteps[8]
        generic_step_with_intervals = generic_workout.get_step_by_id(
            garmin_step_with_intervals.stepOrder
        )

        assert isinstance(generic_step_with_intervals, GenericStepWithIntervals)
        assert generic_step_with_intervals.step_id == garmin_step_with_intervals.stepOrder
        assert generic_step_with_intervals.iterations == garmin_step_with_intervals.numberOfIterations
        assert len(generic_step_with_intervals.steps) == len(garmin_step_with_intervals.workoutSteps)

    def test_interval_step_mapping(self, garmin_workout, generic_workout):
        """Test that individual interval steps within a repeat block are correctly mapped."""
        garmin_step_with_intervals = garmin_workout.workoutSegments[0].workoutSteps[8]
        generic_step_with_intervals = generic_workout.get_step_by_id(
            garmin_step_with_intervals.stepOrder
        )

        assert isinstance(generic_step_with_intervals, GenericStepWithIntervals)

        garmin_interval_step = garmin_step_with_intervals.workoutSteps[1]
        generic_interval_step = generic_step_with_intervals.steps[1]

        assert isinstance(generic_interval_step, GenericIntervalStep)
        assert generic_interval_step.step_id == 2
        assert generic_interval_step.duration_in_seconds == garmin_interval_step.endConditionValue
        assert generic_interval_step.power_zone == garmin_interval_step.zoneNumber
