from datetime import date, datetime, timedelta
from typing import Any

from src.garmin.client.GarminClient import GarminClient, parse_datetime, parse_date
from src.garmin.model.GarminSport import GarminSport


class GarminTrainingPlanService:
    def __init__(self, garmin_client: GarminClient):
        self.client = garmin_client

    def get_scheduled_workouts(
            self,
            sport: GarminSport,
            from_date: date | datetime | None = None,
            to_date: date | datetime | None = None
    ) -> list[dict[str, Any]]:
        """
        Get scheduled workouts for a specific sport within a date range.

        Args:
            sport: Sport type to filter by
            from_date: Start date (inclusive). Defaults to today.
            to_date: End date (inclusive). Defaults to 90 days from start.

        Returns:
            List of scheduled workout details
        """

        # Normalize dates
        from_date = from_date.date() if isinstance(from_date, datetime) else from_date or date.today()
        to_date = to_date.date() if isinstance(to_date, datetime) else to_date or from_date + timedelta(days=90)
        print(f"Fetching workouts for {sport.value} from {from_date} to {to_date}")

        # Get active plans
        plans = self.client.get_training_plans(active=True, sport=sport)
        if not plans:
            return []

        # Extract and filter scheduled workouts for each training plan
        scheduled_workouts = []
        for plan in plans:
            plan_detail = self.client.get_training_plan_by_id(plan["trainingPlanId"])

            for task in plan_detail.get("taskList", []):
                task_workout = task["taskWorkout"]
                if not task_workout or not task_workout.get("workoutId"): # exclude rest days
                    continue

                workout_date = parse_date(task["calendarDate"]) or parse_datetime(task_workout["scheduledDate"]).date()

                if from_date <= workout_date <= to_date:
                    workout = self.client.get_workout_by_id(task_workout["workoutId"])
                    scheduled_workouts.append(workout)

        return scheduled_workouts

    def get_power_zones_by_sport(self, sport: GarminSport) -> dict[str, Any]:
        """
        Returns the power zones configuration for a specific sport.

        Retrieves all available power zones and filters them by the given sport.

        Args:
            sport (GarminSport): The sport for which to retrieve power zones.
                Must be a member of the GarminSport enum (e.g., RUNNING, CYCLING).

        Returns:
            dict[str, Any] | None: A dictionary representing the power zones for the
            specified sport, or None if no power zones are found for that sport.
        """
        power_zones = self.client.get_power_zones()
        return next((p for p in power_zones if p["sport"] == sport.name), None)