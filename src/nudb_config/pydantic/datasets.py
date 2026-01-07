from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class Dataset(DotMapBaseModel):
    """Dataset configuration entry under ``[datasets]``.

    Attributes:
        variables: Ordered list of variable names included in the dataset.
        thresholds_empty: Allowable proportions of emptiness per variable.
        min_values: Minimum inclusive filter values per variable.
        max_values: Maximum inclusive filter values per variable.
        dataset_specific_renames: Custom renames to apply only for this dataset.
    """

    variables: list[str] | None = None
    thresholds_empty: dict[str, float] | None = None
    min_values: dict[str, str] | None = None
    max_values: dict[str, str] | None = None
    dataset_specific_renames: dict[str, str] | None = None


class DatasetsFile(DotMapBaseModel):
    """Root schema of ``datasets.toml``.

    Attributes:
        datasets: Mapping of dataset name to its configuration.
    """

    datasets: DotMapDict[Dataset]