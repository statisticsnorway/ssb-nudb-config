from __future__ import annotations

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict


class Constants(DotMapBaseModel):
    """Typed options configuration under ``[constants]``."""

    snr_allnumeric_7digit_threshold_percent: float
    fullfoertkode: str
    venstresensur: str

    vg_utdprogram_ranges_studiespess: list[str]
    vg_utdprogram_ranges_yrkesfag: list[str]
    sane_skoleaar_range: list[int]
    unique_per_person_cols: list[str]
    valid_personal_ids_prio: list[str]
    brreg_utd_nacekoder: list[str]
    foreign_municipalities: list[str]

    county_municipality_single_mapping: DotMapDict[str]
    extra_municipality_nr: DotMapDict[str]
    missing_vals: DotMapDict[str]
    datadoc_pandas_dtype_mapping: DotMapDict[str]


class ConstantsFile(DotMapBaseModel):
    """Root schema of ``constants.toml``.

    Attributes:
        constants: Constants configuration block.
    """

    constants: Constants
