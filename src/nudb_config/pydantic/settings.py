from __future__ import annotations

from pydantic import BaseModel

from .mixins import SubscriptableModel


class SettingsFile(SubscriptableModel, BaseModel):
    """Root schema of ``settings.toml``.

    Attributes:
        dapla_team: Name of the Dapla team that owns the data.
        short_name: Short identifier for the project or dataset.
        utd_nacekoder: List of NACE codes relevant for education data.
    """

    dapla_team: str
    short_name: str
    utd_nacekoder: list[str]
