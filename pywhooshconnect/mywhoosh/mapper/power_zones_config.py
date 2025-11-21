from datetime import timedelta
from pathlib import Path
from typing import Dict

import yaml


class PowerZoneConfigurationError(Exception):
    """Raised when the power zone configuration is invalid."""

    pass


def _load_config(config_path: str) -> dict:
    """Load YAML configuration file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as file:
        return yaml.safe_load(file)


class PowerZoneConfig:
    """Configuration for power zone mapping with defaults"""

    # Default values if config file is missing or incomplete
    DEFAULT_ZONE_WEIGHT = 0.5
    DEFAULT_ZONE7_MULTIPLIER = 1.1
    DEFAULT_LAP_BUTTON_DURATION_SECONDS = 30

    def __init__(self, config_path: str = None, config_dict: dict = None):
        """
        Initialize the PowerZoneConfig object.

        The configuration can be loaded either from a YAML file or directly from a dictionary.
        If both `config_path` and `config_dict` are provided, `config_dict` takes precedence.

        Parameters
        ----------
        config_path : str, optional
            Path to the YAML configuration file containing power zone settings.
            Defaults to "config/power_zones_config.yml" relative to the project root if not
            provided.
        config_dict : dict, optional
            Dictionary containing power zone configuration. If provided, this will be used
            instead of loading from a file.

        Notes
        -----
        - Zone 7 is treated specially and cannot have a direct weight defined.
        - If the configuration file is missing or incomplete, default values are used.
        """
        if config_dict is not None:
            self.config = config_dict
        else:
            if config_path is None:
                project_root = Path(__file__).parent.parent.parent.parent
                config_path = project_root / "config" / "power_zones_config.yml"

            try:
                self.config = _load_config(config_path)
            except FileNotFoundError:
                self.config = {}

        try:
            power_zones = self.config.get("power_zones", {})
            self.default_zone_weight = power_zones.get(
                "default_zone_weight", self.DEFAULT_ZONE_WEIGHT
            )
            self.zone_weights = self._parse_zone_weights()
        except FileNotFoundError:
            # Use defaults if config file doesn't exist
            self.config = {}
            self.default_zone_weight = self.DEFAULT_ZONE_WEIGHT
            self.zone_weights = {}

    def _parse_zone_weights(self) -> Dict[int, float]:
        """Extract per-zone weights from config"""
        zones_config = self.config.get("power_zones", {}).get("zones", {})
        zone_weights = {}

        for zone_num, zone_config in zones_config.items():
            if "weight" in zone_config:
                if zone_num == 7:
                    raise PowerZoneConfigurationError(
                        "Invalid configuration: Zone 7 cannot specify a weight. Use a multiplier instead."
                    )

                weight = zone_config["weight"]
                if not (0 <= weight <= 1):
                    raise PowerZoneConfigurationError(
                        f"Invalid weight for zone {zone_num}: must be between 0 and 1, got {weight}"
                    )
                zone_weights[zone_num] = zone_config["weight"]

        return zone_weights

    def get_zone_weight(self, zone: int) -> float:
        """Get weight for specific zone, falling back to default"""
        return self.zone_weights.get(zone, self.default_zone_weight)

    def get_zone7_multiplier(self) -> float:
        """Get multiplier for zone 7, with optional override"""
        zones_config = self.config.get("power_zones", {}).get("zones", {})
        zone7_multiplier = zones_config.get(7, {}).get(
            "multiplier", self.DEFAULT_ZONE7_MULTIPLIER
        )
        if zone7_multiplier < 1:
            raise PowerZoneConfigurationError(
                f"Invalid multiplier for zone 7: must be greater than or equal to 1, got {zone7_multiplier}"
            )
        return zone7_multiplier

    def get_lap_button_duration(self) -> timedelta:
        """Get the lap button duration from config"""
        lap_button_duration_seconds = self.config.get(
            "lap_button_duration_seconds", self.DEFAULT_LAP_BUTTON_DURATION_SECONDS
        )
        return timedelta(seconds=lap_button_duration_seconds)
