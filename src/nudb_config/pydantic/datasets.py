from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class Dataset(DotMapBaseModel):
    """Dataset configuration entry under ``[datasets]``.

    Attributes:
        team: The name of the dapla-team who owns the dataset.
        bucket: The bucket name, under the dapla-team, where the dataset is located.
        path_glob: A glob that can be used in the bucket to pinpoint all available periods and versions of the dataset.
        variables: Ordered list of variable names included in the dataset.
        thresholds_empty: Allowable proportions of emptiness per variable.
        min_values: Minimum inclusive filter values per variable.
        max_values: Maximum inclusive filter values per variable.
        dataset_specific_renames: Custom renames to apply only for this dataset.
    """

    team: str
    bucket: str
    path_glob: str
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
