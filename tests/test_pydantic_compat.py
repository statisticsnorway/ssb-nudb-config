import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

import pytest

# Import DotMap directly from its file to avoid triggering package-level
# imports that are unrelated to this test environment.
_DOTMAP_PATH = (
    Path(__file__).parents[1] / "src" / "nudb_config" / "pydantic" / "dotmap.py"
)
_spec = importlib.util.spec_from_file_location("_dotmap_module", _DOTMAP_PATH)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
sys.modules["_dotmap_module"] = _module
_spec.loader.exec_module(_module)
# Tell mypy that the dynamically imported attribute is a class (type)
DotMap = cast(type, _module.DotMap)


def test_missing_attr_on_pydantic_model_triggers_dotmap_getattr() -> None:
    # Simulate a Pydantic-like base: DotMap detects Pydantic at runtime and
    # defers to super().__init__. When pydantic isn't installed, it treats
    # "object" as the base, so any subclass will follow the Pydantic path.
    class DummyBase:
        def __init__(self, *args: object, **kwargs: object) -> None:
            # Accept arbitrary init to mimic BaseModel behavior for this test.
            pass

    if TYPE_CHECKING:

        class Model(DummyBase):
            pass

    else:
        # Create the class dynamically to avoid mypy complaining about using a
        # dynamically imported base in a class definition.
        Model = type("Model", (DotMap, DummyBase), {})

    m = Model(x=1)

    # Access a missing attribute; DotMap.__getattr__ should run and, since
    # no internal mapping exists on a BaseModel mixin, raise AttributeError.
    with pytest.raises(AttributeError):
        _ = m.missing_attribute  # type: ignore[attr-defined]
