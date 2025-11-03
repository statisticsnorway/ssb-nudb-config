from __future__ import annotations

import importlib.resources as impres
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict

from .datasets import DatasetsFile
from .dotmap import DotMap
from .paths import PathsFile
from .settings import SettingsFile
from .variables import Variable
from .variables import VariablesFile


class NudbConfig(BaseModel, DotMap):
    """Unified configuration built from the TOML files.

    This model aggregates values from ``settings.toml``, ``variables.toml``,
    ``variables_outdated.toml`` (if present), ``datasets.toml``, and
    ``paths.toml``. It mirrors the top-level structure
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
    (``settings.toml``, ``variables.toml``, optional ``variables_outdated.toml``,
    ``datasets.toml``, ``paths.toml``),
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
    # Optionally load additional variables flagged as outdated
    outdated_path = cfg_dir / "variables_outdated.toml"
    outdated_file: VariablesFile | None = None
    if outdated_path.exists():
        outdated_toml = _load_toml(outdated_path)
        outdated_file = VariablesFile.model_validate(outdated_toml)
    datasets_file = DatasetsFile.model_validate(datasets_toml)
    paths_file = PathsFile.model_validate(paths_toml)
    settings_file = SettingsFile.model_validate(settings_toml)

    # Apply the same codelist expansions as Dynaconf variant
    _expand_codelist_extras(variables_file.variables)
    if outdated_file is not None:
        _expand_codelist_extras(outdated_file.variables)

    # Merge variables from both files; main file takes precedence on conflicts
    # Let entries from variables_outdated.toml override duplicates to ensure
    # the new file is the authoritative source for outdated variables.
    merged_variables: dict[str, Variable] = dict(variables_file.variables)
    if outdated_file is not None:
        for k, v in outdated_file.variables.items():
            merged_variables[k] = v

    return NudbConfig(
        dapla_team=settings_file.dapla_team,
        short_name=settings_file.short_name,
        utd_nacekoder=settings_file.utd_nacekoder,
        variables_sort_unit=variables_file.variables_sort_unit,
        variables=DotMap(merged_variables),
        datasets=DotMap(datasets_file.datasets),
        paths=DotMap(paths_file.paths),
    )
