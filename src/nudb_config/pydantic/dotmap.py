from __future__ import annotations

from collections.abc import ItemsView
from collections.abc import Iterator
from collections.abc import KeysView
from collections.abc import Mapping
from collections.abc import ValuesView
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import cast
from typing import get_args
from typing import overload

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

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
    - When mixed into Pydantic models, initialization defers to Pydantic;
      otherwise a mapping positional argument or ``data=`` keyword seeds the
      internal store.
    """

    # Avoid __slots__ to stay layout-compatible with Pydantic BaseModel

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
          Any: The value associated with ``name`` from the internal mapping.

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
          Any: The value associated with ``key``.

        Raises:
          KeyError: If ``key`` is not found.
          TypeError: If ``key`` is not a string or integer index.
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

    def __setitem__(self, key: str | int, value: Any) -> None:
        """Assign a value via dict-style indexing.

        For Pydantic models, this sets the field/attribute so validation can
        run. For wrapper usage, this stores into the internal mapping.

        Args:
          key: The key to assign.
          value: The value to store.

        Raises:
          TypeError: If ``key`` is not a string or integer index.
        """
        if isinstance(key, int):
            key_str: str = list(self.keys())[key]
        elif isinstance(key, str):
            key_str = key
        else:
            raise TypeError("Unrecognized key datatype")

        try:
            setattr(self, key_str, value)
        except AttributeError:
            mapping = getattr(self, "_data", None)
            if not isinstance(mapping, dict):
                mapping = {}
                object.__setattr__(self, "_data", mapping)
            mapping[key_str] = value

    def __contains__(self, key: object) -> bool:
        """Return True if ``key`` exists as a field or mapping entry.

        Args:
          key: Candidate key to check. Non-string keys return ``False``.

        Returns:
          bool: Whether the key is present.
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
          Any: The found value or ``default`` if absent.
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
          dict[str, Any]: A dictionary representation of the current data.
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


class DotMapBaseModel(_PydanticBaseModel, DotMap):
    """Combines the Dotmap class with Basemodel, placing BaseModel first."""

    pass


T = TypeVar("T")


class DotMapDict(Generic[T]):
    """Dictionary wrapper that supports both attribute and item access."""

    def __init__(
        self, data: Mapping[str, T] | None = None, *, value_type: type[T] | None = None
    ) -> None:
        self._data: dict[str, T] = dict(data or {})
        if value_type is Any:
            value_type = None
        self._value_type: type[T] | None = value_type

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Build a Pydantic core schema for typed dict-like validation."""
        args = get_args(source_type)
        value_type = args[0] if args else Any
        dict_schema = core_schema.dict_schema(
            keys_schema=core_schema.str_schema(),
            values_schema=handler.generate_schema(value_type),
        )

        union_schema = core_schema.union_schema(
            [core_schema.is_instance_schema(cls), dict_schema]
        )

        def build(value: Mapping[str, Any] | DotMapDict[Any]) -> DotMapDict[Any]:
            if isinstance(value, cls):
                return value
            data = cast(Mapping[str, Any], value)
            init_type = value_type if isinstance(value_type, type) else None
            return cls(data, value_type=cast(type[Any] | None, init_type))

        return core_schema.no_info_after_validator_function(build, union_schema)

    def __getitem__(self, key: str | int) -> T:
        """Return a value via dict-style indexing."""
        if isinstance(key, int):
            key = list(self._data.keys())[key]
        if not isinstance(key, str):
            raise TypeError("Unrecognized key datatype")
        try:
            return self._data[key]
        except KeyError as exc:
            raise KeyError(key) from exc

    def __setitem__(self, key: str | int, value: T) -> None:
        """Assign a value via dict-style indexing, coercing to the target type."""
        if isinstance(key, int):
            key = list(self._data.keys())[key]
        if not isinstance(key, str):
            raise TypeError("Unrecognized key datatype")
        self._data[key] = self._coerce_value(value)

    def __delitem__(self, key: str) -> None:
        """Delete the item associated with ``key``."""
        del self._data[key]

    def __iter__(self) -> Iterator[T]:
        """Iterate over values (to mirror Dynaconf-like behavior)."""
        return iter(self._data.values())

    def __len__(self) -> int:
        """Return the number of stored entries."""
        return len(self._data)

    def __getattr__(self, name: str) -> T:
        """Return a value via attribute access."""
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: T) -> None:
        """Assign a value via attribute access, coercing to the target type."""
        if name.startswith("_") or name in type(self).__dict__:
            object.__setattr__(self, name, value)
            return
        self._data[name] = self._coerce_value(value)

    def __contains__(self, key: object) -> bool:
        """Return True if ``key`` is present in the mapping."""
        return isinstance(key, str) and key in self._data

    def keys(self) -> KeysView[str]:
        """Return a dynamic view of keys."""
        return self._data.keys()

    def items(self) -> ItemsView[str, T]:
        """Return a dynamic view of key/value pairs."""
        return self._data.items()

    def values(self) -> ValuesView[T]:
        """Return a dynamic view of values."""
        return self._data.values()

    @overload
    def get(self, key: str) -> T | None: ...

    @overload
    def get(self, key: str, default: T) -> T: ...

    def get(self, key: str, default: T | None = None) -> T | None:
        """Return the value for ``key`` if present; otherwise ``default``."""
        return self._data.get(key, default)

    def _coerce_value(self, value: T) -> T:
        """Convert or validate values against the configured target type."""
        value_type = self._value_type
        if value_type is None:
            return value
        if isinstance(value, value_type):
            return value
        model_validate = getattr(value_type, "model_validate", None)
        if callable(model_validate):
            return cast(T, model_validate(value))
        return value

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the DotMapDict."""
        return f"DotMapDict({self._data!r})"
