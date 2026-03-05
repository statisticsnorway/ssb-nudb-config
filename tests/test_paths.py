import tomllib
from pathlib import Path

from nudb_config import settings


def test_paths_content() -> None:
    assert isinstance(settings.paths.daplalab_mounted.shared_utdanning_internal, str)
    assert len(settings.paths.daplalab_mounted.shared_utdanning_internal)
    assert isinstance(
        settings["paths"]["daplalab_mounted"]["shared_utdanning_internal"], str
    )
    assert len(settings["paths"]["daplalab_mounted"]["shared_utdanning_internal"])


def test_paths_toml_strings_end_with_slash() -> None:
    paths_toml = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "nudb_config"
        / "config_tomls"
        / "paths.toml"
    )
    with paths_toml.open("rb") as fh:
        data = tomllib.load(fh)

    paths = data.get("paths", {})
    assert isinstance(paths, dict)

    for group in paths.values():
        if isinstance(group, dict):
            for value in group.values():
                if isinstance(value, str):
                    assert value.endswith("/")
        elif isinstance(group, str):
            assert group.endswith("/")
