from __future__ import annotations

from .dotmap import DotMapBaseModel


class Options(DotMapBaseModel):
    """Typed options configuration under ``[options]``."""

    warn_unsafe_derive: bool = True


class OptionsFile(DotMapBaseModel):
    """Root schema of ``options.toml``.

    Attributes:
        options: Options configuration block.
    """

    options: Options
