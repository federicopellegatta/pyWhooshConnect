from datetime import datetime

import pytest

from src.common.mapper.base import PowerZonesOptions
from src.common.model.generic_workout import (
    GenericWorkout,
    GenericAtomicStep,
    GenericStepWithIntervals,
    GenericIntervalStep
)
from src.common.model.generic_workout_step import StepType
from src.common.model.power_zones import PowerZones
from src.mywhoosh.mapper.generic_to_mywhoosh import (
    GenericToMyWhooshPowerMapper,
    GenericToMyWhooshStepMapper,
    GenericToMyWhooshWorkoutStepMapper
)


@pytest.fixture
def power_zones():
    return PowerZones(ftp=300)


@pytest.fixture
def power_zones_options(power_zones):
    return PowerZonesOptions(power_zones=power_zones)


@pytest.fixture
def simple_workout():
    """Fixture for a simple workout with a single step"""
    return GenericWorkout(
        name="Test Workout",
        description="A test workout",
        scheduled_date=datetime(2025, 1, 1),
        steps=[
            GenericAtomicStep(
                step_id=1,
                duration_in_seconds=300,
                power_zone=3,
                rpm=90,
                type=StepType.INTERVAL,
                description="Warm up"
            )
        ]
    )


@pytest.fixture
def complex_workout():
    """Fixture for a complex workout with intervals"""
    return GenericWorkout(
        name="Complex Workout!",
        description="A complex test workout",
        scheduled_date=datetime(2025, 1, 1),
        steps=[
            GenericAtomicStep(
                step_id=1,
                duration_in_seconds=300,
                power_zone=2,
                rpm=85,
                type=StepType.WARM_UP,
                description="Warm up"
            ),
            GenericStepWithIntervals(
                step_id=2,
                steps=[
                    GenericIntervalStep(
                        step_id=3,
                        duration_in_seconds=120,
                        power_zone=5,
                        rpm=100,
                        type=StepType.INTERVAL,
                        description="Hard interval"
                    ),
                    GenericIntervalStep(
                        step_id=4,
                        duration_in_seconds=60,
                        power_zone=2,
                        rpm=80,
                        type=StepType.RECOVERY,
                        description="Recovery"
                    )
                ],
                iterations=3,
                type=StepType.INTERVAL
            ),
            GenericAtomicStep(
                step_id=5,
                duration_in_seconds=300,
                power_zone=1,
                rpm=70,
                type=StepType.COOL_DOWN,
                description="Cool down"
            )
        ]
    )


class TestGenericToMyWhooshPowerMapper:

    def test_map_zone_middle_value(self, power_zones_options):
        mapper = GenericToMyWhooshPowerMapper()
        result = mapper.map(3, power_zones_options)
        # Zone 3: (0.75, 0.90), weight 0.5
        assert result == 0.825

    def test_map_zone_1(self, power_zones_options):
        mapper = GenericToMyWhooshPowerMapper()
        result = mapper.map(1, power_zones_options)
        # Zone 1: (0, 0.55)
        assert result == 0.275

    def test_map_zone_7(self, power_zones_options):
        mapper = GenericToMyWhooshPowerMapper()
        result = mapper.map(7, power_zones_options)
        # Zone 7: (1.50, inf)
        assert result == (1.50 * 1.1)

    def test_map_without_power_zones_raises_error(self):
        mapper = GenericToMyWhooshPowerMapper()
        options = PowerZonesOptions(power_zones=None)

        with pytest.raises(RuntimeError, match="No power zones specified"):
            mapper.map(3, options)


