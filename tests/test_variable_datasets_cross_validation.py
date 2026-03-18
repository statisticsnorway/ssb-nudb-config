from nudb_config import settings


def test_all_dataset_variables_are_defined() -> None:
    defined_variables = set(settings.variables.keys())
    referenced_variables = {
        variable
        for dataset in settings.datasets.values()
        for variable in getattr(dataset, "variables", []) or []
        if dataset.team
        == "utd-nudb"  # We are not taking responsibility for definition of variables in external datasets
    }

    missing_definitions = referenced_variables - defined_variables

    assert not missing_definitions, (
        "Variables referenced in settings.datasets.-dataset names-.variables that are missing definitions in "
        f"variable-toml-files: {sorted(missing_definitions)}. Did you rename them, or add them in just one of these places?"
    )


def test_derived_join_keys_are_in_derived_from() -> None:
    missing_join_keys = []

    for variable in settings.variables.values():
        join_keys = getattr(variable, "derived_join_keys", None)
        if not join_keys:
            continue
        derived_from = set(getattr(variable, "derived_from", []) or [])
        missing = [key for key in join_keys if key not in derived_from]
        if missing:
            missing_join_keys.append((variable.name, missing))

    assert not missing_join_keys, (
        "Derived join keys referenced in settings.variables.-variable names-.derived_join_keys that are missing from "
        f"derived_from: {sorted(missing_join_keys)}. Did you rename them, or add them in just one of these places?"
    )
