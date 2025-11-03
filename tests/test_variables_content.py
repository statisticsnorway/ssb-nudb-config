from nudb_config import settings

def test_variables_sort_unit():
    variables_sort_unit = settings.variables.variables_sort_unit
    assert len(variables_sort_unit)
    assert all([isinstance(x, str) for x in variables_sort_unit])