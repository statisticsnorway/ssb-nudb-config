from __future__ import annotations

from pydantic import ConfigDict

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class Constants(DotMapBaseModel):
    """Typed options configuration under ``[constants]``."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    foreign_municipalities: list[str] | None = None
    datadoc_pandas_dtype_mapping: DotMapDict[str] | None = None


class ConstantsFile(DotMapBaseModel):
    """Root schema of ``constants.toml``.

    Attributes:
        model_config: Pydantic configuration for extra fields.
        constants: Constants configuration block.
    """

    model_config = ConfigDict(extra="allow")

    constants: Constants
