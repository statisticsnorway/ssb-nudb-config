from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class PathEntry(DotMapBaseModel):
    """Path configuration for a named environment under ``[paths]``.

    Attributes:
        katalog: Base catalog path for configuration artifacts.
        delt_utdanning: Location of shared education data.
    """

    katalog: str | None = None
    delt_utdanning: str = ""

    # __getitem__ provided by DotMap


class PathsFile(DotMapBaseModel):
    """Root schema of ``paths.toml``.

    Attributes:
        paths: Mapping of environment name to its paths configuration.
    """

    paths: DotMapDict[PathEntry]
