from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class Constants(DotMapBaseModel):
    """Typed options configuration under ``[constants]``."""

    foreign_municipalities: list[str]
    datadoc_pandas_dtype_mapping: DotMapDict[str]


class ConstantsFile(DotMapBaseModel):
    """Root schema of ``constants.toml``.

    Attributes:
        constants: Constants configuration block.
    """

    constants: Constants
