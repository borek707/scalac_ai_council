from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from council.config.loader import ConfigLoader
from council.config.schema import (
    CompanyConfig,
    Competitor,
    Constraints,
    TargetSegment,
)


class TestCompanyConfig:
    """Tests for CompanyConfig schema validation."""

    def test_valid_config(self, sample_config: CompanyConfig) -> None:
        assert sample_config.name == "TestCorp"
        assert sample_config.product == "AI-Powered Analytics Platform"
        assert len(sample_config.competitors) == 2
        assert sample_config.constraints.timeline_days == 90

    def test_default_constraints(self) -> None:
        config = CompanyConfig(name="Minimal", product="Test")
        assert config.constraints.timeline_days == 90
        assert config.constraints.budget_pln == 0
        assert config.constraints.team_size == 2
        assert config.competitors == []
        assert config.differentiators == []

    def test_name_validation(self) -> None:
        with pytest.raises(ValidationError):
            CompanyConfig(name="", product="Test")

    def test_name_too_long(self) -> None:
        with pytest.raises(ValidationError):
            CompanyConfig(name="A" * 101, product="Test")

    def test_product_required(self) -> None:
        with pytest.raises(ValidationError):
            CompanyConfig(name="TestCorp", product="")

    def test_competitor_threat_levels(self) -> None:
        for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            comp = Competitor(name="X", threat=level)  # type: ignore[arg-type]
            assert comp.threat == level

    def test_competitor_invalid_threat(self) -> None:
        with pytest.raises(ValidationError):
            Competitor(name="X", threat="INVALID")  # type: ignore[arg-type]

    def test_constraints_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Constraints(timeline_days=0)
        with pytest.raises(ValidationError):
            Constraints(timeline_days=366)
        with pytest.raises(ValidationError):
            Constraints(team_size=0)
        with pytest.raises(ValidationError):
            Constraints(budget_pln=-1)

    def test_serialization_roundtrip(self, sample_config: CompanyConfig) -> None:
        data = sample_config.model_dump()
        restored = CompanyConfig.model_validate(data)
        assert restored.name == sample_config.name
        assert restored.product == sample_config.product

    def test_json_serialization(self, sample_config: CompanyConfig, tmp_path: Path) -> None:
        json_path = tmp_path / "config.json"
        json_path.write_text(sample_config.model_dump_json(), encoding="utf-8")
        loaded = ConfigLoader.from_json(json_path)
        assert loaded.name == sample_config.name


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_from_json(self, tmp_path: Path) -> None:
        data = {
            "name": "JsonCorp",
            "product": "Test Product",
            "pricing_tier": "Pro",
            "competitors": [
                {"name": "CompA", "threat": "HIGH"},
            ],
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(data), encoding="utf-8")

        config = ConfigLoader.from_json(json_path)
        assert config.name == "JsonCorp"
        assert config.product == "Test Product"
        assert len(config.competitors) == 1

    def test_from_dict(self) -> None:
        data = {
            "name": "DictCorp",
            "product": "Another Product",
            "constraints": {"timeline_days": 60},
        }
        config = ConfigLoader.from_dict(data)
        assert config.name == "DictCorp"
        assert config.constraints.timeline_days == 60

    def test_from_json_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            ConfigLoader.from_json(tmp_path / "nonexistent.json")

    def test_from_json_invalid_json(self, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("not valid json {{{", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            ConfigLoader.from_json(bad_json)

    def test_empty_competitors_list(self) -> None:
        config = CompanyConfig(name="NoComp", product="Solo")
        assert config.competitors == []
