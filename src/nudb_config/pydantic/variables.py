from __future__ import annotations

from pydantic import BaseModel


class Variable(BaseModel):
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
    length: list[int] | None = None
    klass_codelist: int | None = None
    klass_variant: int | None = None
    renamed_from: str | list[str] | None = None
    # Populated programmatically to mirror Dynaconf expansion
    codelist_extras: dict[str, str] | None = None


class VariablesFile(BaseModel):
    """Root schema of ``variables.toml``.

    Attributes:
        variables_sort_unit: Preferred order of variable units.
        variables: Mapping of variable name to its definition.
    """

    variables_sort_unit: list[str] | None = None
    variables: dict[str, Variable]
