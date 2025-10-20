"""
DTOs (Data Transfer Objects) for MyWhoosh workout.
"""

from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class WorkoutStepMyWhoosh:
    IntervalId: int
    StepType: str
    Id: int
    WorkoutMessage: List[str]
    Rpm: float
    Power: float
    Pace: float
    StartPower: float
    EndPower: float
    Time: int
    IsManualGrade: bool
    ManualGradeValue: float
    ShowAveragePower: bool
    FlatRoad: int


@dataclass
class MyWhooshWorkout:
    Id: int
    Name: str
    Description: str
    Mode: str
    ERGMode: str
    IsRecovery: bool
    IsIntervals: bool
    FTPMode: str
    IsTT: bool
    IsTSS: bool
    IsIF: bool
    FTPMultiplier: float
    StressPoint: float
    Time: int
    CustomTagDescription: str
    CategoryId: int
    SubcategoryId: int
    Type: str
    DisplayType: str
    StepCount: int
    IsFavorite: bool
    CompletedCount: int
    WorkoutSteps: List[WorkoutStepMyWhoosh]
    AuthorName: str
    WokoutAssociationId: int
    IF: float
    TSS: float
    KJ: float

    def to_json(self) -> str:
        from pydantic.json import pydantic_encoder
        import json
        return json.dumps(self, default=pydantic_encoder)
