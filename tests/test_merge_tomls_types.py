from collections.abc import Iterator

import pytest

from nudb_config import config as config_module
from nudb_config.pydantic.datasets import Dataset
from nudb_config.pydantic.dotmap import DotMapDict
from nudb_config.pydantic.load import NudbConfig
from nudb_config.pydantic.load import load_pydantic_settings
from nudb_config.pydantic.options import Options
from nudb_config.pydantic.paths import PathEntry
from nudb_config.pydantic.variables import Variable


@pytest.fixture
def isolated_settings() -> Iterator[NudbConfig]:
    original = config_module.settings
    config_module.settings = load_pydantic_settings()
    try:
        yield config_module.settings
    finally:
        config_module.settings = original


def test_merge_tomls_preserves_types(isolated_settings: NudbConfig) -> None:
    merged = isolated_settings.merge_tomls("tests/external_tomls_samples")

    assert isinstance(isolated_settings, NudbConfig)
    assert isinstance(merged, NudbConfig)

    assert isinstance(isolated_settings.variables, DotMapDict)
    assert isinstance(merged.variables, DotMapDict)
    assert isinstance(isolated_settings.variables.fnr, Variable)
    assert isinstance(merged.variables.fnr, Variable)

    assert isinstance(isolated_settings.datasets, DotMapDict)
    assert isinstance(merged.datasets, DotMapDict)
    assert isinstance(isolated_settings.datasets.avslutta, Dataset)
    assert isinstance(merged.datasets.avslutta, Dataset)

    assert isinstance(isolated_settings.paths, DotMapDict)
    assert isinstance(merged.paths, DotMapDict)
    assert isinstance(isolated_settings.paths.on_prem, PathEntry)
    assert isinstance(merged.paths.on_prem, PathEntry)

    assert isinstance(isolated_settings.options, Options)
    assert isinstance(merged.options, Options)
