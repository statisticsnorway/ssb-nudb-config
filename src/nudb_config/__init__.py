"""Config of metadata for functions used in ssb-nudb-use."""

from importlib.metadata import version

from .config import settings

__all__ = ["settings"]


class MissingVersionWarning(UserWarning): ...


try:
    try:
        __version__ = version(__name__)
    except Exception:
        __version__ = version("ssb-nudb-config")

except Exception as err:
    import sys
    import warnings

    if not sys.warnoptions:
        warnings.simplefilter("default")

    warnings.warn(
        f"Unable to determine package version!\nMessage: {err}",
        category=MissingVersionWarning,
        stacklevel=2,
    )

    __version__ = "0.0.0"
