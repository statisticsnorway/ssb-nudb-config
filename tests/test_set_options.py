from nudb_config import settings


def test_set_option() -> None:
    settings.options["warn_unsafe_derive"] = False
    settings.options.warn_unsafe_derive = False
    assert not settings.options.warn_unsafe_derive
