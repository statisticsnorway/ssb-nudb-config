from nudb_config import settings


def test_variables_sort_unit() -> None:
    variables_sort_unit = settings.variables_sort_unit
    assert variables_sort_unit
    assert all([isinstance(x, str) for x in variables_sort_unit])

def test_variables_name_field() -> None:
    assert all([isinstance(x.name, str) and len(x.name) for x in settings.variables])