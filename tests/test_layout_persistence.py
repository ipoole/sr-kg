from srkg.layout_persistence import PublishedLayout, resolve_published_layout
from srkg.model import LayoutPosition, Module


def test_resolve_published_layout_fills_concepts_and_module_anchors():
    published = PublishedLayout(
        schema_version=1,
        revision="r3",
        concepts={"test.alpha": LayoutPosition(10, 20)},
        modules={},
    )

    resolved = resolve_published_layout(
        published,
        generated_concept_positions={
            "test.alpha": (100, 200),
            "test.beta": (30, 50),
        },
        generated_module_positions={"test.module": (70, 80)},
        modules=(Module(
            module_id="test.module",
            domain="test",
            title="Test",
            sequence=1,
            members=["test.alpha", "test.beta"],
        ),),
    )

    assert resolved.to_viewer_data() == {
        "schema_version": 1,
        "revision": "r3",
        "concepts": {
            "test.alpha": {"x": 10.0, "y": 20.0},
            "test.beta": {"x": 30.0, "y": 50.0},
        },
        "modules": {
            "test.module": {"anchor": {"x": 70.0, "y": 80.0}},
        },
    }


def test_resolve_published_layout_preserves_authored_module_anchor():
    published = PublishedLayout(
        schema_version=1,
        revision="r3",
        concepts={},
        modules={"test.module": LayoutPosition(400, 500)},
    )

    resolved = resolve_published_layout(
        published,
        generated_concept_positions={"test.alpha": (10, 20)},
        generated_module_positions={"test.module": (70, 80)},
        modules=(Module(
            module_id="test.module",
            domain="test",
            title="Test",
            sequence=1,
            members=["test.alpha"],
        ),),
    )

    assert resolved.modules["test.module"] == LayoutPosition(400, 500)
