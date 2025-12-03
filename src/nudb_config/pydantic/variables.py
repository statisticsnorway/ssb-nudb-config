from __future__ import annotations

from typing import Any

import klass
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from .dotmap import DotMap


class Variable(BaseModel, DotMap):
    """Definition of a single variable from ``variables.toml``.

    Attributes:
        unit: Logical grouping the variable belongs to.
        dtype: Storage or semantic type of the variable.
        length: Allowed lengths for string fields, if constrained.
        klass_codelist: KLASS codelist identifier, if applicable.
        klass_variant: KLASS variant identifier, if applicable.
        renamed_from: Previous column name(s) that map to this variable.
        codelist_extras: Additional code mappings injected at load time.
    """

    name: str
    unit: str
    dtype: str
    description_short: str | None = None
    length: list[int] | None = None
    klass_codelist: int | None = None
    klass_codelist_from_date: str | None = None
    klass_variant: int | None = None
    klass_variant_search_term: str | None = None
    renamed_from: list[str] | None = None
    derived_from: list[str] | None = None
    # Populated programmatically to mirror Dynaconf expansion
    codelist_extras: dict[str, str] | None = None
    outdated_comment: str | None = None

    # Populated by find_var or similar functions that actually fetch from klass
    klass_codelist_metadata: klass.KlassClassification | None = None
    klass_variant_metadata: klass.KlassVariant | None = None

    # klass.* types come from an external package without Pydantic hooks.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _require_outdated_comment_when_utdatert(self) -> Variable:
        """Ensure ``outdated_comment`` is set when ``unit`` is ``utdatert``.

        Treats ``None``, empty, and whitespace-only strings as invalid.
        """
        if self.unit == "utdatert":
            if self.outdated_comment is None or not str(self.outdated_comment).strip():
                raise ValueError(
                    'outdated_comment is required when unit="utdatert" and cannot be blank'
                )
        return self

    @model_validator(mode="after")
    def _require_klass_codelist_to_be_positive_int(self) -> Variable:
        if (
            self.klass_codelist is not None
        ):  # Wont raise error if it is the default None
            if not isinstance(self.klass_codelist, int) or self.klass_codelist < 0:
                raise ValueError(
                    "If klass_codelist is filled, it must be an int of 0 or above. 0 means the variable is never supposed to have a codelist, variant or similar in klass."
                )
        return self


class VariablesFile(BaseModel, DotMap):
    """Root schema of ``variables.toml``.

    Attributes:
        variables_sort_unit: Preferred order of variable units.
        variables: Mapping of variable name to its definition.
    """

    variables_sort_unit: list[str] | None = None
    variables: dict[str, Variable]

    @model_validator(mode="before")
    @classmethod
    def _inject_variable_names(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Ensure each Variable inherits its key as the ``name`` attribute."""
        variables = data.get("variables")
        if isinstance(variables, dict):
            enriched: dict[str, Any] = {}
            for name, definition in variables.items():
                if isinstance(definition, Variable):
                    definition.name = name
                    enriched[name] = definition
                    continue
                if isinstance(definition, dict):
                    enriched[name] = {**definition, "name": name}
                    continue
                enriched[name] = definition
            data["variables"] = enriched
        return data
