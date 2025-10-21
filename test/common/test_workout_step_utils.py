from datetime import timedelta

from src.common.model.generic_workout import GenericAtomicStep, GenericStepWithIntervals, GenericWorkout


def test_step_container_add_remove_and_duration():
    step1 = GenericAtomicStep(step_id=1, _duration_in_seconds=60, power_zone=1, type="normal")
    step2 = GenericAtomicStep(step_id=2, _duration_in_seconds=120, power_zone=2, type="normal")

    # Create an interval step using step1
    interval_step = GenericStepWithIntervals(
        step_id=1,
        type="interval",
        steps=[step1],
        iterations=2
    )

    assert interval_step.duration_in_seconds == 120
    assert interval_step.duration() == timedelta(seconds=120)

    # Add step2
    interval_step.add_step(step2)
    assert len(interval_step.steps) == 2
    assert interval_step.steps[-1].step_id == 2
    assert interval_step.duration_in_seconds == (60 + 120) * 2

    # Remove last step
    interval_step.remove_step()
    assert len(interval_step.steps) == 1
    assert interval_step.steps[0].step_id == 1
    assert interval_step.duration_in_seconds == 60 * 2

    # test GenericWorkout
    workout = GenericWorkout(name="Test Workout", description="desc", steps=[step1])
    assert workout.steps[0].step_id == 1

    step3 = GenericAtomicStep(step_id=0, _duration_in_seconds=30, power_zone=1, type="warmup")
    workout.add_step(step3)
    assert len(workout.steps) == 2
    assert workout.steps[-1].step_id == 2
