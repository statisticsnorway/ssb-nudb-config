from nudb_config import settings
from nudb_config.pydantic.datasets import Dataset
from nudb_config.pydantic.dotmap import DotMapDict
from nudb_config.pydantic.load import NudbConfig
from nudb_config.pydantic.options import Options
from nudb_config.pydantic.paths import PathEntry
from nudb_config.pydantic.variables import Variable


def test_merge_tomls_preserves_types() -> None:
    merged = settings.merge_tomls("tests/external_tomls_samples")

    assert isinstance(settings, NudbConfig)
    assert isinstance(merged, NudbConfig)

    assert isinstance(settings.variables, DotMapDict)
    assert isinstance(merged.variables, DotMapDict)
    assert isinstance(settings.variables.fnr, Variable)
    assert isinstance(merged.variables.fnr, Variable)

    assert isinstance(settings.datasets, DotMapDict)
    assert isinstance(merged.datasets, DotMapDict)
    assert isinstance(settings.datasets.avslutta, Dataset)
    assert isinstance(merged.datasets.avslutta, Dataset)

    assert isinstance(settings.paths, DotMapDict)
    assert isinstance(merged.paths, DotMapDict)
    assert isinstance(settings.paths.on_prem, PathEntry)
    assert isinstance(merged.paths.on_prem, PathEntry)

    assert isinstance(settings.options, Options)
    assert isinstance(merged.options, Options)
