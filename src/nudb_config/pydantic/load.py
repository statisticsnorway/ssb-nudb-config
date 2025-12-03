from __future__ import annotations

import importlib.resources as impres
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict

from .datasets import Dataset
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


def _expand_codelist_extras(variables: dict[str, Variable]) -> dict[str, Variable]:
    """Expands codelists from KLASS that we have no direct control over, but 360 has their own values for...

    Args:
        variables: The dict that will be placed as variables under the settings-object.

    Returns:
        dict[str, Variable]: The modified variables-settings part after adding the codelist_extras field.
    """
    for _name, var in variables.items():
        if var.klass_codelist == 91:
            var.codelist_extras = {
                "151": "DDR / Øst-Tyskland",
                "135": "SSSR / Sovjetunionen",
                "125": "Jugoslavia (til 2004) / Serbia og Montenegro (fra og med 2004)",
                "142": "Tsjekkoslovakia",
            }
        if var.klass_codelist == 131:
            var.codelist_extras = {
                "2580": "360s definerte Utland",
                "2111": "Longyearbyen arealplanområde",
            }
    return variables


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
    paths_toml = _load_toml(cfg_dir / "paths.toml")
    settings_toml = _load_toml(cfg_dir / "settings.toml")
    paths_file = PathsFile.model_validate(paths_toml)
    settings_file = SettingsFile.model_validate(settings_toml)

    # Variable-toml was getting too big so we split the variables across different tomls
    variables_paths = cfg_dir.glob("variables*.toml")
    merged_variables: dict[str, Variable] = {}
    variables_sort_unit_list: None | list[str] = None
    for path in variables_paths:
        var_toml = _load_toml(path)
        var_file: VariablesFile = VariablesFile.model_validate(var_toml)
        # Merge variable definitions
        merged_variables |= dict(var_file.variables)
        # Capture the sort order if present on this file
        if getattr(var_file, "variables_sort_unit", None) is not None:
            variables_sort_unit_list = var_file.variables_sort_unit
    merged_variables = _expand_codelist_extras(merged_variables)

    # Dataset-toml was split
    merged_datasets: dict[str, Dataset] = {}
    datasets_paths = cfg_dir.glob("datasets*.toml")
    for path in datasets_paths:
        datatoml = _load_toml(path)
        data_file: DatasetsFile = DatasetsFile.model_validate(datatoml)
        # Merge variable definitions
        merged_datasets |= dict(data_file.datasets)

    return NudbConfig(
        dapla_team=settings_file.dapla_team,
        short_name=settings_file.short_name,
        utd_nacekoder=settings_file.utd_nacekoder,
        variables_sort_unit=variables_sort_unit_list,
        variables=DotMap(merged_variables),
        datasets=DotMap(merged_datasets),
        paths=DotMap(paths_file.paths),
    )
