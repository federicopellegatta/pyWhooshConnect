from typing import Optional

from pywhooshconnect.common.mapper.base import BaseMapper, MapperOptions
from pywhooshconnect.common.model.power_zones import PowerZones
from pywhooshconnect.garmin.model.garmin_power_zones_dto import GarminPowerZones


def _calculate_zone_floor(zone: int, garmin: GarminPowerZones):
    mapping = {
        1: garmin.zone1Floor,
        2: garmin.zone2Floor,
        3: garmin.zone3Floor,
        4: garmin.zone4Floor,
        5: garmin.zone5Floor,
        6: garmin.zone6Floor,
        7: garmin.zone7Floor,
    }

    return mapping[zone] / garmin.functionalThresholdPower


class GarminToGenericPowerZonesMapper(BaseMapper[GarminPowerZones, PowerZones]):
    def map(
        self, garmin: GarminPowerZones, options: Optional[MapperOptions] = None
    ) -> PowerZones:
        return PowerZones(
            ftp=int(garmin.functionalThresholdPower),
            z1_floor=_calculate_zone_floor(1, garmin),
            z2_floor=_calculate_zone_floor(2, garmin),
            z3_floor=_calculate_zone_floor(3, garmin),
            z4_floor=_calculate_zone_floor(4, garmin),
            z5_floor=_calculate_zone_floor(5, garmin),
            z6_floor=_calculate_zone_floor(6, garmin),
            z7_floor=_calculate_zone_floor(7, garmin),
        )
