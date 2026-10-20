from __future__ import annotations

from .dotmap import DotMapBaseModel


class Options(DotMapBaseModel):
    """Typed options configuration."""

    warn_unsafe_derive: bool = True
    folder_path_local_parquet: str = (
        ""  # If not an empty string at runtime, will override where we look for the nudb-parquet files in nudb_use
    )


class OptionsFile(DotMapBaseModel):
    """Root schema of ``options.toml``.

    Attributes:
        options: Options configuration block.
    """

    options: Options
