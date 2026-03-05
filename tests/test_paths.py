from nudb_config import settings


def test_paths_content() -> None:
    assert isinstance(settings.paths.daplalab_mounted.shared_utdanning_internal, str)
    assert len(settings.paths.daplalab_mounted.shared_utdanning_internal)
    assert isinstance(
        settings["paths"]["daplalab_mounted"]["shared_utdanning_internal"], str
    )
    assert len(settings["paths"]["daplalab_mounted"]["shared_utdanning_internal"])
