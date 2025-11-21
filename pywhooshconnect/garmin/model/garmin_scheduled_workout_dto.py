"""
DTOs (Data Transfer Objects) for Garmin API scheduled workout responses.
These mirror the exact structure from Garmin API.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic.dataclasses import dataclass

from pywhooshconnect.garmin.model.garmin_workout_dto import GarminWorkout


@dataclass
class GarminScheduledWorkout:
    workoutScheduleId: int
    workout: GarminWorkout
    calendarDate: date
    createdDate: date
    ownerId: int
    newName: Optional[str] = None
    consumer: Optional[str] = None
    atpPlanTypeId: Optional[int] = None
    associatedActivityId: Optional[int] = None
    priority: Optional[int] = None
    associatedActivityDateTime: Optional[datetime] = None
    tpType: Optional[str] = None
    race: bool = False
    itp: bool = False
    nameChanged: bool = False
    protected: bool = False
