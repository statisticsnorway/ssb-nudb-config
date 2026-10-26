from nudb_config import settings


def test_klass_codelist_131_requires_relative_time() -> None:
    offenders = [
        name
        for name, var in settings.variables.items()
        if var.klass_codelist == 131 and var.klass_use_relative_time is not True
    ]

    assert not offenders, (
        "When defined as kommuner, klass_use_relative_time should be True: "
        f"{sorted(offenders)}"
    )


def test_klass_codelist_present_when_variant_metadata_present() -> None:
    offenders: list[str] = []

    for name, var in settings.variables.items():
        has_correspondence = getattr(var, "klass_correspondence_to", None) is not None
        has_variant_search = bool(getattr(var, "klass_variant_search_term", None))
        if has_correspondence or has_variant_search:
            if getattr(var, "klass_codelist", None) is None:
                offenders.append(name)

    assert offenders == [], (
        '"klass_codelist" must be set whenever "klass_correspondence_to" or '
        f'"klass_variant_search_term" is provided: {sorted(offenders)}'
    )


def test_klass_codelist_or_variant_requires_length_list_of_ints() -> None:
    offenders: list[str] = []

    for name, var in settings.variables.items():
        codelist_filled = getattr(var, "klass_codelist", None) not in (None, 0)
        variant_filled = getattr(var, "klass_variant", None) is not None
        if getattr(var, "dtype", "") == "BOOLEAN" or not (
            codelist_filled or variant_filled
        ):
            continue

        length = getattr(var, "length", None)
        if not (
            isinstance(length, list)
            and length
            and all(isinstance(x, int) for x in length)
        ):
            offenders.append(name)

    assert offenders == [], (
        "Variables with 'klass_codelist' or 'klass_variant' must declare a non-empty "
        "list of ints for the variable-field length: "
        f"{sorted(offenders)}"
    )


def test_derived_from_references_existing_variables() -> None:
    missing_dependencies: dict[str, list[str]] = {}
    known_variables = set(settings.variables.keys())

    for name, var in settings.variables.items():
        if not var.derived_from:
            continue

        missing = [
            ref
            for ref in var.derived_from
            if not isinstance(ref, str) or ref not in known_variables
        ]
        if missing:
            missing_dependencies[name] = missing

    assert not missing_dependencies, (
        "derived_from references must point to existing variables: "
        f"{missing_dependencies}"
    )


def test_derived_relevant_datasets_reference_existing_datasets() -> None:
    missing_datasets: dict[str, list[str]] = {}
    # nudb-use creates this virtual dataset with one row per person;
    # virtual datasets are not currently represented in settings.datasets.
    virtual_datasets = {"utd_person"}
    known_datasets = set(settings.datasets.keys()) | virtual_datasets

    for name, var in settings.variables.items():
        missing = [
            dataset
            for dataset in var.derived_relevant_datasets or []
            if dataset not in known_datasets
        ]
        if missing:
            missing_datasets[name] = missing

    assert not missing_datasets, (
        "derived_relevant_datasets references must point to datasets in "
        "settings.datasets or explicitly allowed virtual datasets: "
        f"{missing_datasets}"
    )


def test_uh_foerste_nus2000_sources_and_relevant_dataset() -> None:
    variable = settings.variables["uh_foerste_nus2000"]

    # Derive the person's first UH education from course records,
    # then attach the result to the virtual dataset with one row per person.
    assert variable.derived_uses_datasets is not None
    assert set(variable.derived_uses_datasets) == {"avslutta", "igang", "eksamen"}
    assert variable.derived_relevant_datasets == ["utd_person"]


def test_variables_with_codelist_have_label_variant() -> None:
    offenders: list[str] = []

    for name, var in settings.variables.items():
        klass_codelist = getattr(var, "klass_codelist", None)
        if not (isinstance(klass_codelist, int) and klass_codelist > 0):
            continue

        dtype = str(getattr(var, "dtype", "") or "").upper()
        outdated_comment = getattr(var, "outdated_comment", None)
        outdated_filled = bool(outdated_comment) and str(outdated_comment).strip() != ""

        # Boolean or explicitly outdated variables should not require a label variant
        if dtype == "BOOLEAN" or outdated_filled:
            continue

        if f"{name}_label" not in settings.variables:
            offenders.append(name)

    assert offenders == [], (
        "Variables with 'klass_codelist' > 0 must have a corresponding "
        f"`*_label` entry: {sorted(offenders)}"
    )