class TestGenericToMyWhooshStepMapper:

    def test_map_atomic_step_normal(self, power_zones_options):
        mapper = GenericToMyWhooshStepMapper()
        step = GenericAtomicStep(
            step_id=1,
            duration_in_seconds=300,
            power_zone=3,
            rpm=90,
            type=StepType.INTERVAL,
            description="Test step"
        )

        result = mapper.map(step, power_zones_options)

        assert len(result) == 1
        assert result[0].Id == 1
        assert result[0].StepType == "E_Normal"
        assert result[0].Time == 300
        assert result[0].Rpm == 90
        assert result[0].Power == 0.825
        assert result[0].WorkoutMessage == ["Test step"]

    def test_map_atomic_step_free_ride(self, power_zones_options):
        mapper = GenericToMyWhooshStepMapper()
        step = GenericAtomicStep(
            step_id=2,
            duration_in_seconds=600,
            power_zone=2,
            rpm=0,
            type=StepType.FREE_RIDE,
            description=None
        )

        result = mapper.map(step, power_zones_options)

        assert len(result) == 1
        assert result[0].StepType == "E_FreeRide"
        assert result[0].Rpm == 0
        assert result[0].WorkoutMessage == []

    def test_map_interval_step(self, power_zones_options):
        mapper = GenericToMyWhooshStepMapper()
        step = GenericIntervalStep(
            step_id=3,
            duration_in_seconds=120,
            power_zone=5,
            rpm=100,
            type=StepType.INTERVAL,
            description="Interval"
        )

        result = mapper.map(step, power_zones_options)

        assert len(result) == 1
        assert result[0].Power == 1.125

    def test_map_step_with_intervals(self, power_zones_options):
        mapper = GenericToMyWhooshStepMapper()
        step = GenericStepWithIntervals(
            step_id=1,
            steps=[
                GenericIntervalStep(
                    step_id=2,
                    duration_in_seconds=120,
                    power_zone=5,
                    rpm=100,
                    type=StepType.INTERVAL,
                    description="Hard"
                ),
                GenericIntervalStep(
                    step_id=3,
                    duration_in_seconds=60,
                    power_zone=2,
                    rpm=80,
                    type=StepType.INTERVAL,
                    description="Easy"
                )
            ],
            iterations=2,
            type=StepType.INTERVAL
        )

        result = mapper.map(step, power_zones_options)

        assert len(result) == 4  # 2 steps * 2 iterations
        assert result[0].Id == 2
        assert result[1].Id == 3
        assert result[2].Id == 2
        assert result[3].Id == 3

    def test_map_step_with_intervals_respects_iterations(self, power_zones_options):
        """Test that iterations are correctly expanded"""
        mapper = GenericToMyWhooshStepMapper()
        step = GenericStepWithIntervals(
            step_id=1,
            steps=[
                GenericIntervalStep(
                    step_id=10,
                    duration_in_seconds=120,
                    power_zone=5,
                    rpm=100,
                    type=StepType.INTERVAL,
                    description="Hard"
                )
            ],
            iterations=3,
            type=StepType.INTERVAL
        )

        result = mapper.map(step, power_zones_options)

        assert len(result) == 3  # 1 step * 3 iterations
        # All should have the same original step_id
        assert all(step.Id == 10 for step in result)


