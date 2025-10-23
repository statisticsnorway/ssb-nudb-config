from __future__ import annotations

from collections.abc import ItemsView
from collections.abc import KeysView
from collections.abc import ValuesView
from typing import Any
from typing import overload

try:  # Detect Pydantic models without hard-coding a runtime dependency
    from pydantic import BaseModel as _PydanticBaseModel
except Exception:
    _PydanticBaseModel = object  # type: ignore


class DotMap:
    """Provide dot- and item-access for wrappers and Pydantic models.

    Usage:
    - Wrapper: ``DotMap({"a": 1}).a`` and ``DotMap({"a": 1})["a"]``.
    - Base class: ``class M(DotMap, BaseModel): ...`` so ``m.a`` and
      ``m["a"]`` both work, without conflicting with Pydantic's iterator.
    """

    # Avoid __slots__ to stay layout-compatible with Pydantic BaseModel

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a DotMap wrapper or mixin.

        Behavior:
        - When mixed into a Pydantic model, defers to Pydantic's initializer.
        - In wrapper mode, accepts a single mapping positional argument or a
          ``data=`` keyword argument to seed the internal mapping.

        Args:
          args: Optional positional arguments. In wrapper mode, the first
            positional argument can be a mapping used as initial data.
          kwargs: Optional keyword arguments. In wrapper mode, ``data`` can be
            provided as a mapping used as initial data.
        """
        if isinstance(self, _PydanticBaseModel):
            super().__init__(*args, **kwargs)
            return

        data = args[0] if args else kwargs.get("data", {})
        self._data = data if isinstance(data, dict) else {}

    def __getattr__(self, name: str) -> Any:
        """Return attribute from the internal mapping in wrapper mode.

        For Pydantic BaseModel subclasses, this is only invoked for missing
        attributes and therefore does not interfere with normal field access.

        Args:
          name: Attribute name to resolve.

        Returns:
          The value associated with ``name`` from the internal mapping.

        Raises:
          AttributeError: If ``name`` is not present in the mapping.
        """
        try:
            mapping = object.__getattribute__(self, "_data")
        except AttributeError:
            mapping = None
        if isinstance(mapping, dict) and name in mapping:
            return mapping[name]
        raise AttributeError(name)

    def __getitem__(self, key: str | int) -> Any:
        """Return a value via dict-style indexing.

        Prefers attribute access (e.g., Pydantic field) and falls back to the
        internal mapping if the attribute is not found.

        Args:
          key: The key to look up.

        Returns:
          The value associated with ``key``.

        Raises:
          KeyError: If ``key`` is not found.
        """
        if isinstance(key, int):
            key_str: str = list(self.keys())[key]
        elif isinstance(key, str):
            key_str = key
        else:
            raise TypeError("Unrecognized key datatype")

        try:
            return getattr(self, key_str)
        except AttributeError:
            mapping = self._as_mapping()
            try:
                return mapping[key_str]
            except KeyError as exc:
                raise KeyError(key_str) from exc

    def __contains__(self, key: object) -> bool:
        """Return True if ``key`` exists as a field or mapping entry.

        Args:
          key: Candidate key to check. Non-string keys return ``False``.

        Returns:
          Whether the key is present.
        """
        if not isinstance(key, str):
            return False
        fields = getattr(type(self), "model_fields", None)
        if isinstance(fields, dict):
            return key in fields
        mapping = getattr(self, "_data", None)
        return isinstance(mapping, dict) and key in mapping

    def keys(self) -> KeysView[str]:
        """Return a dynamic view of keys across model or mapping."""
        return self._as_mapping().keys()

    def items(self) -> ItemsView[str, Any]:
        """Return a dynamic view of key/value pairs across model or mapping."""
        return self._as_mapping().items()

    def values(self) -> ValuesView[Any]:
        """Return a dynamic view of values across model or mapping."""
        return self._as_mapping().values()

    @overload
    def get(self, key: str) -> Any | None: ...

    @overload
    def get(self, key: str, default: Any) -> Any: ...

    def get(self, key: str, default: Any | None = None) -> Any:
        """Return the value for ``key`` if present; otherwise ``default``.

        Tries attribute access first and then falls back to the mapping view.

        Args:
          key: The key to look up.
          default: Value to return if ``key`` is not found.

        Returns:
          The found value or ``default`` if absent.
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return self._as_mapping().get(key, default)

    def _as_mapping(self) -> dict[str, Any]:
        """Return a mapping view of the instance data.

        Uses ``model_dump`` for Pydantic models; otherwise returns the
        internal ``_data`` mapping or an empty dict.

        Returns:
          A dictionary representation of the current data.
        """
        model_dump = getattr(self, "model_dump", None)
        if callable(model_dump):
            dumped_model: dict[str, Any] = model_dump()
            return dumped_model
        mapping = getattr(self, "_data", None)
        return mapping if isinstance(mapping, dict) else {}

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the DotMap."""
        return f"DotMap({self._as_mapping()!r})"
