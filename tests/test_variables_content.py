from nudb_config import settings


def test_variables_sort_unit() -> None:
    variables_sort_unit = settings.variables_sort_unit
    assert variables_sort_unit
    assert all([isinstance(x, str) for x in variables_sort_unit])
