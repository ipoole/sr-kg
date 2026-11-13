"""Reviewed GR units retain annotation identities and have usable reading-tree content."""
import json
from pathlib import Path
import pytest
from srkg.kb import load_knowledge_base
from srkg.schema import AUTHORING_BLOCK_KINDS
from srkg.content_units import ContentExplanation, ContentReference

ROOT = Path(__file__).resolve().parents[3]
REVIEWED_MODULE_COUNT = 3
BASELINE = json.loads((ROOT/'domains/gr/docs/reading_tree_authoring_baseline.json').read_text())


def walk(parts, path=()):
    for part in parts:
        yield part, path
        if isinstance(part, ContentExplanation):
            yield from walk(part.parts, path+(part.slot,))


@pytest.fixture(scope='module')
def kb():
    return load_knowledge_base(ROOT/'data', include_graphics=False)


def test_reviewed_gr_units_retain_canonical_content_and_clarifications(kb):

    # Read membership from the source tables, independent of viewer ordering.
    import csv
    with (ROOT/'domains/gr/data/modules.csv').open() as f:
        reviewed = [r['module_id'] for r in csv.DictReader(f)][:REVIEWED_MODULE_COUNT]
    owners = {owner for module in reviewed for owner in kb.module(module).members}
    for owner in owners:
        blocks = kb.content_blocks_for(owner)
        assert {'definition', 'explanation'} <= {b.kind for b in blocks}, owner
        assert sum(b.kind == 'graphic' for b in blocks) == 1, owner
        for block in blocks:
            assert block.kind in AUTHORING_BLOCK_KINDS, block.block_id
            assert block.title and block.statement and block.body, block.block_id
            assert not any(isinstance(p, ContentReference) for p, _ in walk(kb.content_units[block.block_id].parts))
    for old in BASELINE['blocks']:
        if old['owner'] not in owners | set(reviewed):
            continue
        parts = kb.content_units[old['block_id']].parts
        paths = {path+(p.slot,) for p, path in walk(parts) if isinstance(p, ContentExplanation)}
        assert {tuple(p) for p in old['local_slots']} <= paths, old['block_id']
