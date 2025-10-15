from __future__ import annotations

import importlib.resources as impres
import tomllib
from collections.abc import ItemsView
from collections.abc import Iterator
from collections.abc import KeysView
from collections.abc import Mapping
from collections.abc import ValuesView
from pathlib import Path
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict

from .datasets import Dataset
from .datasets import DatasetsFile
from .paths import PathEntry
from .paths import PathsFile
from .settings import SettingsFile
from .variables import Variable
from .variables import VariablesFile

T = TypeVar("T")


class DotMap(Mapping[str, T], Generic[T]):
    """Read-only mapping that also exposes keys via dot-notation.

    Example: for a mapping ``{"env": PathEntry(...)}``, ``dot.env`` returns the
    same as ``dot["env"]``. Unknown attributes raise ``AttributeError``.
    """

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, T]) -> None:
        """Initialize the dot-accessible mapping.

        Args:
            data: Underlying mapping providing storage and lookups.
        """
        self._data = data

    def __getattr__(self, name: str) -> T:  # for mypy attr access
        """Return value using attribute-style access.

        Mirrors ``self[name]``.

        Args:
            name: Key to access within the mapping.

        Returns:
            T: Value associated with ``name``.

        Raises:
            AttributeError: If ``name`` is not present in the mapping.
        """
        try:
            return self._data[name]
        except KeyError as exc:  # pragma: no cover - defensive
            raise AttributeError(name) from exc

    # Mapping interface
    def __getitem__(self, key: str) -> T:
        """Retrieve an item by key.

        Args:
            key: Mapping key.

        Returns:
            T: Value associated with ``key``.
        """
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys in insertion order.

        Returns:
            Iterator[str]: Iterator over the mapping's keys.
        """
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of items in the mapping.

        Returns:
            int: Count of items.
        """
        return len(self._data)

    # Convenience
    def keys(self) -> KeysView[str]:
        """Return a dynamic view of the mapping's keys.

        Returns:
            KeysView[str]: Dynamic view of keys.
        """
        return self._data.keys()

    def items(self) -> ItemsView[str, T]:
        """Return a dynamic view of the mapping's key/value pairs.

        Returns:
            ItemsView[str, T]: Dynamic view of key/value pairs.
        """
        return self._data.items()

    def values(self) -> ValuesView[T]:
        """Return a dynamic view of the mapping's values.

        Returns:
            ValuesView[T]: Dynamic view of values.
        """
        return self._data.values()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """Return a concise string representation.

        Returns:
            str: Debug-friendly representation of the mapping.
        """
        return f"DotMap({self._data!r})"


class NudbConfig(BaseModel):
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
    variables: DotMap[Variable]

    datasets: DotMap[Dataset]

    paths: DotMap[PathEntry]


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
