from nudb_config.pydantic.dotmap import DotMapDict
from nudb_config.pydantic.load import _merge_mapping
from nudb_config.pydantic.variables import Variable


def test_merge_mapping_injects_variable_name_for_new_entry() -> None:
    target: DotMapDict[Variable] = DotMapDict(value_type=Variable)

    _merge_mapping(
        target,
        {"fullfort_gk": {"unit": "vgogjen", "dtype": "STRING", "length": [2]}},
    )

    assert "fullfort_gk" in target
    assert isinstance(target.fullfort_gk, Variable)
    assert target.fullfort_gk.name == "fullfort_gk"


def test_merge_mapping_updates_existing_and_deletes_none() -> None:
    target: DotMapDict[Variable] = DotMapDict(value_type=Variable)
    target["bar"] = Variable.model_validate(
        {
            "name": "bar",
            "unit": "old",
            "dtype": "STRING",
            "length": [2],
        }
    )
    target["remove_me"] = Variable.model_validate(
        {
            "name": "remove_me",
            "unit": "old",
            "dtype": "STRING",
        }
    )

    _merge_mapping(
        target,
        {
            "bar": {"unit": "new"},
            "remove_me": "None",
        },
    )

    assert target.bar.unit == "new"
    assert "remove_me" not in target
