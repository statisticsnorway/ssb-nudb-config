from __future__ import annotations

import copy
import importlib.resources as impres
import tomllib
from pathlib import Path

from pydantic import ConfigDict

from ..logger import logger
from .datasets import Dataset
from .datasets import DatasetsFile
from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict
from .options import Options
from .options import OptionsFile
from .paths import PathEntry
from .paths import PathsFile
from .settings import SettingsFile
from .variables import Variable
from .variables import VariablesFile


class NudbConfig(DotMapBaseModel):
    """Unified configuration built from the TOML files.

    This model aggregates values from ``settings.toml`` ,``options.toml``, ``variables.toml``,
    ``variables_outdated.toml`` (if present), ``datasets.toml``, and
    ``paths.toml``. It mirrors the top-level structure
    exposed by the Dynaconf-based loader to preserve compatibility. Any
    codelist augmentations performed by the Dynaconf variant are also applied
    during loading so that downstream behavior matches.

    Attributes:
        model_config: Pydantic configuration allowing arbitrary DotMap content.
        dapla_team: Team identifier from ``settings.toml``.
        short_name: Short project name from ``settings.toml``.
        variables_sort_unit: Unit sort order from ``variables.toml``.
        variables: Mapping of variable name to definition.
        datasets: Mapping of dataset name to configuration.
        paths: Mapping of environment name to paths configuration.
        options: Options from ``options.toml``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dapla_team: str
    short_name: str

    variables_sort_unit: list[str] | None = None
    variables: DotMapDict[Variable]

    datasets: DotMapDict[Dataset]
    paths: DotMapDict[PathEntry]
    options: Options

    def merge_tomls(self, toml_dir: str | Path) -> NudbConfig:
        """Merge values from external TOML files into this config and return it."""
        cfg_dir = _resolve_toml_dir(toml_dir)
        for path in sorted(cfg_dir.glob("*.toml")):
            toml_data = _load_toml(path)
            _merge_into(self, toml_data)
        return self

    def _deep_copy(self) -> NudbConfig:
        try:
            return self.model_copy(deep=True)
        except Exception:
            return copy.deepcopy(self)


# Ensure forward refs are resolved for Pydantic
NudbConfig.model_rebuild()


def _load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _resolve_toml_dir(toml_dir: str | Path) -> Path:
    cfg_dir = Path(toml_dir)
    if cfg_dir.exists():
        return cfg_dir
    fallback = Path.cwd() / str(toml_dir).lstrip("/\\")
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"TOML directory not found: {toml_dir}")


def _is_none_sentinel(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() == "none":
        return True
    return False


def _merge_into(target: object, updates: object) -> None:
    if isinstance(updates, dict):
        _merge_mapping(target, updates, path=())
        return
    # Scalar replacement on leaves is handled by parent callers.


def _merge_mapping(
    target: object, updates: dict[str, object], *, path: tuple[str, ...]
) -> None:
    if isinstance(target, DotMapDict):
        for key, value in updates.items():
            if _is_none_sentinel(value):
                if key in target:
                    del target[key]
                continue
            if isinstance(value, dict):
                value_type = getattr(target, "_value_type", None)
                if value_type is Variable and "name" not in value:
                    value = {**value, "name": key}
            if key in target:
                current = target[key]
                if isinstance(value, dict) and isinstance(
                    current, (DotMapBaseModel, DotMapDict, dict)
                ):
                    _merge_mapping(current, value, path=(*path, key))
                else:
                    if current == value:
                        logger.warning(
                            "Merge overwrite has same value; consider removing from local config: %s",
                            ".".join((*path, key)),
                        )
                    target[key] = value
            else:
                target[key] = value
        return

    if isinstance(target, DotMapBaseModel):
        model_fields = getattr(type(target), "model_fields", {})
        for key, value in updates.items():
            if key not in model_fields:
                continue
            if _is_none_sentinel(value):
                setattr(target, key, None)
                continue
            current = getattr(target, key, None)
            if isinstance(value, dict) and isinstance(
                current, (DotMapBaseModel, DotMapDict, dict)
            ):
                _merge_mapping(current, value, path=(*path, key))
            else:
                if current == value:
                    logger.warning(
                        "Merge overwrite has same value; consider removing from local config: %s",
                        ".".join((*path, key)),
                    )
                setattr(target, key, value)
        return

    if isinstance(target, dict):
        for key, value in updates.items():
            if _is_none_sentinel(value):
                target.pop(key, None)
                continue
            current = target.get(key)
            if isinstance(value, dict) and isinstance(
                current, (DotMapBaseModel, DotMapDict, dict)
            ):
                _merge_mapping(current, value, path=(*path, key))
            else:
                if current == value:
                    logger.warning(
                        "Merge overwrite has same value; consider removing from local config: %s",
                        ".".join((*path, key)),
                    )
                target[key] = value


def _iter_variable_paths(cfg_dir: Path) -> list[Path]:
    """Return variable TOML paths excluding derived label entries."""
    return [
        path
        for path in cfg_dir.glob("variables*.toml")
        if path.name != "variables_derived_label.toml"
    ]


def _load_variables(cfg_dir: Path) -> VariablesFile:
    """Load and merge variables, generating derived label entries."""
    merged_variables: DotMapDict[Variable] = DotMapDict(value_type=Variable)
    variables_sort_unit_list: None | list[str] = None
    derived_file: VariablesFile | None = None

    for path in _iter_variable_paths(cfg_dir):
        var_toml = _load_toml(path)
        var_file: VariablesFile = VariablesFile.model_validate(var_toml)
        if path.name == "variables_derived.toml":
            derived_file = var_file
        for key, variable in var_file.variables.items():
            merged_variables[key] = variable
        if getattr(var_file, "variables_sort_unit", None) is not None:
            variables_sort_unit_list = var_file.variables_sort_unit

    variables_file = VariablesFile(
        variables=merged_variables,
        variables_sort_unit=variables_sort_unit_list,
    )
    if derived_file is not None:
        label_variables = _expand_derived_label_variables(derived_file)
        for key, variable in label_variables.items():
            if key not in variables_file.variables:
                variables_file.variables[key] = variable
    return _expand_codelist_extras(variables_file)


def _load_datasets(cfg_dir: Path) -> DatasetsFile:
    """Load and merge dataset TOML files."""
    merged_datasets: DotMapDict[Dataset] = DotMapDict(value_type=Dataset)
    for path in cfg_dir.glob("datasets*.toml"):
        datatoml = _load_toml(path)
        data_file: DatasetsFile = DatasetsFile.model_validate(datatoml)
        for key, dataset in data_file.datasets.items():
            merged_datasets[key] = dataset
    return DatasetsFile(datasets=merged_datasets)


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
    settings_toml = _load_toml(cfg_dir / "settings.toml")
    settings_file = SettingsFile.model_validate(settings_toml)
    paths_toml = _load_toml(cfg_dir / "paths.toml")
    paths_file = PathsFile.model_validate(paths_toml)
    options_toml = _load_toml(cfg_dir / "options.toml")
    options_file = OptionsFile.model_validate(options_toml)

    variables_file = _load_variables(cfg_dir)
    dataset_file = _load_datasets(cfg_dir)

    return NudbConfig(
        dapla_team=settings_file.dapla_team,
        short_name=settings_file.short_name,
        variables_sort_unit=variables_file.variables_sort_unit,
        variables=variables_file.variables,
        datasets=dataset_file.datasets,
        paths=paths_file.paths,
        options=options_file.options,
    )


def _expand_derived_label_variables(
    variables_file: VariablesFile,
) -> DotMapDict[Variable]:
    """Create label variables for derived entries with klass codelists.

    Mirrors the contents of the old ``variables_derived_label.toml`` by generating
    ``{name}_label`` variables for derived entries whose ``klass_codelist`` is
    a positive integer.
    """
    label_variables: DotMapDict[Variable] = DotMapDict(value_type=Variable)
    for name, variable in variables_file.variables.items():
        klass_codelist = getattr(variable, "klass_codelist", None)
        if not isinstance(klass_codelist, int) or klass_codelist <= 0:
            continue
        label_name = f"{name}_label"
        label_variables[label_name] = Variable(
            name=label_name,
            unit=variable.unit,
            dtype="STRING",
            derived_from=[name],
        )
    return label_variables


def _expand_codelist_extras(variables_file: VariablesFile) -> VariablesFile:
    """Expands codelists from KLASS that we have no direct control over, but 360 has their own values for...

    Args:
        variables_file: The VariablesFile object to expand on.

    Returns:
        VariablesFile: The modified variablesfile part after adding the codelist_extras field.
    """
    for _name, var in variables_file.variables.items():
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
    return variables_file
