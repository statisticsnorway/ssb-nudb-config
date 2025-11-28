from nudb_config import settings


def test_all_dataset_variables_are_defined() -> None:
    defined_variables = set(settings.variables.keys())
    referenced_variables = {
        variable
        for dataset in settings.datasets.values()
        for variable in getattr(dataset, "variables", []) or []
    }

    missing_definitions = referenced_variables - defined_variables

    assert not missing_definitions, (
        "Variables referenced in settings.datasets.-dataset names-.variables that are missing definitions in "
        f"variable-toml-files: {sorted(missing_definitions)}. Did you rename them, or add them in just one of these places?"
    )
