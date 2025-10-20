"""
DTOs (Data Transfer Objects) for Garmin API workout responses.
These mirror the exact structure from Garmin API.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic.dataclasses import dataclass


@dataclass
class GarminSportType:
    sportTypeId: Optional[int] = None
    sportTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None

    def to_enum(self) -> Optional[GarminSport]:
        if not self.sportTypeKey:
            return None
        key = self.sportTypeKey.strip().upper().replace(" ", "_")

        try:
            return GarminSport[key]
        except KeyError:
            return None


class GarminSport(Enum):
    CYCLING = "CYCLING"
    RUNNING = "RUNNING"
    CROSS_COUNTRY_SKIING = "CROSS_COUNTRY_SKIING"


@dataclass
class GarminSportType:
    sportTypeId: Optional[int] = None
    sportTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None


@dataclass
class GarminStepType:
    stepTypeId: Optional[int] = None
    stepTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None


@dataclass
class GarminConditionType:
    conditionTypeId: Optional[int] = None
    conditionTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None
    displayable: Optional[bool] = None


@dataclass
class GarminTargetType:
    workoutTargetTypeId: Optional[int] = None
    workoutTargetTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None


@dataclass
class GarminStrokeType:
    strokeTypeId: Optional[int] = None
    strokeTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None


@dataclass
class GarminEquipmentType:
    equipmentTypeId: Optional[int] = None
    equipmentTypeKey: Optional[str] = None
    displayOrder: Optional[int] = None


@dataclass
class GarminWorkoutStep:
    type: Optional[str] = None
    stepId: Optional[int] = None
    stepOrder: Optional[int] = None
    stepType: Optional[GarminStepType] = None
    childStepId: Optional[int] = None
    description: Optional[str] = None
    endCondition: Optional[GarminConditionType] = None
    endConditionValue: Optional[float] = None
    targetType: Optional[GarminTargetType] = None
    targetValueOne: Optional[float] = None
    targetValueTwo: Optional[float] = None
    zoneNumber: Optional[int] = None
    strokeType: Optional[GarminStrokeType] = None
    equipmentType: Optional[GarminEquipmentType] = None
    workoutSteps: Optional[List["GarminWorkoutStep"]] = None


@dataclass
class GarminWorkoutSegment:
    segmentOrder: Optional[int] = None
    sportType: Optional[GarminSportType] = None
    workoutSteps: Optional[List[GarminWorkoutStep]] = None


@dataclass
class GarminWorkout:
    workoutId: Optional[int] = None
    ownerId: Optional[int] = None
    workoutName: Optional[str] = None
    description: Optional[str] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None
    sportType: Optional[GarminSportType] = None
    trainingPlanId: Optional[int] = None
    workoutSegments: Optional[List[GarminWorkoutSegment]] = None
    workoutThumbnailUrl: Optional[str] = None
    workoutNameI18nKey: Optional[str] = None
    descriptionI18nKey: Optional[str] = None
    shared: Optional[bool] = None
