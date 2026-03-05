from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class PathEntry(DotMapBaseModel):
    """Path configuration for a named environment under ``[paths]``.

    Attributes:
        produkt: Product data root.
        katalog: Base catalog path for configuration artifacts.
        shared_root_external: Shared bucket root for common datasets external to the team.
        shared_root_internal: Shared bucket root for common datasets internal to the team.
        shared_utdanning_external: Local shared education data path external to the team.
        shared_utdanning_internal: Local shared education data path internal to the team.

    """

    produkt: str | None = None
    katalog: str | None = None
    shared_root_external: str | None = None
    shared_root_internal: str | None = None
    shared_utdanning_external: str | None = None
    shared_utdanning_internal: str | None = None


class PathsFile(DotMapBaseModel):
    """Root schema of ``paths.toml``.

    Attributes:
        paths: Mapping of environment name to its paths configuration.
    """

    paths: DotMapDict[PathEntry]
