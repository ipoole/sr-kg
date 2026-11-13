"""SR-2 content remains self-contained, graph-supported and canonically stable."""
import json
from pathlib import Path

import pytest

from srkg.content_units import ContentExplanation, ContentReference
from srkg.kb import load_knowledge_base
from srkg.schema import AUTHORING_BLOCK_KINDS

ROOT = Path(__file__).resolve().parents[3]
BASELINE = json.loads((ROOT / 'domains/sr/docs/reading_tree_authoring_baseline.json').read_text())
MODULE = 'sr.relativistic_mechanics'
OWNERS = {c['id'] for c in BASELINE['concepts'] if c['module_id'] == MODULE}


def walk(parts, path=()):
    for part in parts:
        yield part, path
        if isinstance(part, ContentExplanation):
            yield from walk(part.parts, path + (part.slot,))


@pytest.fixture(scope='module')
def kb():
    return load_knowledge_base(ROOT / 'data', domains=['sr', 'math'], include_graphics=False)


def test_sr2_has_statement_led_self_contained_blocks(kb):
    for owner in OWNERS:
        blocks = kb.content_blocks_for(owner)
        assert {'definition', 'explanation'} <= {b.kind for b in blocks}
        assert sum(b.kind == 'graphic' for b in blocks) == 1
        for block in blocks:
            assert block.kind in AUTHORING_BLOCK_KINDS, block.block_id
            assert block.title.strip() and block.statement.strip() and block.body.strip(), block.block_id
            assert not any(isinstance(p, ContentReference) for p, _ in walk(kb.content_units[block.block_id].parts))
    assert all(b.statement and b.kind in AUTHORING_BLOCK_KINDS
               for b in kb.module_content_blocks_for(MODULE))
    mass = kb.content_blocks_for('sr.mass_energy_equivalence')
    assert sum(b.kind == 'intuition' for b in mass) >= 2
    assert {b.block_id for b in mass if b.kind == 'derivation'} >= {
        'sr.mass_energy_equivalence.from_momentum', 'sr.mass_energy_equivalence.light_inertia'}


def test_sr2_retains_note_scopes_and_tutorial_targets(kb):
    for old in BASELINE['blocks']:
        if old['owner'] not in OWNERS and old['owner'] != MODULE:
            continue
        unit = kb.content_units[old['block_id']]
        slots = {path + (p.slot,) for p, path in walk(unit.parts)
                 if isinstance(p, ContentExplanation)}
        assert {tuple(p) for p in old['local_slots']} <= slots, old['block_id']


def test_sr2_supports_are_acyclic_and_do_not_assume_rest_energy(kb):
    edges = kb.edges_df
    outgoing = {}
    for e in edges.itertuples():
        if e.relation in {'DERIVES_FROM', 'CONSTRUCTED_FROM', 'REQUIRES'}:
            outgoing.setdefault(e.source, set()).add(e.target)
    def descend(owner, trail):
        assert owner not in trail, f'Circular prerequisite route through {owner}'
        for child in outgoing.get(owner, ()):
            descend(child, trail | {owner})
    for owner in OWNERS:
        descend(owner, set())
    assert outgoing['sr.mass_energy_equivalence'] == {'sr.momentum_four_vector'}
    assert 'sr.mass_energy_equivalence' not in outgoing['sr.momentum_four_vector']
