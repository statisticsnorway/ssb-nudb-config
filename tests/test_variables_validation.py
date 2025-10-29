from __future__ import annotations

import pytest
from pydantic import ValidationError

from nudb_config.pydantic.variables import Variable


def test_utdatert_with_missing_outdated_comment_raises() -> None:
    with pytest.raises(ValidationError):
        Variable(unit="utdatert", dtype="string")

    with pytest.raises(ValidationError):
        Variable(unit="utdatert", dtype="string", outdated_comment=" ")


def test_utdatert_with_outdated_comment_ok() -> None:
    v = Variable(
        unit="utdatert", dtype="string", outdated_comment="deprecated due to X"
    )
    assert v.outdated_comment == "deprecated due to X"


def test_non_utdatert_without_outdated_comment_ok() -> None:
    v = Variable(unit="na", dtype="string")
    assert v.outdated_comment is None
