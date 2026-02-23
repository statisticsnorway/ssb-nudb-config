from __future__ import annotations

from typing import Any
from typing import Literal

import klass
from pydantic import ConfigDict
from pydantic import model_validator

from .dotmap import DotMapBaseModel
from .dotmap import DotMapDict

DTYPE_FIELD_TYPE = Literal["INTEGER", "FLOAT", "STRING", "DATETIME", "BOOLEAN"]


class Variable(DotMapBaseModel):
    """Definition of a single variable from ``variables.toml``.

    Attributes:
        name: Variable name injected from its TOML key.
        unit: Logical grouping the variable belongs to.
        dtype: Storage or semantic type of the variable.
        description_short: Optional short description.
        length: Allowed lengths for string fields, if constrained.
        klass_codelist: KLASS codelist identifier, if applicable.
        klass_codelist_from_date: Earliest date for the codelist.
        klass_variant: KLASS variant identifier, if applicable.
        klass_variant_search_term: Search term used to find a variant.
        klass_correspondence_to: The Classification ID for what we are mapping from the klass_codelist to.
        klass_codelist_metadata: Metadata fetched from KLASS for the codelist.
        klass_variant_metadata: Metadata fetched from KLASS for the variant.
        renamed_from: Previous column name(s) that map to this variable.
        derived_from: Source variables used to derive this value.
        derived_uses_datasets: Names of datasets a derived variable should be derived from (in the cases it is "all-data dependent").
        derived_join_keys: The keys the derived variable can be joined back on a dataset with, if its a variable with one value per person, this could be just "snr" for example.
        derived_values_priority: The priority of which values to keep if derive variable already exists in the data.
        codelist_extras: Additional code mappings injected at load time.
        outdated_comment: Explanation when the unit is outdated.
        model_config: Pydantic configuration allowing arbitrary KLASS types.

    """

    name: str
    unit: str
    dtype: DTYPE_FIELD_TYPE
    description_short: str | None = None
    length: list[int] | None = None

    klass_codelist: int | None = None
    klass_codelist_from_date: str | None = None
    klass_variant: int | None = None
    klass_variant_search_term: str | None = None
    klass_correspondence_to: int | None = None
    # Populated by find_var or similar functions that actually fetch from klass
    klass_codelist_metadata: klass.KlassClassification | None = None
    klass_variant_metadata: klass.KlassVariant | None = None

    renamed_from: list[str] | None = None

    derived_from: list[str] | None = None
    derived_uses_datasets: list[str] | None = None
    derived_join_keys: list[str] | None = None
    derived_values_priority: str | None = None

    # Populated programmatically to mirror Dynaconf expansion
    codelist_extras: dict[str, str] | None = None
    outdated_comment: str | None = None

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


class VariablesFile(DotMapBaseModel):
    """Root schema of ``variables.toml``.

    Attributes:
        variables_sort_unit: Preferred order of variable units.
        variables: Mapping of variable name to its definition.
    """

    variables_sort_unit: list[str] | None = None
    variables: DotMapDict[Variable]

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
