from pathlib import Path

import pytest

from nudb_config import settings
from nudb_config.pydantic.load import _load_datasets


def test_baked_flags_in_packaged_datasets() -> None:
    assert settings.datasets.utd_hoeyeste.baked is True
    assert settings.datasets.utd_foreldres_utdnivaa.baked is True
    assert settings.datasets.avslutta.baked is False


@pytest.mark.parametrize(
    ("baked_override", "expected"),
    [("", True), ("baked = false\n", False)],
    ids=["omitted", "explicit-false"],
)
def test_baked_flag_in_dataset_override(
    tmp_path: Path, baked_override: str, expected: bool
) -> None:
    (tmp_path / "datasets.toml").write_text(
        '[datasets.example]\nteam = "team"\nbucket = "bucket"\n'
        'path_glob = "*.parquet"\nbaked = true\n',
        encoding="utf-8",
    )
    (tmp_path / "datasets_override.toml").write_text(
        f'[datasets.example]\nbucket = "other-bucket"\n{baked_override}',
        encoding="utf-8",
    )

    assert _load_datasets(tmp_path).datasets["example"].baked is expected
