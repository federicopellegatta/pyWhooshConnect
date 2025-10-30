import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from src.common.mapper.base import PowerZonesOptions
from src.garmin.client.GarminClient import GarminClient
from src.garmin.mapper.garmin_to_generic_power_zones import GarminToGenericPowerZonesMapper
from src.garmin.mapper.garmin_to_generic_workout import GarminToGenericScheduledWorkoutMapper
from src.garmin.model.garmin_workout_dto import GarminSport
from src.garmin.service.garmin_training_plan_service import GarminTrainingPlanService
from src.mywhoosh.mapper.generic_to_mywhoosh import GenericToMyWhooshWorkoutMapper
from src.mywhoosh.model.mywhoosh_workout_dto import MyWhooshWorkout


class GarminToMyWhooshWorkoutSyncService:
    garminClient: GarminClient
    garmin_training_plan_service: GarminTrainingPlanService

    def __init__(self, garmin_client: GarminClient):
        self.garminClient = garmin_client
        self.garmin_training_plan_service = GarminTrainingPlanService(self.garminClient)

    @classmethod
    def from_credentials(cls, email: str, password: str):
        client = GarminClient(email, password)
        client.login()
        return cls(client)

    def sync_workouts(
            self,
            sport: GarminSport,
            from_date: datetime = datetime.today(),
            to_date: Optional[datetime] = None,
    ) -> List[MyWhooshWorkout]:
        # Retrieve Garmin workouts
        to_date = to_date if to_date is not None else (from_date + timedelta(days=7))
        garmin_workouts = self.garmin_training_plan_service.get_scheduled_workouts(
            sport=sport,
            from_date=from_date,
            to_date=to_date
        )

        # Retrieve Garmin power zones and create PowerZonesOptions
        garmin_power_zones = self.garmin_training_plan_service.get_power_zones_by_sport(sport=sport)
        power_zones = GarminToGenericPowerZonesMapper().map(garmin_power_zones)
        power_zones_options = PowerZonesOptions(power_zones=power_zones)

        # Map each Garmin workout to MyWhoosh format and return it
        mywhoosh_workouts = []
        for garmin_workout in garmin_workouts:
            generic_workout = GarminToGenericScheduledWorkoutMapper().map(garmin_workout)
            mywhoosh_workout = GenericToMyWhooshWorkoutMapper().map(generic_workout, power_zones_options)
            mywhoosh_workouts.append(mywhoosh_workout)

        return mywhoosh_workouts

    def sync_and_download_workouts(
            self,
            sport: GarminSport,
            from_date: datetime = datetime.today(),
            to_date: Optional[datetime] = None,
            output_dir: str = "~/downloads/",
    ):
        mywhoosh_workouts = self.sync_workouts(sport, from_date, to_date)

        # Map each Garmin workout to MyWhoosh format and save it
        for mywhoosh_workout in mywhoosh_workouts:
            data = json.loads(mywhoosh_workout.to_json())

            output_dir = Path(output_dir).expanduser()
            filename = output_dir.joinpath(f"{mywhoosh_workout.Name}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"Saved {filename}")
