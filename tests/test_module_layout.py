import pandas as pd

from srkg.kb import load_knowledge_base
from srkg.model import Module
from srkg.module_layout import (
    STRUCTURAL_RELATIONS,
    build_generated_module_anchors,
    build_module_local_layout,
    propose_module_concept_numbering,
)


def _module(*members: str, title: str = "SR-2 Test Module") -> Module:
    return Module(
        module_id="sr.test",
        domain="sr",
        title=title,
        sequence=20,
        members=list(members),
    )


def _nodes(*concept_ids: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"id": concept_id, "display_id": f"old.{index}"}
            for index, concept_id in enumerate(concept_ids, start=1)
        ]
    )


def _edges(*rows: tuple[str, str, str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["source", "target", "relation"])


def test_module_layout_places_prerequisites_below_derived_concepts():
    module = _module("derived", "middle", "foundation")
    result = build_module_local_layout(
        _nodes(*module.members),
        _edges(
            ("derived", "middle", "REQUIRES"),
            ("middle", "foundation", "DERIVES_FROM"),
        ),
        [module],
        module_anchors={"sr.test": (300.0, 400.0)},
        x_spacing=100,
        y_spacing=120,
    )

    assert result.ranks == {"foundation": 0, "middle": 1, "derived": 2}
    assert result.positions["derived"][1] < result.positions["middle"][1]
    assert result.positions["middle"][1] < result.positions["foundation"][1]


def test_module_layout_centres_each_module_on_its_anchor():
    module = _module("a", "b", "c", "d", "e")
    result = build_module_local_layout(
        _nodes(*module.members),
        _edges(),
        [module],
        module_anchors={"sr.test": (250.0, -175.0)},
        max_columns=3,
    )

    xs = [result.positions[node_id][0] for node_id in module.members]
    ys = [result.positions[node_id][1] for node_id in module.members]
    assert sum(xs) / len(xs) == 250.0
    assert sum(ys) / len(ys) == -175.0


def test_module_layout_wraps_wide_ranks_to_a_bounded_footprint():
    members = tuple(f"node-{index}" for index in range(7))
    module = _module(*members)
    result = build_module_local_layout(
        _nodes(*members),
        _edges(),
        [module],
        module_anchors={"sr.test": (0.0, 0.0)},
        x_spacing=90,
        max_columns=3,
    )

    xs = [result.positions[node_id][0] for node_id in members]
    assert max(xs) - min(xs) <= 180


def test_module_layout_is_deterministic_and_uses_member_order_for_ties():
    module = _module("second", "first", "third")
    args = (
        _nodes("first", "second", "third"),
        _edges(),
        [module],
    )

    first = build_module_local_layout(*args)
    second = build_module_local_layout(*args)

    assert first == second
    assert first.ordered_members["sr.test"] == ("second", "first", "third")


def test_module_layout_keeps_cycles_together_and_reports_them():
    module = _module("c", "a", "b")
    result = build_module_local_layout(
        _nodes(*module.members),
        _edges(
            ("a", "b", "REQUIRES"),
            ("b", "a", "DERIVES_FROM"),
            ("c", "a", "CONSTRUCTED_FROM"),
        ),
        [module],
    )

    assert result.ranks["a"] == result.ranks["b"]
    assert result.ranks["c"] > result.ranks["a"]
    assert result.cycles == {"sr.test": (("a", "b"),)}


def test_non_structural_and_cross_module_edges_do_not_affect_local_ranks():
    first = _module("a", "b")
    second = Module(
        module_id="sr.other",
        domain="sr",
        title="SR-3 Other",
        sequence=30,
        members=["c"],
    )
    result = build_module_local_layout(
        _nodes("a", "b", "c"),
        _edges(
            ("a", "b", "RELATED"),
            ("a", "c", "REQUIRES"),
        ),
        [first, second],
    )

    assert result.ranks == {"a": 0, "b": 0, "c": 0}


def test_generated_module_anchors_put_prerequisite_modules_below_dependants():
    foundation = _module("foundation", title="SR-1 Foundation")
    derived = Module(
        "sr.derived", "sr", "SR-2 Derived", 20, members=["derived"]
    )

    result = build_generated_module_anchors(
        _nodes("foundation", "derived"),
        _edges(("derived", "foundation", "REQUIRES")),
        [foundation, derived],
        x_spacing=500,
        y_spacing=600,
    )

    assert result.ranks == {"sr.test": 0, "sr.derived": 1}
    assert result.anchors["sr.derived"][1] < result.anchors["sr.test"][1]


def test_generated_module_anchors_default_spacing_reserves_room_for_footprints():
    nodes = pd.DataFrame([{"id": "a"}, {"id": "b"}, {"id": "c"}])
    modules = [
        Module(module_id="m1", title="First", domain="sr", sequence=1, members=("a",)),
        Module(module_id="m2", title="Second", domain="sr", sequence=2, members=("b",)),
        Module(module_id="m3", title="Third", domain="sr", sequence=3, members=("c",)),
    ]
    edges = pd.DataFrame([{"source": "c", "target": "a", "relation": "REQUIRES"}])
    result = build_generated_module_anchors(nodes, edges, modules)
    assert result.anchors["m2"][0] - result.anchors["m1"][0] == 3300
    assert result.anchors["m1"][1] - result.anchors["m3"][1] == 2700


def test_generated_module_anchors_place_independent_modules_side_by_side():
    first = _module("a", title="SR-1 First")
    second = Module("sr.second", "sr", "SR-2 Second", 20, members=["b"])

    result = build_generated_module_anchors(
        _nodes("a", "b"),
        _edges(),
        [first, second],
        x_spacing=500,
        y_spacing=600,
    )

    assert result.ranks == {"sr.test": 0, "sr.second": 0}
    assert result.anchors["sr.test"][1] == result.anchors["sr.second"][1]
    assert result.anchors["sr.test"][0] != result.anchors["sr.second"][0]


def test_numbering_uses_module_code_and_fundamental_to_derived_order():
    module = _module("derived", "independent", "foundation")
    proposals = propose_module_concept_numbering(
        _nodes(*module.members),
        _edges(("derived", "foundation", "REQUIRES")),
        [module],
    )

    assert [proposal.concept_id for proposal in proposals] == [
        "independent",
        "foundation",
        "derived",
    ]
    assert [proposal.new_display_id for proposal in proposals] == [
        "SR-2.1",
        "SR-2.2",
        "SR-2.3",
    ]
    assert [proposal.member_sequence for proposal in proposals] == [10, 20, 30]


def test_numbering_retains_authored_order_when_topology_allows_it():
    module = _module("foundation", "first-result", "later-independent", "capstone")
    proposals = propose_module_concept_numbering(
        _nodes(*module.members),
        _edges(
            ("first-result", "foundation", "REQUIRES"),
            ("capstone", "first-result", "DERIVES_FROM"),
        ),
        [module],
    )

    assert [proposal.concept_id for proposal in proposals] == [
        "foundation",
        "first-result",
        "later-independent",
        "capstone",
    ]


def test_numbering_supports_gr_and_maths_module_codes():
    modules = [
        Module("gr.test", "gr", "GR-4 Matter", 40, members=["gr.a"]),
        Module("math.test", "math", "MATHS-2 Tensors", 20, members=["math.a"]),
    ]
    proposals = propose_module_concept_numbering(
        _nodes("gr.a", "math.a"),
        _edges(),
        modules,
    )

    assert [proposal.new_display_id for proposal in proposals] == [
        "GR-4.1",
        "MATHS-2.1",
    ]


def test_real_data_numbering_is_complete_contiguous_and_topological():
    kb = load_knowledge_base("data")
    proposals = propose_module_concept_numbering(kb.nodes_df, kb.edges_df, kb.modules)
    proposal_by_id = {proposal.concept_id: proposal for proposal in proposals}
    module_by_concept = {
        concept_id: module.module_id
        for module in kb.modules
        for concept_id in module.members
    }

    assert len(proposals) == len(kb.nodes_df) == len(proposal_by_id)
    for module in kb.modules:
        module_proposals = [
            proposal for proposal in proposals if proposal.module_id == module.module_id
        ]
        assert [proposal.member_sequence for proposal in module_proposals] == [
            index * 10 for index in range(1, len(module_proposals) + 1)
        ]
        assert [int(proposal.new_display_id.rsplit(".", 1)[1]) for proposal in module_proposals] == list(
            range(1, len(module_proposals) + 1)
        )

    for edge in kb.edges_df.itertuples(index=False):
        source = str(edge.source)
        target = str(edge.target)
        if (
            str(edge.relation) in STRUCTURAL_RELATIONS
            and module_by_concept[source] == module_by_concept[target]
        ):
            assert proposal_by_id[target].member_sequence < proposal_by_id[source].member_sequence
