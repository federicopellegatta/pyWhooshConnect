import json
from datetime import date
from pathlib import Path
from typing import List

import pytest

from src.garmin.model.garmin_power_zones_dto import GarminPowerZones
from src.garmin.model.garmin_scheduled_workout_dto import GarminScheduledWorkout
from src.garmin.model.garmin_workout_dto import GarminSport, GarminWorkout
from src.garmin.service.garmin_training_plan_service import GarminTrainingPlanService


def json_path(filename: str) -> Path:
    """Path to the Garmin workout JSON test file."""
    return Path(__file__).parents[2] / "resources" / "garmin" / filename


def garmin_workout(filename: str) -> GarminWorkout:
    """Load GarminWorkout from JSON file."""
    with open(json_path(filename), encoding="utf-8") as f:
        workout_data = json.load(f)
    return GarminWorkout(**workout_data)


def garmin_power_zones(filename: str) -> List[GarminPowerZones]:
    """Load GarminPowerZones  from JSON file."""
    with open(json_path(filename), encoding="utf-8") as f:
        power_zones_data = json.load(f)
    return [GarminPowerZones(**item) for item in power_zones_data]


class TestGarminTrainingPlanService:

    @pytest.fixture
    def mock_client(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_client):
        return GarminTrainingPlanService(mock_client)

    def test_get_scheduled_workouts_no_active_plans(self, service, mock_client):
        # Arrange
        mock_client.get_training_plans.return_value = []

        # Act
        result = service.get_scheduled_workouts(sport=GarminSport.CYCLING)

        # Assert
        assert result == []
        mock_client.get_training_plans.assert_called_once()
        mock_client.get_training_plan_by_id.assert_not_called()

    def test_get_scheduled_workouts_with_active_plans(self, service, mock_client):
        from_date = date(2025, 1, 1)
        to_date = date(2025, 1, 31)

        mock_client.get_training_plans.return_value = [
            {"trainingPlanId": "Training Plan Name"}
        ]

        workout = garmin_workout("garmin_workout.json")
        mock_client.get_training_plan_by_id.return_value = {
            "taskList": [
                {
                    "calendarDate": "2025-01-15",
                    "taskWorkout": {
                        "workoutId": workout.workoutId,
                        "workoutScheduleId": 12345,
                        "scheduledDate": "2025-01-15T10:00:00",
                    },
                }
            ]
        }

        mock_client.get_scheduled_workout_by_id.return_value = GarminScheduledWorkout(
            workoutScheduleId=12345,
            workout=workout,
            calendarDate=date(2025, 1, 15),
            createdDate=date(2025, 1, 15),
            ownerId=1,
        ).__dict__

        # Act
        result = service.get_scheduled_workouts(
            sport=GarminSport.CYCLING, from_date=from_date, to_date=to_date
        )

        # Assert
        assert len(result) == 1
        mock_client.get_training_plans.assert_called_once_with(
            active=True, sport=GarminSport.CYCLING
        )
        mock_client.get_training_plan_by_id.assert_called_once_with(
            "Training Plan Name"
        )
        mock_client.get_scheduled_workout_by_id.assert_called_once_with(12345)

    def test_get_power_zones_by_sport(self, service, mock_client):
        # Arrange
        mock_client.get_power_zones.return_value = [
            p.__dict__ for p in garmin_power_zones("garmin_power_zones.json")
        ]

        # Act
        result = service.get_power_zones_by_sport(GarminSport.CYCLING)

        # Assert
        assert result is not None
        assert result.sport == "CYCLING"
        mock_client.get_power_zones.assert_called_once()
