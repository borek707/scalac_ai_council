from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from council.config.schema import CompanyConfig

if TYPE_CHECKING:
    pass


class ConfigLoader:
    """Loads and validates company configuration from various sources.

    This class provides static methods to load :class:`CompanyConfig`
    from JSON files, YAML files (when PyYAML is available), and plain
    Python dictionaries. All loading methods perform full Pydantic
    validation and raise ``ValidationError`` on invalid data.

    Example::

        config = ConfigLoader.from_json(Path("config/company.json"))
        config = ConfigLoader.from_yaml(Path("config/company.yaml"))
        config = ConfigLoader.from_dict({"name": "Acme", "product": "API"})
    """

    @staticmethod
    def from_json(path: Path) -> CompanyConfig:
        """Load a :class:`CompanyConfig` from a JSON file.

        Args:
            path: Filesystem path to the JSON configuration file.

        Returns:
            A fully validated :class:`CompanyConfig` instance.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            pydantic.ValidationError: If the JSON data fails schema validation.
        """
        resolved = path.resolve()
        with open(resolved, "r", encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
        return CompanyConfig.model_validate(data)

    @staticmethod
    def from_yaml(path: Path) -> CompanyConfig:
        """Load a :class:`CompanyConfig` from a YAML file.

        Requires the ``PyYAML`` package to be installed. If it is not
        available, :exc:`ImportError` is raised.

        Args:
            path: Filesystem path to the YAML configuration file.

        Returns:
            A fully validated :class:`CompanyConfig` instance.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ImportError: If ``PyYAML`` is not installed.
            yaml.YAMLError: If the file contains invalid YAML.
            pydantic.ValidationError: If the YAML data fails schema validation.
        """
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for YAML config loading. "
                "Install it with: pip install PyYAML",
            ) from exc

        resolved = path.resolve()
        with open(resolved, "r", encoding="utf-8") as fh:
            data: dict[str, Any] = yaml.safe_load(fh)
        return CompanyConfig.model_validate(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> CompanyConfig:
        """Create a :class:`CompanyConfig` from a Python dictionary.

        This is the lowest-level loader; ``from_json`` and ``from_yaml``
        both delegate here after parsing their respective formats.

        Args:
            data: Dictionary containing the company configuration.

        Returns:
            A fully validated :class:`CompanyConfig` instance.

        Raises:
            pydantic.ValidationError: If the dictionary fails schema validation.
        """
        return CompanyConfig.model_validate(data)
