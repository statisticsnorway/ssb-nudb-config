from __future__ import annotations

from pydantic import ConfigDict

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class PathEntry(DotMapBaseModel):
    """Path configuration for a named environment under ``[paths]``.

    Attributes:
        model_config: Pydantic configuration for extra fields.
        katalog: Base catalog path for configuration artifacts.
        delt_utdanning: Location of shared education data.
    """

    model_config = ConfigDict(extra="allow")

    katalog: str | None = None
    delt_utdanning: str = ""

    # __getitem__ provided by DotMap


class PathsFile(DotMapBaseModel):
    """Root schema of ``paths.toml``.

    Attributes:
        shared_root: Shared bucket root for common datasets.
        paths: Mapping of environment name to its paths configuration.
    """

    shared_root: str | None = None
    paths: DotMapDict[PathEntry]
