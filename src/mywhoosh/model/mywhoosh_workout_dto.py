"""
DTOs (Data Transfer Objects) for MyWhoosh workout.
"""
import random
from dataclasses import field
from typing import List, Optional

from pydantic.dataclasses import dataclass


@dataclass
class MyWhooshWorkoutStep:
    IntervalId: int
    StepType: str
    Id: int
    WorkoutMessage: List[str]
    Rpm: float
    Power: Optional[float]
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
    Name: str
    Description: str
    StepCount: int
    Time: int
    WorkoutStepsArray: List[MyWhooshWorkoutStep]
    Id: int = field(default_factory=lambda: random.randint(1_000_000, 99_999_999))
    Mode: str = "E_Ride"
    ERGMode: str = "E_ON"
    IsRecovery: bool = False
    IsIntervals: bool = False
    FTPMode: str = "E_NoFTP"
    IsTT: bool = False
    IsTSS: bool = False
    IsIF: bool = False
    FTPMultiplier: float = 1
    StressPoint: float = 0
    CustomTagDescription: str = 2
    CategoryId: int = 200000000
    SubcategoryId: int = 1
    Type: str = "E_Normal"
    DisplayType: str = "E_Normal"
    IsFavorite: bool = False
    CompletedCount: int = 0
    AuthorName: str = "mywhoosh"
    WokoutAssociationId: int = 0
    IF: Optional[float] = None
    TSS: Optional[float] = None
    KJ: Optional[float] = None

    def to_json(self) -> str:
        from pydantic.json import pydantic_encoder
        import json
        return json.dumps(self, default=pydantic_encoder)
