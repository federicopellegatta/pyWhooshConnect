from pathlib import Path

import pytest
import yaml

from src.mywhoosh.mapper.power_zones_config import PowerZoneConfig, PowerZoneConfigurationError


def write_yaml(tmp_path: Path, data: dict) -> Path:
    file_path = tmp_path / "config.yml"
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)
    return file_path


class TestPowerZoneConfig:
    """Test suite for PowerZoneConfig YAML loading, defaults, and validation."""

    def test_loads_defaults_when_file_missing(self, tmp_path):
        config_path = tmp_path / "missing.yml"
        config = PowerZoneConfig(str(config_path))

        assert config.default_zone_weight == PowerZoneConfig.DEFAULT_ZONE_WEIGHT
        assert config.zone_weights == {}
        for zone in range(1, 6):
            assert config.get_zone_weight(zone) == PowerZoneConfig.DEFAULT_ZONE_WEIGHT
        assert config.get_zone7_multiplier() == PowerZoneConfig.DEFAULT_ZONE7_MULTIPLIER

    def test_loads_valid_config(self, tmp_path):
        data = {
            "power_zones": {
                "default_zone_weight": 0.4,
                "zones": {
                    1: {"weight": 0.3},
                    2: {"weight": 0.8}
                }
            }
        }
        path = write_yaml(tmp_path, data)
        config = PowerZoneConfig(str(path))

        assert config.default_zone_weight == 0.4
        assert config.zone_weights == {1: 0.3, 2: 0.8}
        assert config.get_zone_weight(1) == 0.3
        assert config.get_zone_weight(2) == 0.8
        assert config.get_zone_weight(5) == 0.4  # fallback to default
        assert config.get_zone7_multiplier() == config.DEFAULT_ZONE7_MULTIPLIER

    def test_zone7_with_weight_raises_error(self, tmp_path):
        data = {
            "power_zones": {
                "zones": {7: {"weight": 0.4}}
            }
        }
        path = write_yaml(tmp_path, data)

        with pytest.raises(PowerZoneConfigurationError):
            PowerZoneConfig(str(path))

    def test_weight_out_of_range_raises_error(self, tmp_path):
        data = {
            "power_zones": {
                "zones": {3: {"weight": 2.0}}
            }
        }
        path = write_yaml(tmp_path, data)

        with pytest.raises(PowerZoneConfigurationError):
            PowerZoneConfig(str(path))

    def test_zone7_multiplier_override(self, tmp_path):
        data = {
            "power_zones": {
                "zones": {
                    7: {"multiplier": 1.5}
                }
            }
        }
        path = write_yaml(tmp_path, data)
        config = PowerZoneConfig(str(path))

        assert config.get_zone7_multiplier() == 1.5

    def test_zone7_multiplier_less_than_1_raise_error(self, tmp_path):
        data = {
            "power_zones": {
                "zones": {
                    7: {"multiplier": 0.9}
                }
            }
        }
        path = write_yaml(tmp_path, data)

        config = PowerZoneConfig(str(path))
        with pytest.raises(PowerZoneConfigurationError):
            config.get_zone7_multiplier()
