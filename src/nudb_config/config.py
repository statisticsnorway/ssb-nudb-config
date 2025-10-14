from pathlib import Path
import importlib.resources as impres

from dynaconf import Dynaconf # type: ignore
from dynaconf import Validator

config_paths = list(Path(str(impres.files("nudb_config"))).glob("config_tomls/*.toml"))


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=config_paths,
)


# Expand codelists
def expand_codelist(settings: Dynaconf, var_name: str, klass_id: int) -> None:
    """Expand codelist with certain known values missing from KLASS.

    Args:
        settings: The combined settings for this package.
        var_name: Name of variable
        klass_id: Klass id

    Returns:
        None
    """
    if klass_id == 91:
        settings.variables[var_name]["codelist_extras"] = {
            "151": "DDR / Øst-Tyskland",
            "135": "SSSR / Sovjetunionen",
        }
    if klass_id == 131:
        settings.variables[var_name]["codelist_extras"] = {
            "2580": "360s definerte Utland",
            "2111": "Longyearbyen arealplanområde",
        }
        # Hva med alle "kjent fylke, men ukjent kommune, som ender i "00"?
    return None


for k, v in settings.variables.items():
    # all variables should have a defined dtype
    settings.validators.register(
        Validator(f"variables.{k}.dtype", must_exist=True, is_type_of=str),
    )
    if "length" in v:
        settings.validators.register(
            Validator(f"variables.{k}.length", is_type_of=list),
        )
    if "klass_codelist" in v:
        settings.validators.register(
            Validator(f"variables.{k}.klass_codelist", gte=1, is_type_of=int),
        )
        expand_codelist(settings, k, v["klass_codelist"])
    if "klass_variant" in v:
        settings.validators.register(
            Validator(f"variables.{k}.klass_variant", gte=1, is_type_of=int),
        )
    if "renamed_from" in v:
        settings.validators.register(
            Validator(f"variables.{k}.renamed_from", is_type_of=str | list),
        )


settings.validators.validate_all()
