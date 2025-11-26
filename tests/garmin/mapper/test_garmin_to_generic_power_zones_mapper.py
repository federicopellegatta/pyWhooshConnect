import pytest

from pywhooshconnect.common.model.power_zones import PowerZones
from pywhooshconnect.garmin.mapper.garmin_to_generic_power_zones import (
    GarminToGenericPowerZonesMapper,
)
from pywhooshconnect.garmin.model.garmin_power_zones_dto import GarminPowerZones


@pytest.fixture
def garmin_power_zones() -> GarminPowerZones:
    """Map GarminWorkout to GenericWorkout."""
    return GarminPowerZones(
        functionalThresholdPower=200,
        zone1Floor=0,
        zone2Floor=110,
        zone3Floor=150,
        zone4Floor=180,
        zone5Floor=210,
        zone6Floor=240,
        zone7Floor=300,
        sport="CYCLING",
        userLocalTime=None,
    )


@pytest.fixture
def generic_power_zones(garmin_power_zones: GarminPowerZones) -> PowerZones:
    """Map GarminWorkout to GenericWorkout."""
    return GarminToGenericPowerZonesMapper().map(garmin_power_zones)


class TestGarminToPowerZonesMapper:
    """Test suite for mapping Garmin power zones to generic power zones format."""

    def test_ftp_mapping(self, garmin_power_zones, generic_power_zones):
        assert generic_power_zones.ftp == garmin_power_zones.functionalThresholdPower

    def test_zone_floor_mapping(self, generic_power_zones):
        assert generic_power_zones.z1_floor == 0.00  # 0 / 200 = 0.55
        assert generic_power_zones.z2_floor == 0.55  # 110 / 200 = 0.55
        assert generic_power_zones.z3_floor == 0.75  # 150 / 200 = 0.75
        assert generic_power_zones.z4_floor == 0.90  # 180 / 200 = 0.90
        assert generic_power_zones.z5_floor == 1.05  # 220 / 200 = 1.05
        assert generic_power_zones.z6_floor == 1.20  # 240 / 200 = 1.20
        assert generic_power_zones.z7_floor == 1.50  # 300 / 200 = 1.50
