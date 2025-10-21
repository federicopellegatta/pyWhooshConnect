from dataclasses import dataclass


def _validate_zone(zone: int) -> None:
    if zone < 1 or zone > 7:
        raise ValueError("Zone must be between 1 and 7")


@dataclass
class PowerZones:
    """Power zones based on FTP (Functional Threshold Power) ratios.

    Each zone floor represents the minimum FTP ratio for that zone.
    Typically: Z1 (recovery), Z2 (endurance), Z3 (tempo), Z4 (threshold),
    Z5 (VO2max), Z6 (anaerobic), Z7 (neuromuscular).
    """
    ftp: int
    z1_floor: float = 0
    z2_floor: float = 0.55
    z3_floor: float = 0.75
    z4_floor: float = 0.90
    z5_floor: float = 1.05
    z6_floor: float = 1.20
    z7_floor: float = 1.50

    def get_zone(self, zone: int) -> tuple[float, float]:
        """Get the FTP ratio range (floor, ceiling) for a specific zone.

        Args:
            zone: Zone number (1-7)

        Returns:
            Tuple of (floor_ratio, ceiling_ratio) for the zone

        Raises:
            ValueError: If zone is not between 1 and 7
        """
        _validate_zone(zone)

        zone_floors = self.zone_floors()
        floor_ratio = zone_floors[zone]

        # Ceiling is the floor of the next zone, or a high value for Z7
        if zone < 7:
            ceiling_ratio = zone_floors[zone + 1]
        else:
            # Z7 has no upper limit, use a reasonable maximum
            ceiling_ratio = 2.0

        return floor_ratio, ceiling_ratio

    def get_absolute_zone(self, zone: int) -> tuple[int, int]:
        """Get the absolute power range (in watts) for a specific zone.

        Args:
            zone: Zone number (1-7)

        Returns:
            Tuple of (floor_watts, ceiling_watts) for the zone

        Raises:
            ValueError: If zone is not between 1 and 7
        """
        floor_ratio, ceiling_ratio = self.get_zone(zone)
        floor_watts = int(floor_ratio * self.ftp)
        ceiling_watts = int(ceiling_ratio * self.ftp)

        return floor_watts, ceiling_watts

    def get_zone_by_ftp_ratio(self, ftp_ratio: float) -> int:
        """Determine which zone a given FTP ratio belongs to.

        Args:
            ftp_ratio: Power as a ratio of FTP (e.g., 0.85 for 85% FTP)

        Returns:
            Zone number (1-7), or 0 if below Z1
        """
        for zone in range(7, 0, -1):
            if ftp_ratio >= self.zone_floors()[zone]:
                return zone
        return 0

    def get_zone_by_power(self, power: float) -> int:
        """Determine which zone a given power output belongs to.

        Args:
            power: Power output in watts

        Returns:
            Zone number (1-7), or 0 if below Z1
        """
        power_ftp_ratio = power / self.ftp
        return self.get_zone_by_ftp_ratio(power_ftp_ratio)

    def zone_floors(self) -> dict[int, float]:
        """Get all zone floors as a dictionary."""
        return {
            1: self.z1_floor,
            2: self.z2_floor,
            3: self.z3_floor,
            4: self.z4_floor,
            5: self.z5_floor,
            6: self.z6_floor,
            7: self.z7_floor
        }
