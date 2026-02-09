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
    thresholds_empty: DotMapDict[float] | None = None
    min_values: DotMapDict[str] | None = None
    max_values: DotMapDict[str] | None = None
    dataset_specific_renames: DotMapDict[str] | None = None


class DatasetsFile(DotMapBaseModel):
    """Root schema of ``datasets.toml``.

    Attributes:
        datasets: Mapping of dataset name to its configuration.
    """

    datasets: DotMapDict[Dataset]
