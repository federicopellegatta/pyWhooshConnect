from datetime import datetime, date
from typing import Any, List

from garminconnect import Garmin

from src.garmin.model.garmin_workout_dto import GarminSport


def parse_datetime(date_str: str) -> datetime | None:
    return (
        datetime.strptime(date_str.replace(" ", ""), "%Y-%m-%dT%H:%M:%S.%f")
        if date_str
        else None
    )


def parse_date(date_str: str) -> date | None:
    return (
        datetime.strptime(date_str.replace(" ", ""), "%Y-%m-%d").date()
        if date_str
        else None
    )


class GarminClient(Garmin):
    def __init__(self, email: str, password: str):
        super().__init__(email, password)

    def get_training_plans(
        self, active: bool = False, sport: GarminSport = None
    ) -> List[dict[str, Any]]:
        """
        Retrieve all training plans, optionally filtering by active status and sport type.

        Args:
            active (bool, optional): If True, only return training plans that are currently active.
                A plan is considered active if today's date is between its start and end dates.
                Defaults to False.
            sport (GarminSport | None, optional): If provided, filter plans to only include
                the specified sport. Defaults to None (no sport filtering).

        Returns:
            List[dict[str, Any]]: A list of training plan dictionaries matching the specified filters.
        """
        training_plans = self.connectapi("/trainingplan-service/trainingplan/plans")[
            "trainingPlanList"
        ]

        if not active and sport is None:
            return training_plans

        today = datetime.today().date()

        return [
            t
            for t in training_plans
            if (
                not active
                or (
                    parse_datetime(t["startDate"]).date()
                    <= today
                    <= parse_datetime(t["endDate"]).date()
                )
            )
            and (sport is None or t["trainingType"]["typeKey"].upper() == sport.value)
        ]

    def get_power_zones(self) -> List[dict[str, Any]]:
        """Returns all available power zones"""
        return self.connectapi("/biometric-service/powerZones/sports/all")
