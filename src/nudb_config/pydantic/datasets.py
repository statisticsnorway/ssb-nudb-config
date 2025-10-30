from __future__ import annotations

from pydantic import BaseModel

from .dotmap import DotMap


class Dataset(BaseModel, DotMap):
    """Dataset configuration entry under ``[datasets]``.

    Attributes:
        variables: Ordered list of variable names included in the dataset.
        thresholds_empty: Allowable proportions of emptiness per variable.
        min_values: Minimum inclusive filter values per variable.
        max_values: Maximum inclusive filter values per variable.
    """

    variables: list[str] = []
    thresholds_empty: dict[str, float] | None = None
    min_values: dict[str, str] | None = None
    max_values: dict[str, str] | None = None
    dataset_specific_renames: dict[str, str] | None = None


class DatasetsFile(BaseModel, DotMap):
    """Root schema of ``datasets.toml``.

    Attributes:
        datasets: Mapping of dataset name to its configuration.
    """

    datasets: dict[str, Dataset]
