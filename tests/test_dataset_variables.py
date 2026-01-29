from nudb_config import settings


def test_dataset_variables_are_unique() -> None:
    duplicate_variables: list[tuple[str, str]] = []

    for dataset_name, dataset in settings.datasets.items():
        variables = getattr(dataset, "variables", None) or []
        seen: set[str] = set()
        for variable in variables:
            if variable in seen:
                duplicate_variables.append((dataset_name, variable))
            else:
                seen.add(variable)

    assert not duplicate_variables, (
        "Duplicate entries found in settings.datasets.-dataset names-.variables. Each variable name must be unique "
        f"per dataset: {sorted(duplicate_variables)}"
    )
