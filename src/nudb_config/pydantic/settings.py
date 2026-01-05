from __future__ import annotations

from pydantic import BaseModel

from .dotmap import DotMap


class SettingsFile(BaseModel, DotMap):
    """Root schema of ``settings.toml``.

    Attributes:
        dapla_team: Name of the Dapla team that owns the data.
        short_name: Short identifier for the project or dataset.
    """

    dapla_team: str
    short_name: str
