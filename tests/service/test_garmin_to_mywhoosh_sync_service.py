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
    """Load JSON test data from resources directory."""
    with open(json_path(filename), encoding="utf-8") as f:
        return json.load(f)


class TestGarminToMyWhooshWorkoutSyncService:

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock Garmin client."""
        return mocker.Mock()

    @pytest.fixture
    def service(self, mock_client):
        """Create service instance with mocked client."""
        return GarminToMyWhooshWorkoutSyncService(mock_client)

    @pytest.fixture
    def mock_workouts_data(self, mock_client):
        """Setup mock responses for Garmin API calls."""
        mock_client.get_training_plans.return_value = load_file(
            "garmin_training_plan_list.json"
        )
        mock_client.get_training_plan_by_id.return_value = load_file(
            "training_plan_details.json"
        )
        mock_client.get_scheduled_workout_by_id.side_effect = (
            lambda scheduled_workout_id: load_file(
                f"garmin_scheduled_workout_{scheduled_workout_id}.json"
            )
        )
        mock_client.get_power_zones.return_value = load_file("garmin_power_zones.json")

    def test_sync_workouts(self, service, mock_workouts_data):
        """Test that workouts are correctly synchronized and converted to MyWhoosh format."""
        mywhoosh_workouts = service.sync_workouts(
            sport=GarminSport.CYCLING,
            from_date=datetime(2025, 10, 29),
            to_date=datetime(2025, 11, 2),
        )

        assert len(mywhoosh_workouts) == 2

    def test_sync_and_download_workouts(self, service, mock_workouts_data, mocker):
        """Test that workouts are synchronized and files are created without writing to disk."""
        # Mock file operations to prevent actual file writes
        mock_file = mocker.mock_open()
        mocker.patch("src.service.workout_sync_service.open", mock_file)

        output_dir = "~/downloads/"

        service.sync_and_download_workouts(
            sport=GarminSport.CYCLING,
            from_date=datetime(2025, 10, 29),
            to_date=datetime(2025, 11, 2),
            output_dir=output_dir,
        )

        # Verify two files were opened for writing
        assert mock_file.call_count == 2

        # Verify file paths are correct
        calls = mock_file.call_args_list
        for call in calls:
            filepath = call[0][0]
            assert str(filepath).startswith(str(Path(output_dir).expanduser()))
            assert str(filepath).endswith(".json")
