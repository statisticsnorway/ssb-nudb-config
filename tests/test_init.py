import importlib
import warnings
from importlib import metadata
from unittest.mock import patch

import nudb_config


def test_version_uses_package_fallback_without_warning() -> None:
    call_order = []

    def fake_version(dist_name: str) -> str:
        call_order.append(dist_name)
        if len(call_order) == 1:
            raise metadata.PackageNotFoundError(dist_name)
        return "9.9.9"

    with patch("importlib.metadata.version", side_effect=fake_version):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            reloaded = importlib.reload(nudb_config)

    assert reloaded.__version__ == "9.9.9"
    assert call_order == ["nudb_config", "ssb-nudb-config"]
    assert not any(
        isinstance(warning.message, nudb_config.MissingVersionWarning)
        for warning in caught
    )


def test_missing_version_warns_and_defaults() -> None:
    with patch("importlib.metadata.version", side_effect=Exception("not found")):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            reloaded = importlib.reload(nudb_config)

    assert reloaded.__version__ == "0.0.0"
    assert any(
        isinstance(warning.message, nudb_config.MissingVersionWarning)
        for warning in caught
    )
