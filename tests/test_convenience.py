from nudb_config import settings


def test_keys_on_single_variable() -> None:
    var = settings.variables["fnr"]
    assert len(var.keys())
    assert len(var.values())
    assert len(var.items())
    assert var.get("dtype")


def test_fetch_variable_different() -> None:
    assert settings.variables.fnr
    assert settings.variables["fnr"]
    assert settings.variables.get("fnr")


def test_iteration() -> None:
    for elem in settings.variables:
        assert elem
