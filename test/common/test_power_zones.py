import math

import pytest

from src.common.model.power_zones import PowerZones


@pytest.fixture
def zones():
    """Create a PowerZones instance with FTP of 200W."""
    return PowerZones(ftp=200)


class TestPowerZones:
    def test_get_zone_returns_correct_range(self, zones):
        """Test that get_zone returns correct floor and ceiling ratios."""
        floor, ceiling = zones.get_zone(3)
        assert floor == 0.75
        assert ceiling == 0.90

    def test_get_zone_z7_has_high_ceiling(self, zones):
        """Test that Z7 has ceiling of 2.0."""
        floor, ceiling = zones.get_zone(7)
        assert floor == 1.50
        assert ceiling == math.inf

    def test_get_zone_invalid_raises_error(self, zones):
        """Test that invalid zone numbers raise ValueError."""
        with pytest.raises(ValueError, match="Zone must be between 1 and 7"):
            zones.get_zone(0)
        with pytest.raises(ValueError, match="Zone must be between 1 and 7"):
            zones.get_zone(8)

    def test_get_absolute_zone(self, zones):
        """Test that absolute zone returns correct wattage range."""
        floor_watts, ceiling_watts = zones.get_absolute_zone(4)
        assert floor_watts == 180  # 0.90 * 200
        assert ceiling_watts == 210  # 1.05 * 200

    def test_get_zone_by_ftp_ratio(self, zones):
        """Test that FTP ratio correctly identifies zones."""
        assert zones.get_zone_by_ftp_ratio(0.80) == 3
        assert zones.get_zone_by_ftp_ratio(1.00) == 4
        assert zones.get_zone_by_ftp_ratio(-0.1) == 0  # Below Z1

    def test_get_zone_by_power(self, zones):
        """Test that power values correctly identify zones."""
        assert zones.get_zone_by_power(160) == 3  # 0.80 FTP
        assert zones.get_zone_by_power(200) == 4  # 1.00 FTP
        assert zones.get_zone_by_power(300) == 7  # 1.50 FTP
        assert zones.get_zone_by_power(-10) == 0  # Below Z1

    def test_zone_floors_returns_all_zones(self, zones):
        """Test that zone_floors returns dictionary with all 7 zones."""
        floors = zones.zone_floors()
        assert len(floors) == 7
        assert floors[1] == 0
        assert floors[7] == 1.50
