from __future__ import annotations

from collections.abc import ItemsView
from collections.abc import KeysView
from collections.abc import ValuesView
from typing import Any
from typing import overload

try:  # Detect Pydantic models without hard-coding a runtime dependency
    from pydantic import BaseModel as _PydanticBaseModel  # type: ignore
except Exception:  # pragma: no cover
    _PydanticBaseModel = object  # type: ignore


class DotMap:
    """Provide dot- and item-access for wrappers and Pydantic models.

    Usage:
    - Wrapper: ``DotMap({"a": 1}).a`` and ``DotMap({"a": 1})["a"]``.
    - Base class: ``class M(DotMap, BaseModel): ...`` so ``m.a`` and
      ``m["a"]`` both work, without conflicting with Pydantic's iterator.
    """

    # Avoid __slots__ to stay layout-compatible with Pydantic BaseModel

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        # When used as a BaseModel mixin, defer to Pydantic's initializer.
        if isinstance(self, _PydanticBaseModel):
            super().__init__(*args, **kwargs)
            return

        # Wrapper mode: accept a single mapping positional arg or 'data=' kwarg
        data = args[0] if args else kwargs.get("data", {})
        self._data = data if isinstance(data, dict) else {}

    # Attribute access (for wrapper mode). For BaseModel subclasses this is
    # only invoked for missing attributes and thus does not interfere.
    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        mapping = getattr(self, "_data", None)
        if isinstance(mapping, dict) and name in mapping:
            return mapping[name]
        raise AttributeError(name)

    # Dict-style item access. Prefer attributes (BaseModel fields), then fall
    # back to a mapping view.
    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            mapping = self._as_mapping()
            try:
                return mapping[key]
            except KeyError as exc:
                raise KeyError(key) from exc

    def __contains__(self, key: object) -> bool:  # pragma: no cover
        if not isinstance(key, str):
            return False
        fields = getattr(self, "model_fields", None)
        if isinstance(fields, dict):
            return key in fields
        mapping = getattr(self, "_data", None)
        return isinstance(mapping, dict) and key in mapping

    def keys(self) -> KeysView[str]:  # pragma: no cover
        return self._as_mapping().keys()

    def items(self) -> ItemsView[str, Any]:  # pragma: no cover
        return self._as_mapping().items()

    def values(self) -> ValuesView[Any]:  # pragma: no cover
        return self._as_mapping().values()

    @overload
    def get(self, key: str) -> Any | None: ...

    @overload
    def get(self, key: str, default: Any) -> Any: ...

    def get(self, key: str, default: Any | None = None) -> Any:  # pragma: no cover
        try:
            return getattr(self, key)
        except AttributeError:
            return self._as_mapping().get(key, default)

    # Internal helper to provide a mapping view across modes
    def _as_mapping(self) -> dict[str, Any]:  # pragma: no cover
        model_dump = getattr(self, "model_dump", None)
        if callable(model_dump):
            return model_dump()
        mapping = getattr(self, "_data", None)
        return mapping if isinstance(mapping, dict) else {}

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"DotMap({self._as_mapping()!r})"
