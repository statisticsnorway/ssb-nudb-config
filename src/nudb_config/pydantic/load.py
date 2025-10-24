from __future__ import annotations

import importlib.resources as impres
import logging
import tomllib
from pathlib import Path
from typing import Any
from typing import cast

from pydantic import BaseModel
from pydantic import ConfigDict

from .datasets import DatasetsFile
from .dotmap import DotMap
from .paths import PathsFile
from .settings import SettingsFile
from .variables import Variable
from .variables import VariablesFile

logger = logging.getLogger(__name__)


class NudbConfig(BaseModel, DotMap):
    """Unified configuration built from the TOML files.

    This model aggregates values from ``settings.toml``, ``variables.toml``,
    ``datasets.toml``, and ``paths.toml``. It mirrors the top-level structure
    exposed by the Dynaconf-based loader to preserve compatibility. Any
    codelist augmentations performed by the Dynaconf variant are also applied
    during loading so that downstream behavior matches.

    Attributes:
        dapla_team: Team identifier from ``settings.toml``.
        short_name: Short project name from ``settings.toml``.
        utd_nacekoder: NACE codes from ``settings.toml``.
        variables_sort_unit: Unit sort order from ``variables.toml``.
        variables: Mapping of variable name to definition.
        datasets: Mapping of dataset name to configuration.
        paths: Mapping of environment name to paths configuration.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dapla_team: str
    short_name: str
    utd_nacekoder: list[str]

    variables_sort_unit: list[str] | None = None
    variables: Any

    datasets: DotMap

    paths: DotMap


# Ensure forward refs are resolved for Pydantic
NudbConfig.model_rebuild()


def _load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _expand_codelist_extras(variables: dict[str, Variable]) -> None:
    # Mirror expand_codelist() logic from dynaconf-based config
    for _name, var in variables.items():
        if var.klass_codelist == 91:
            var.codelist_extras = {
                "151": "DDR / Øst-Tyskland",
                "135": "SSSR / Sovjetunionen",
            }
        if var.klass_codelist == 131:
            var.codelist_extras = {
                "2580": "360s definerte Utland",
                "2111": "Longyearbyen arealplanområde",
            }


def load_pydantic_settings() -> NudbConfig:
    """Load and assemble configuration using Pydantic models.

    Reads the package-embedded TOML files under ``nudb_config/config_tomls``
    (``settings.toml``, ``variables.toml``, ``datasets.toml``, ``paths.toml``),
    parses them into their respective Pydantic models, applies the same
    codelist augmentations as the Dynaconf-based loader, and returns a unified
    ``NudbConfig`` object mirroring the Dynaconf structure.

    Returns:
        NudbConfig: Aggregated configuration ready for downstream use.
    """
    base = Path(str(impres.files("nudb_config")))
    cfg_dir = base / "config_tomls"

    # Read individual toml files
    variables_toml = _load_toml(cfg_dir / "variables.toml")
    datasets_toml = _load_toml(cfg_dir / "datasets.toml")
    paths_toml = _load_toml(cfg_dir / "paths.toml")
    settings_toml = _load_toml(cfg_dir / "settings.toml")

    # Parse with Pydantic
    variables_file = VariablesFile.model_validate(variables_toml)
    datasets_file = DatasetsFile.model_validate(datasets_toml)
    paths_file = PathsFile.model_validate(paths_toml)
    settings_file = SettingsFile.model_validate(settings_toml)

    # Apply the same codelist expansions as Dynaconf variant
    _expand_codelist_extras(variables_file.variables)

    return NudbConfig(
        dapla_team=settings_file.dapla_team,
        short_name=settings_file.short_name,
        utd_nacekoder=settings_file.utd_nacekoder,
        variables_sort_unit=variables_file.variables_sort_unit,
        variables=DotMap(variables_file.variables),
        datasets=DotMap(datasets_file.datasets),
        paths=DotMap(paths_file.paths),
    )


def _warn_unknown(prefix: str, unknown_keys: set[str]) -> None:
    for key in sorted(unknown_keys):
        logger.warning("Unknown key in %s: %s (ignored)", prefix, key)


def _apply_settings_overrides(self: NudbConfig, data: dict[str, Any]) -> None:
    allowed = {"dapla_team", "short_name", "utd_nacekoder"}
    _warn_unknown("settings.toml", set(data.keys()) - allowed)
    merged = {
        "dapla_team": self.dapla_team,
        "short_name": self.short_name,
        "utd_nacekoder": self.utd_nacekoder,
        **{k: v for k, v in data.items() if k in allowed},
    }
    validated = SettingsFile.model_validate(merged)
    self.dapla_team = validated.dapla_team
    self.short_name = validated.short_name
    self.utd_nacekoder = validated.utd_nacekoder


def _apply_variables_overrides(self: NudbConfig, data: dict[str, Any]) -> None:
    allowed_top = {"variables_sort_unit", "variables"}
    _warn_unknown("variables.toml", set(data.keys()) - allowed_top)

    if "variables_sort_unit" in data:
        vsu = data["variables_sort_unit"]
        tmp = VariablesFile.model_validate(
            {
                "variables_sort_unit": vsu,
                "variables": getattr(self.variables, "_data", {}) or {},
            }
        )
        self.variables_sort_unit = tmp.variables_sort_unit

    vars_section = data.get("variables")
    if isinstance(vars_section, dict):
        for name, payload in vars_section.items():
            if not isinstance(payload, dict):
                logger.warning("Variable %s has non-mapping payload; ignored", name)
                continue
            allowed_fields = set(Variable.model_fields.keys())
            _warn_unknown(f"variables.{name}", set(payload.keys()) - allowed_fields)
            filtered = {k: v for k, v in payload.items() if k in allowed_fields}
            validated_var = Variable.model_validate(filtered)
            mapping = getattr(self.variables, "_data", None)
            if isinstance(mapping, dict):
                mapping[name] = validated_var
            else:
                self.variables = DotMap({name: validated_var})
        mapping_all = cast(
            dict[str, Variable], getattr(self.variables, "_data", {}) or {}
        )
        _expand_codelist_extras(mapping_all)


def _apply_datasets_overrides(self: NudbConfig, data: dict[str, Any]) -> None:
    allowed_top = {"datasets"}
    _warn_unknown("datasets.toml", set(data.keys()) - allowed_top)
    from .datasets import Dataset

    ds_section = data.get("datasets")
    if isinstance(ds_section, dict):
        for name, payload in ds_section.items():
            if not isinstance(payload, dict):
                logger.warning("Dataset %s has non-mapping payload; ignored", name)
                continue
            allowed_fields = set(Dataset.model_fields.keys())
            _warn_unknown(f"datasets.{name}", set(payload.keys()) - allowed_fields)
            filtered = {k: v for k, v in payload.items() if k in allowed_fields}
            mapping = getattr(self.datasets, "_data", None)
            base: dict[str, Any] = {}
            if isinstance(mapping, dict) and name in mapping:
                try:
                    base = mapping[name].model_dump()
                except Exception:
                    base = {}
            merged = {**base, **filtered}
            validated = Dataset.model_validate(merged)
            if isinstance(mapping, dict):
                mapping[name] = validated
            else:
                self.datasets = DotMap({name: validated})


def _apply_paths_overrides(self: NudbConfig, data: dict[str, Any]) -> None:
    allowed_top = {"paths"}
    _warn_unknown("paths.toml", set(data.keys()) - allowed_top)
    from .paths import PathEntry

    section = data.get("paths")
    if isinstance(section, dict):
        for name, payload in section.items():
            if not isinstance(payload, dict):
                logger.warning("Path entry %s has non-mapping payload; ignored", name)
                continue
            allowed_fields = set(PathEntry.model_fields.keys())
            _warn_unknown(f"paths.{name}", set(payload.keys()) - allowed_fields)
            filtered = {k: v for k, v in payload.items() if k in allowed_fields}
            mapping = getattr(self.paths, "_data", None)
            base: dict[str, Any] = {}
            if isinstance(mapping, dict) and name in mapping:
                try:
                    base = mapping[name].model_dump()
                except Exception:
                    base = {}
            merged = {**base, **filtered}
            validated = PathEntry.model_validate(merged)
            if isinstance(mapping, dict):
                mapping[name] = validated
            else:
                self.paths = DotMap({name: validated})


def _read_toml_if_exists(path: Path) -> dict[str, Any] | None:
    if path.exists():
        return _load_toml(path)
    return None


def apply_overrides_from_dir(self: NudbConfig, directory: str | Path) -> None:
    """Apply overrides from a directory of TOML files.

    Looks for ``settings.toml``, ``variables.toml``, ``datasets.toml``, and
    ``paths.toml`` in the given directory. Any provided values are validated
    via Pydantic and merged into the current settings object. Unknown keys are
    ignored with a warning.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(str(dir_path))

    settings_data = _read_toml_if_exists(dir_path / "settings.toml")
    if settings_data:
        _apply_settings_overrides(self, settings_data)

    variables_data = _read_toml_if_exists(dir_path / "variables.toml")
    if variables_data:
        _apply_variables_overrides(self, variables_data)

    datasets_data = _read_toml_if_exists(dir_path / "datasets.toml")
    if datasets_data:
        _apply_datasets_overrides(self, datasets_data)

    paths_data = _read_toml_if_exists(dir_path / "paths.toml")
    if paths_data:
        _apply_paths_overrides(self, paths_data)


# Bind as a method on NudbConfig instances
NudbConfig.apply_overrides_from_dir = apply_overrides_from_dir  # type: ignore[attr-defined]
