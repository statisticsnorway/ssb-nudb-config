from __future__ import annotations

import pytest
from pydantic import ValidationError

from nudb_config.pydantic.variables import Variable


def test_utdatert_with_missing_outdated_comment_raises() -> None:
    with pytest.raises(ValidationError):
        Variable(unit="utdatert", dtype="STRING", name="test_navn")

    with pytest.raises(ValidationError):
        Variable(
            unit="utdatert", dtype="STRING", outdated_comment=" ", name="test_navn"
        )


def test_utdatert_with_outdated_comment_ok() -> None:
    v = Variable(
        unit="utdatert",
        dtype="STRING",
        outdated_comment="deprecated due to X",
        name="test_navn",
    )
    assert v.outdated_comment == "deprecated due to X"


def test_non_utdatert_without_outdated_comment_ok() -> None:
    v = Variable(unit="na", dtype="STRING", name="test_navn")
    assert v.outdated_comment is None
