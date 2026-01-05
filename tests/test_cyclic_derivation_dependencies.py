from nudb_config import settings


class CyclicGraphError(Exception): ...


def variable_is_cyclic_depth_first_search(
    variable: str,
    derived_graph: dict[str, list[str]],
    visited: set[str] | None = None,
    fail_on_cyclic: bool = False,
) -> bool:
    visited = visited or set()

    if variable in visited:
        if fail_on_cyclic:
            raise CyclicGraphError(
                f"There are cyclic 'derived_from' dependencies, '{variable}' depends on itself!"
            )
        return True

    elif variable not in derived_graph.keys():
        return False

    derived_from: list[str] = derived_graph[variable]
    visited_next: set[str] = visited | {variable}

    for variable_next in derived_from:
        from_is_cyclic = variable_is_cyclic_depth_first_search(
            variable=variable_next,
            derived_graph=derived_graph,
            visited=visited_next,
            fail_on_cyclic=fail_on_cyclic,
        )

        if from_is_cyclic:
            return True

    return False


def is_cyclic_depth_first_search(
    derived_graph: dict[str, list[str]], fail_on_cyclic: bool = False
) -> bool:
    for variable in derived_graph.keys():
        is_cyclic = variable_is_cyclic_depth_first_search(
            variable=variable,
            derived_graph=derived_graph,
            fail_on_cyclic=fail_on_cyclic,
        )

        if is_cyclic:
            return True

    return False


def test_cyclic_graph() -> None:
    cyclic_graph: dict[str, list[str]] = {
        "a": ["b"],
        "b": ["c", "d"],
        "c": ["e"],
        "e": ["a"],
    }

    assert is_cyclic_depth_first_search(cyclic_graph)


def test_non_cyclic_graph() -> None:
    non_cyclic_graph: dict[str, list[str]] = {
        "a": ["b"],
        "b": ["c", "d"],
        "c": ["e"],
        "e": ["f"],
    }

    assert not is_cyclic_depth_first_search(non_cyclic_graph)


def test_cyclic_derived_from() -> None:
    variables = settings.variables
    derived_graph = {k: v.derived_from for k, v in variables.items() if v.derived_from}

    assert not is_cyclic_depth_first_search(derived_graph, fail_on_cyclic=True)
