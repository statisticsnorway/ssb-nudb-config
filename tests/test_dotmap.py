from nudb_config.pydantic.dotmap import DotMap
import pytest

def test_dotmap_get_basic() -> None:
    """Test the get convenience method on the Dotmap class."""
    dm = DotMap({"a": 1, "b": 2})

    # existing key
    assert dm.get("a") == 1

    # missing without default -> None
    assert dm.get("missing") is None

    # missing with default -> default
    assert dm.get("missing", 42) == 42

    # Testing __contains__()
    assert "a" in dm
    
    # Should raise an error if the element is not there
    with pytest.raises(KeyError):
        dm["c"]


