from __future__ import annotations

from pydantic import BaseModel

from .dotmap import DotMap


class PathEntry(DotMap, BaseModel):
    """Path configuration for a named environment under ``[paths]``.

    Attributes:
        katalog: Base catalog path for configuration artifacts.
        delt_utdanning: Location of shared education data.
    """

    katalog: str = ""
    delt_utdanning: str = ""

    # __getitem__ provided by DotMap


class PathsFile(DotMap, BaseModel):
    """Root schema of ``paths.toml``.

    Attributes:
        paths: Mapping of environment name to its paths configuration.
    """

    paths: dict[str, PathEntry]
