from srkg.model import Module
from srkg.module_colours import build_module_visuals_by_concept


def test_module_colours_are_shared_within_modules_and_vary_between_modules():
    visuals = build_module_visuals_by_concept(
        [
            Module("sr.one", "sr", "SR-1 One", 10, members=["a", "b"]),
            Module("sr.two", "sr", "SR-2 Two", 20, members=["c"]),
        ]
    )

    assert visuals["a"] == visuals["b"]
    assert visuals["a"]["module_id"] == "sr.one"
    assert visuals["c"]["module_id"] == "sr.two"
    assert visuals["a"]["background"] != visuals["c"]["background"]
