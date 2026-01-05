from __future__ import annotations

from pydantic import BaseModel

from .dotmap import DotMap


class OptionEntry(BaseModel, DotMap):
    """Options configuration under ``[options]``.

    Attributes:
        warn_unsafe_derive: If we should warn of unsafe derivations.
    """

    warn_unsafe_derive: bool


class OptionsFile(BaseModel, DotMap):
    """Root schema of ``options.toml``.

    Attributes:
        options: Options configuration block.
    """

    options: OptionEntry
