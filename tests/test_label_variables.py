import importlib.resources as impres
import tomllib
from pathlib import Path

import pytest

from nudb_config.pydantic.load import load_pydantic_settings


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({"klass_codelist": 36}, True),
        ({"klass_variant": 123}, True),
        ({"klass_codelist": 36, "klass_variant_search_term": "Grouping"}, True),
        ({"klass_codelist": 139, "klass_correspondence_to": 36}, True),
        ({"klass_codelist": 131, "klass_use_relative_time": True}, True),
        ({}, False),
        ({"klass_codelist": 0}, False),
        ({"klass_codelist": 0, "klass_variant": 123}, False),
        ({"klass_variant": 0}, False),
        ({"klass_codelist": 36, "dtype": "BOOLEAN"}, False),
        ({"klass_codelist": 36, "outdated_comment": "Retired"}, False),
        (
            {"klass_codelist": 36, "unit": "utdatert", "outdated_comment": "Retired"},
            False,
        ),
    ],
)
def test_label_eligibility_after_external_merge(
    tmp_path: Path, metadata: dict[str, object], expected: bool
) -> None:
    import json

    fields = {"unit": "fag", "dtype": "STRING", **metadata}
    lines = ["[variables.example]"]
    for key, value in fields.items():
        lines.append(f"{key} = {json.dumps(value)}")
    (tmp_path / "variables.toml").write_text("\n".join(lines), encoding="utf-8")

    settings = load_pydantic_settings().merge_tomls(tmp_path)

    assert ("example_label" in settings.variables) is expected
    if expected:
        label = settings.variables.example_label
        assert label.name == "example_label"
        assert label.unit == "fag"
        assert label.dtype == "STRING"
        assert label.derived_from == ["example"]
        assert label.klass_codelist is None
        assert label.klass_variant is None
        assert "example_label_label" not in settings.variables


def test_generated_labels_inherit_updated_parent_unit(tmp_path: Path) -> None:
    settings = load_pydantic_settings()
    path = tmp_path / "variables.toml"
    path.write_text('[variables.nus2000]\nunit = "utd"\n', encoding="utf-8")

    settings.merge_tomls(tmp_path)
    assert settings.variables.nus2000_label.unit == settings.variables.nus2000.unit

    names = set(settings.variables.keys())
    settings.merge_tomls(tmp_path)
    assert set(settings.variables.keys()) == names
    assert "nus2000_label_label" not in settings.variables


def test_package_tomls_reserve_label_variable_names() -> None:
    config_dir = Path(str(impres.files("nudb_config"))) / "config_tomls"
    offenders: list[str] = []
    for path in config_dir.rglob("*.toml"):
        with path.open("rb") as stream:
            variables = tomllib.load(stream).get("variables", {})
        offenders.extend(
            f"{path.name}: {name}" for name in variables if name.endswith("_label")
        )
    assert not offenders, (
        "The _label suffix is reserved for dynamically generated variables; "
        f"remove these TOML definitions: {sorted(offenders)}"
    )


def test_label_generation_uses_all_merged_variable_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    config_dir = tmp_path / "config_tomls"
    config_dir.mkdir()
    original_dir = Path(str(impres.files("nudb_config"))) / "config_tomls"
    for filename in ("settings.toml", "options.toml", "constants.toml", "paths.toml"):
        (config_dir / filename).write_bytes((original_dir / filename).read_bytes())
    (config_dir / "variables.toml").write_text(
        '[variables.example]\nunit = "fag"\ndtype = "STRING"\nklass_codelist = 36\n',
        encoding="utf-8",
    )
    (config_dir / "variables_derived_external.toml").write_text(
        '[variables.example]\nunit = "utd"\ndtype = "STRING"\nklass_codelist = 139\n'
        '[variables.external]\nunit = "pers"\ndtype = "STRING"\nklass_codelist = 91\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(impres, "files", lambda _: tmp_path)

    settings = load_pydantic_settings()

    assert settings.variables.example_label.unit == "utd"
    assert settings.variables.external_label.derived_from == ["external"]
    assert not any(name.endswith("_label_label") for name in settings.variables.keys())
