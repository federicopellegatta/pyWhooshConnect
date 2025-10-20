from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class GarminPowerZones:
    sport: str
    functionalThresholdPower: float
    zone1Floor: float
    zone2Floor: float
    zone3Floor: float
    zone4Floor: float
    zone5Floor: float
    zone6Floor: float
    zone7Floor: float
    userLocalTime: Optional[datetime]
