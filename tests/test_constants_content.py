from nudb_config import settings


def test_constants_foreign_municipalities() -> None:
    muncs = settings.constants.foreign_municipalities
    assert muncs
    assert isinstance(muncs, list)
    assert all(bool(x) and isinstance(x, str) for x in muncs)


def test_dot_accessor_string_type() -> None:
    assert "string" in settings.constants.datadoc_pandas_dtype_mapping.STRING
