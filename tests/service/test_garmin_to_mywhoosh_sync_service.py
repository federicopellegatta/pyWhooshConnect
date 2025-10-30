import json
from datetime import datetime
from pathlib import Path

import pytest

from src.garmin.model.garmin_workout_dto import GarminSport
from src.service.workout_sync_service import GarminToMyWhooshWorkoutSyncService


def json_path(filename: str) -> Path:
    """Path to the Garmin workout JSON test file."""
    return Path(__file__).parents[1] / "resources" / "garmin" / filename


def load_file(filename: str):
    with open(json_path(filename), encoding="utf-8") as f:
        return json.load(f)


class TestGarminToMyWhooshWorkoutSyncService:

    @pytest.fixture
    def mock_client(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_client):
        return GarminToMyWhooshWorkoutSyncService(mock_client)

    def test_sync_workouts(self, service, mock_client):
        # Arrange
        mock_client.get_training_plans.return_value = load_file("garmin_training_plan_list.json")
        mock_client.get_training_plan_by_id.return_value = load_file("training_plan_details.json")
        mock_client.get_scheduled_workout_by_id.side_effect = lambda scheduled_workout_id: load_file(
            f"garmin_scheduled_workout_{scheduled_workout_id}.json"
        )
        mock_client.get_power_zones.return_value = load_file("garmin_power_zones.json")

        # Act
        mywhoosh_workouts = service.sync_workouts(
            sport=GarminSport.CYCLING,
            from_date=datetime(2025, 10, 29),
            to_date=datetime(2025, 11, 2)
        )

        # Assert
        assert len(mywhoosh_workouts) == 2
