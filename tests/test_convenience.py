from nudb_config import settings


def test_keys_on_single_variable() -> None:
    var = settings.variables["snr"]
    assert len(var.keys())
    assert len(var.values())
    assert len(var.items())
    assert var.get("dtype")


def test_fetch_variable_different() -> None:
    assert settings.variables.snr
    assert settings.variables["snr"]
    assert settings.variables.get("snr")


def test_iteration() -> None:
    for elem in settings.variables:
        assert elem