class TestGenericToMyWhooshWorkoutStepMapper:

    def test_map_simple_workout(self, simple_workout, power_zones_options):
        mapper = GenericToMyWhooshWorkoutStepMapper()

        result = mapper.map(simple_workout, power_zones_options)

        assert result.Name == "20250101 TestWorkout"
        assert result.Description == "A test workout"
        assert len(result.WorkoutSteps) == 1
        assert result.WorkoutSteps[0].Id == 1  # Should be reindexed to 1
        assert result.StepCount == 1
        assert result.Time == 300
        assert result.AuthorName == "Garmin powered by pyWhooshGarmin"

    def test_map_complex_workout(self, complex_workout, power_zones_options):
        mapper = GenericToMyWhooshWorkoutStepMapper()

        result = mapper.map(complex_workout, power_zones_options)

        assert result.Name == "20250101 ComplexWorkout"
        assert result.Description == "A complex test workout"
        # 1 warm up + (2 interval steps * 3 iterations) + 1 cool down = 8 steps
        assert len(result.WorkoutSteps) == 8
        assert result.StepCount == 8
        assert result.AuthorName == "Garmin powered by pyWhooshGarmin"

    def test_map_workout_reindexes_step_ids_sequentially(self, power_zones_options):
        """Test that step IDs are reindexed sequentially starting from 1"""
        workout = GenericWorkout(
            name="Reindex Test",
            description="Test",
            scheduled_date=None,
            steps=[
                GenericAtomicStep(
                    step_id=100,
                    duration_in_seconds=100,
                    power_zone=1,
                    rpm=70,
                    type=StepType.INTERVAL
                ),
                GenericAtomicStep(
                    step_id=200,
                    duration_in_seconds=200,
                    power_zone=2,
                    rpm=80,
                    type=StepType.INTERVAL
                ),
                GenericAtomicStep(
                    step_id=300,
                    duration_in_seconds=300,
                    power_zone=3,
                    rpm=90,
                    type=StepType.INTERVAL
                )
            ]
        )

        mapper = GenericToMyWhooshWorkoutStepMapper()
        result = mapper.map(workout, power_zones_options)

        # IDs should be reindexed to 1, 2, 3
        assert result.WorkoutSteps[0].Id == 1
        assert result.WorkoutSteps[1].Id == 2
        assert result.WorkoutSteps[2].Id == 3

    def test_map_workout_reindexes_after_flattening_intervals(self, power_zones_options):
        """Test that step IDs are reindexed after flattening interval repetitions"""
        workout = GenericWorkout(
            name="Flatten Test",
            description="Test interval flattening and reindexing",
            scheduled_date=None,
            steps=[
                GenericAtomicStep(
                    step_id=1,
                    duration_in_seconds=300,
                    power_zone=2,
                    rpm=85,
                    type=StepType.WARM_UP
                ),
                GenericStepWithIntervals(
                    step_id=2,
                    steps=[
                        GenericIntervalStep(
                            step_id=10,
                            duration_in_seconds=120,
                            power_zone=5,
                            rpm=100,
                            type=StepType.INTERVAL
                        ),
                        GenericIntervalStep(
                            step_id=20,
                            duration_in_seconds=60,
                            power_zone=2,
                            rpm=80,
                            type=StepType.RECOVERY
                        )
                    ],
                    iterations=2,
                    type=StepType.INTERVAL
                ),
                GenericAtomicStep(
                    step_id=3,
                    duration_in_seconds=300,
                    power_zone=1,
                    rpm=70,
                    type=StepType.COOL_DOWN
                )
            ]
        )

        mapper = GenericToMyWhooshWorkoutStepMapper()
        result = mapper.map(workout, power_zones_options)

        # Should have: 1 warm-up + 4 intervals (2 steps * 2 iterations) + 1 cool-down = 6 steps
        assert len(result.WorkoutSteps) == 6
        assert result.StepCount == 6

        # IDs should be sequential from 1 to 6
        expected_ids = [1, 2, 3, 4, 5, 6]
        actual_ids = [step.Id for step in result.WorkoutSteps]
        assert actual_ids == expected_ids

    def test_map_workout_calculates_total_time(self, power_zones_options):
        workout = GenericWorkout(
            name="Time Test",
            description="Test",
            scheduled_date=None,
            steps=[
                GenericAtomicStep(
                    step_id=1,
                    duration_in_seconds=300,
                    power_zone=2,
                    rpm=80,
                    type=StepType.INTERVAL
                ),
                GenericAtomicStep(
                    step_id=2,
                    duration_in_seconds=600,
                    power_zone=3,
                    rpm=90,
                    type=StepType.INTERVAL
                )
            ]
        )

        mapper = GenericToMyWhooshWorkoutStepMapper()
        result = mapper.map(workout, power_zones_options)

        assert result.Time == 900  # 300 + 600

    def test_map_workout_with_multiple_interval_blocks(self, power_zones_options):
        """Test workout with multiple interval blocks to ensure correct flattening and reindexing"""
        workout = GenericWorkout(
            name="Multi Interval Test",
            description="Test multiple interval blocks",
            scheduled_date=None,
            steps=[
                GenericStepWithIntervals(
                    step_id=1,
                    steps=[
                        GenericIntervalStep(
                            step_id=1,
                            duration_in_seconds=40,
                            power_zone=5,
                            rpm=90,
                            type=StepType.INTERVAL
                        ),
                        GenericIntervalStep(
                            step_id=2,
                            duration_in_seconds=20,
                            power_zone=2,
                            type=StepType.RECOVERY
                        )
                    ],
                    iterations=2,
                    type=StepType.INTERVAL
                ),
                GenericStepWithIntervals(
                    step_id=2,
                    steps=[
                        GenericIntervalStep(
                            step_id=1,
                            duration_in_seconds=120,
                            power_zone=5,
                            rpm=95,
                            type=StepType.INTERVAL
                        )
                    ],
                    iterations=3,
                    type=StepType.INTERVAL
                )
            ]
        )

        mapper = GenericToMyWhooshWorkoutStepMapper()
        result = mapper.map(workout, power_zones_options)

        # Should have: 2 intervals from first block + 3 intervals from second block = 5 steps
        assert len(result.WorkoutSteps) == 7
        assert result.StepCount == 7

        # IDs should be sequential from 1 to 5
        expected_ids = [1, 2, 3, 4, 5, 6, 7]
        actual_ids = [step.Id for step in result.WorkoutSteps]
        assert actual_ids == expected_ids