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


def test_dataset_specific_renames_are_not_general_renames() -> None:
    dataset_renames: dict[str, list[str]] = {}
    for dataset_name, dataset in settings.datasets.items():
        for old_name, new_name in (dataset.dataset_specific_renames or {}).items():
            dataset_renames.setdefault(old_name.lower(), []).append(
                f"datasets.{dataset_name}.dataset_specific_renames: {old_name!r} -> {new_name!r}"
            )

    conflicts: list[str] = []
    for variable_name, variable in settings.variables.items():
        for old_name in variable.renamed_from or []:
            if mappings := dataset_renames.get(old_name.lower()):
                conflicts.append(
                    f"variables.{variable_name}.renamed_from contains {old_name!r}; "
                    + "; ".join(sorted(mappings))
                )

    assert not conflicts, (
        "Dataset-specific rename sources must not also appear in variables.renamed_from, "
        "even when both mappings have the same target. Keep context-dependent renames "
        "in dataset_specific_renames only. The intended default dataset priority is "
        "avslutta > igang > eksamen, including datasets with prefixes avslutta_, igang_, "
        "and eksamen_; an explicitly selected dataset takes precedence. "
        "To control the mapping as a config contributor, remove the old name from "
        'variables.<new_variable>.renamed_from and add old_name = "new_variable" under '
        "datasets.avslutta.dataset_specific_renames, datasets.igang.dataset_specific_renames, "
        "or datasets.eksamen.dataset_specific_renames as appropriate. "
        "Add an explicit mapping for each dataset family where the old name is used. "
        "Conflicts:\n" + "\n".join(sorted(conflicts))
    )
