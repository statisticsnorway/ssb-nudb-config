from nudb_config import settings


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
        if not (codelist_filled or variant_filled):
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
