"""SR-1's authored units and physical-postulate reading routes."""
import json
from pathlib import Path

import pytest

from srkg.content_units import ContentExplanation, ContentReference
from srkg.kb import load_knowledge_base

ROOT = Path(__file__).resolve().parents[3]
BASELINE = json.loads((ROOT / 'domains/sr/docs/reading_tree_authoring_baseline.json').read_text())
MODULE = 'sr.spacetime_foundations'
OWNERS = {c['id'] for c in BASELINE['concepts'] if c['module_id'] == MODULE}


@pytest.fixture(scope='module')
def sr_math():
    return load_knowledge_base(ROOT / 'data', domains=['sr', 'math'], include_graphics=False)


def walk(parts, path=()):
    for part in parts:
        yield part, path
        if isinstance(part, ContentExplanation):
            yield from walk(part.parts, path + (part.slot,))


def test_sr1_units_have_authored_three_level_content(sr_math):
    from srkg.schema import AUTHORING_BLOCK_KINDS
    for owner in OWNERS:
        blocks = sr_math.content_blocks_for(owner)
        assert {'definition', 'explanation'} <= {b.kind for b in blocks}
        assert next(b for b in blocks if b.kind == 'definition').block_id == owner + '.definition'
        for block in blocks:
            assert block.kind in AUTHORING_BLOCK_KINDS
            assert block.title.strip() and block.statement.strip() and block.body.strip(), block.block_id
            assert not any(isinstance(part, ContentReference)
                           for part, _ in walk(sr_math.content_units[block.block_id].parts))
    assert all(b.statement for b in sr_math.module_content_blocks_for(MODULE))
    assert all(b.kind in AUTHORING_BLOCK_KINDS for b in sr_math.module_content_blocks_for(MODULE))


def test_sr1_preserves_existing_ids_and_local_note_scopes(sr_math):
    for old in BASELINE['blocks']:
        if old['owner'] not in OWNERS and old['owner'] != MODULE:
            continue
        unit = sr_math.content_units[old['block_id']]
        slots = {path + (part.slot,) for part, path in walk(unit.parts)
                 if isinstance(part, ContentExplanation)}
        assert {tuple(path) for path in old['local_slots']} <= slots, old['block_id']


def test_sr1_formal_routes_reach_postulates_without_interval_circularity(sr_math):
    edges = sr_math.edges_df
    triples = set(zip(edges.source, edges.target, edges.relation))
    assert ('sr.metric_tensor', 'sr.lorentz_transformations', 'DERIVES_FROM') in triples
    assert ('sr.spacetime_interval', 'sr.metric_tensor', 'DERIVES_FROM') in triples
    for postulate in ('principle_of_relativity', 'constancy_of_speed_of_light'):
        assert ('sr.lorentz_transformations', 'sr.' + postulate, 'DERIVES_FROM') in triples
    assert ('sr.lorentz_transformations', 'sr.spacetime_interval', 'DERIVES_FROM') not in triples
    assert ('sr.minkowski_diagram', 'sr.lorentz_transformations', 'DERIVES_FROM') in triples

    outgoing = {}
    for edge in edges.itertuples():
        if edge.relation in {'DERIVES_FROM', 'CONSTRUCTED_FROM', 'REQUIRES'}:
            outgoing.setdefault(edge.source, []).append(edge.target)
    def visit(id, ancestors):
        assert id not in ancestors, f'Circular reading route through {id}'
        for target in outgoing.get(id, []):
            visit(target, ancestors | {id})
    for owner in OWNERS:
        visit(owner, set())
