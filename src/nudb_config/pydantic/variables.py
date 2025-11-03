from __future__ import annotations

from pydantic import BaseModel
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

    unit: str
    dtype: str
    description_short: str | None = None
    length: list[int] | None = None
    klass_codelist: int | None = None
    klass_codelist_from_date: str | None = None
    klass_variant: int | None = None
    renamed_from: list[str] | None = None
    # Populated programmatically to mirror Dynaconf expansion
    codelist_extras: dict[str, str] | None = None
    outdated_comment: str | None = None

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


class VariablesFile(BaseModel, DotMap):
    """Root schema of ``variables.toml``.

    Attributes:
        variables_sort_unit: Preferred order of variable units.
        variables: Mapping of variable name to its definition.
    """

    variables_sort_unit: list[str] | None = None
    variables: dict[str, Variable]
