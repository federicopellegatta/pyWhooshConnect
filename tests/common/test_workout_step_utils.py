from datetime import timedelta

import pytest

from src.common.model.generic_workout import (
    GenericAtomicStep,
    GenericStepWithIntervals,
    GenericWorkout,
    GenericIntervalStep,
)
from src.common.model.generic_workout_step import StepType


@pytest.fixture
def basic_interval_step():
    """Create a basic interval step of 60 seconds."""
    return GenericIntervalStep(
        step_id=1, duration_in_seconds=60, power_zone=1, type=StepType.INTERVAL
    )


@pytest.fixture
def second_interval_step():
    """Create a second interval step of 120 seconds."""
    return GenericIntervalStep(
        step_id=2, duration_in_seconds=120, power_zone=2, type=StepType.INTERVAL
    )


@pytest.fixture
def warmup_step():
    """Create a warmup atomic step of 30 seconds."""
    return GenericAtomicStep(
        step_id=0, duration_in_seconds=30, power_zone=1, type=StepType.WARM_UP
    )


class TestGenericStepWithIntervals:
    def test_duration_calculation_with_iterations(self, basic_interval_step):
        """Test that duration is correctly multiplied by iterations."""
        interval_step = GenericStepWithIntervals(
            step_id=1, type=StepType.INTERVAL, steps=[basic_interval_step], iterations=2
        )

        assert interval_step.duration_in_seconds == 120
        assert interval_step.duration == timedelta(seconds=120)

    def test_add_step_updates_duration(self, basic_interval_step, second_interval_step):
        """Test that adding a step updates the total duration correctly."""
        interval_step = GenericStepWithIntervals(
            step_id=1, type=StepType.INTERVAL, steps=[basic_interval_step], iterations=2
        )

        interval_step.add_step(second_interval_step)

        assert len(interval_step.steps) == 2
        assert interval_step.steps[-1].step_id == 2
        assert interval_step.duration_in_seconds == (60 + 120) * 2

    def test_remove_step_updates_duration(
        self, basic_interval_step, second_interval_step
    ):
        """Test that removing a step updates the total duration correctly."""
        interval_step = GenericStepWithIntervals(
            step_id=1,
            type=StepType.INTERVAL,
            steps=[basic_interval_step, second_interval_step],
            iterations=2,
        )

        interval_step.remove_step()

        assert len(interval_step.steps) == 1
        assert interval_step.steps[0].step_id == 1
        assert interval_step.duration_in_seconds == 60 * 2


class TestGenericWorkout:
    def test_initialization_with_step(self, basic_interval_step):
        """Test that workout is correctly initialized with a step."""
        workout = GenericWorkout(
            name="Test Workout", description="desc", steps=[basic_interval_step]
        )

        assert workout.steps[0].step_id == 1

    def test_add_step_assigns_correct_id(self, basic_interval_step, warmup_step):
        """Test that add_step automatically assigns the correct step_id."""
        workout = GenericWorkout(
            name="Test Workout", description="desc", steps=[basic_interval_step]
        )

        workout.add_step(warmup_step)

        assert len(workout.steps) == 2
        assert workout.steps[-1].step_id == 2
