from __future__ import annotations

from .dotmap import DotMapBaseModel


class Options(DotMapBaseModel):
    """Typed options configuration.
    
    Attributes:
        warn_unsafe_derive: 
        folder_path_local_parquet: If not an empty string at runtime, will override where we look for the nudb-parquet files in nudb_use
        baked_data_use: Where there is an option to use baked data in a derive, will prioritize using the baked data instead of re-deriviation.
        baked_data_use_v0: When set to True, will pick v0 of a baked dataset of the latest period. If False, we only pick v1 or above.
            Mainly we want the utd-tverr team to flip this to True and use baked dataset of utd_person as input.

    """

    warn_unsafe_derive: bool = True
    folder_path_local_parquet: str = ""
    baked_data_use: bool = True
    baked_data_use_v0: bool = False


class OptionsFile(DotMapBaseModel):
    """Root schema of ``options.toml``.

    Attributes:
        options: Options configuration block.
    """

    options: Options
