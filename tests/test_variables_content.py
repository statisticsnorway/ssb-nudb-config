from nudb_config import settings


def test_variables_sort_unit() -> None:
    variables_sort_unit = settings.variables_sort_unit
    assert variables_sort_unit
    assert all([isinstance(x, str) for x in variables_sort_unit])


def test_variables_name_field() -> None:
    assert all([isinstance(x.name, str) and len(x.name) for x in settings.variables])

def test_nus_label_klass_variable_dynamic_created() -> None:
    assert "fa_studiepoeng_nus_label" in settings.variables.keys()

def test_renamed_from_entries_are_unique_across_variables() -> None:
    renamed_index: dict[str, str] = {}
    duplicates: list[str] = []

    for var_name, variable in settings.variables.items():
        for old_name in variable.renamed_from or []:
            first_seen = renamed_index.setdefault(old_name, var_name)
            if first_seen != var_name:
                duplicates.append(f"{old_name} -> {first_seen}, {var_name}")

    assert not duplicates, (
        "renamed_from values must be unique across variables; duplicates found: "
        + "; ".join(sorted(duplicates))
    )
