"""Config of metadata for functions used in ssb-nudb-use."""

from .config import settings

__all__ = ["settings"]


try:
    __version__ = importlib.metadata.version(__name__)
except Exception as err:
    __version__ = "0.0.0"
    logger.warning(f"Unable to determine package version!\nMessage: {err}")
