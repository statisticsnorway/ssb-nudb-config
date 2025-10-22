from nudb_config import settings


def test_keys_on_single_variable() -> None:
    var = settings.variables["snr"]
    assert len(var.keys())
    assert len(var.values())
    assert len(var.items())
    assert var.get("dtype")
