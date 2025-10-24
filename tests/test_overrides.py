import textwrap
from pathlib import Path

import pytest

from nudb_config import settings


def write(p: Path, content: str) -> None:
    p.write_text(textwrap.dedent(content), encoding="utf-8")


def test_apply_overrides_from_dir(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    # Prepare override TOML files
    write(
        tmp_path / "settings.toml",
        """
        short_name = "overridden-name"
        unknown_key = "not-allowed"
        """,
    )

    write(
        tmp_path / "variables.toml",
        """
        variables_sort_unit = ["custom"]

        top_unknown = true

        [variables]
          [variables.fnr]
            unit = "person"
            dtype = "STRING"
            length = [10]
            nonsense = 123
        """,
    )

    write(
        tmp_path / "datasets.toml",
        """
        [datasets]
          [datasets.testset]
            variables = ["fnr"]
            extra_field = 1
        """,
    )

    write(
        tmp_path / "paths.toml",
        """
        [paths]
          [paths.local_daplalab]
            katalog = "/override/catalog/"
            extra = "ignored"
        """,
    )

    # Apply overrides
    with caplog.at_level("WARNING"):
        settings.apply_overrides_from_dir(tmp_path)

    # Verify overrides applied
    assert settings.short_name == "overridden-name"
    assert settings.variables_sort_unit == ["custom"]

    # Variables override applied and type-checked
    assert settings.variables.fnr.dtype == "STRING"
    assert settings.variables.fnr.length == [10]

    # Datasets merged
    assert "testset" in settings.datasets
    assert settings.datasets["testset"].variables == ["fnr"]

    # Paths override applied
    assert settings.paths.local_daplalab.katalog == "/override/catalog/"

    # Unknown keys warned (at least some representative ones)
    warnings_joined = "\n".join(m.message for m in caplog.records)
    assert "unknown_key" in warnings_joined
    assert "top_unknown" in warnings_joined
    assert "nonsense" in warnings_joined
    assert "extra_field" in warnings_joined
    assert "extra" in warnings_joined

