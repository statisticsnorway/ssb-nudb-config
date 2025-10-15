from __future__ import annotations

from typing import Any


class SubscriptableModel:
    """Mixin that enables dict-style subscription on Pydantic models.

    This provides ``__getitem__`` so fields can be accessed via
    ``model["field"]`` in addition to standard attribute access.
    """

    def __getitem__(self, key: str) -> Any:
        """Return a field value by key.

        Mirrors attribute access (e.g., ``model["field"]`` == ``model.field``).

        Args:
            key (str): Name of the field to access.

        Returns:
            Any: Value of the requested field.

        Raises:
            KeyError: If ``key`` is not a defined field on the model.
        """
        try:
            return getattr(self, key)
        except AttributeError as exc:  # pragma: no cover - defensive
            raise KeyError(key) from exc
