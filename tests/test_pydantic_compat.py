from __future__ import annotations

from nudb_config.config import settings as dyn_settings
from nudb_config.pydantic import load_pydantic_settings


def test_pydantic_has_same_top_level_fields() -> None:
    pyd = load_pydantic_settings()
    dyn = dyn_settings

    expected_top_level = (
        "dapla_team",
        "short_name",
        "utd_nacekoder",
        "variables_sort_unit",
        "variables",
        "datasets",
        "paths",
    )

    # Ensure both expose all expected top-level attributes via dot-notation
    for attr in expected_top_level:
        assert hasattr(dyn, attr)
        assert hasattr(pyd, attr)


def test_variables_structure_matches() -> None:
    pyd = load_pydantic_settings()
    dyn = dyn_settings

    pvars = pyd.variables  # dict[str, Variable]
    dvars = dyn.variables  # dict-like

    # Same variable names
    assert set(pvars.keys()) == set(dvars.keys())

    # For each variable: compare available field names (excluding None like exclude_none)
    for name, pvar in pvars.items():
        present_fields = {
            fname
            for fname in pvar.__class__.model_fields
            if getattr(pvar, fname) is not None
        }
        # Dynaconf may expose additional derived keys; ensure Pydantic subset matches
        assert present_fields.issubset(set(dvars[name].keys()))


def test_datasets_structure_matches() -> None:
    pyd = load_pydantic_settings()
    dyn = dyn_settings

    pdsets = pyd.datasets  # dict[str, Dataset]
    ddsets = dyn.datasets  # dict-like

    # Same dataset names
    assert set(pdsets.keys()) == set(ddsets.keys())

    # Each dataset has comparable keys (variables/min/max/thresholds), ignoring None
    for name, pds in pdsets.items():
        present_fields = {
            fname
            for fname in pds.__class__.model_fields
            if getattr(pds, fname) is not None
        }
        assert present_fields.issubset(set(ddsets[name].keys()))


def test_paths_structure_matches() -> None:
    pyd = load_pydantic_settings()
    dyn = dyn_settings

    ppaths = pyd.paths  # dict[str, PathEntry]
    dpaths = dyn.paths  # dict-like

    # Same path environment names
    assert set(ppaths.keys()) == set(dpaths.keys())
