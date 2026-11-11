"""Editorial structure and canonical identities for Maths reading-tree content."""
from pathlib import Path

import pytest

from srkg.content_units import ContentExplanation, ContentReference
from srkg.kb import load_knowledge_base

ROOT = Path(__file__).resolve().parents[3]
@pytest.fixture(scope='module')
def maths():
    return load_knowledge_base(ROOT / 'data', domains=['math'], include_graphics=False)


def walk(parts):
    for part in parts:
        yield part
        if isinstance(part, ContentExplanation):
            yield from walk(part.parts)


def test_migrated_blocks_have_three_levels_and_no_owned_block_calls(maths):
    for concept in maths.concepts:
        blocks = maths.content_blocks_for(concept.id)
        assert {'definition', 'derivation', 'explanation'} <= {b.kind for b in blocks}
        for block in blocks:
            assert block.title and block.body and block.statement, block.block_id
            assert len(block.statement.split()) <= 30, block.block_id
            assert not any(isinstance(p, ContentReference)
                           for p in walk(maths.content_units[block.block_id].parts))
        definition = next(b for b in blocks if b.kind == 'definition')
        assert definition.block_id == concept.id + '.definition'
        graphics = [b for b in blocks if b.kind == 'graphic']
        assert len(graphics) == 1 and graphics[0].graphic == 'detail'
    for module in maths.modules:
        for block in maths.module_content_blocks_for(module.module_id):
            assert block.statement and len(block.statement.split()) <= 30
            assert not any(isinstance(p, ContentReference)
                           for p in walk(maths.content_units[block.block_id].parts))


def test_temperature_argument_retains_named_clarification_and_source_identity(maths):
    root = maths.content_units['math.cotangent_space.gradient_example']
    linearity = next(p for p in root.parts
                     if isinstance(p, ContentExplanation) and p.slot == 'linearity')
    assert any(isinstance(p, ContentExplanation) and p.slot == 'first-order'
               for p in linearity.parts)
    for source, slot in [('math.cotangent_space.basis', 'algebra'),
                         ('math.cotangent_space.terrain_survey', 'centimetres'),
                         ('math.tangent_space.curves', 'equivalence')]:
        assert any(isinstance(p, ContentExplanation) and p.slot == slot
                   for p in maths.content_units[source].parts)
    assert maths.content_units['math.tangent_space.graphic'].graphic == 'detail'
    assert maths.missing_domains == ('sr',)


def test_foundational_routes_are_explicit_and_acyclic(maths):
    edges = maths.edges_df
    foundation = edges[edges.relation.isin(['DERIVES_FROM', 'CONSTRUCTED_FROM', 'REQUIRES'])]
    assert all(str(note).strip() for note in foundation.note)
    supports = set(zip(foundation.source, foundation.target))
    assert ('math.cotangent_space', 'math.tangent_space') in supports
    assert ('math.tangent_space', 'math.coordinate_transformation') in supports
    assert ('math.coordinate_transformation', 'math.coordinate_chart') in supports
    assert ('math.coordinate_chart', 'math.manifold') in supports
    complete, active = set(), set()
    def visit(id):
        assert id not in active, f'Circular foundational route: {id}'
        if id in complete:
            return
        active.add(id)
        for source, target in supports:
            if source == id:
                visit(target)
        active.remove(id)
        complete.add(id)
    for concept in maths.concepts:
        visit(concept.id)
