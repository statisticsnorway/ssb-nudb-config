from nudb_config import settings


def test_paths_content() -> None:
    assert len(settings.paths.local_daplalab.delt_utdanning)
