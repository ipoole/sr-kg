"""Stable authored field units and acyclic teaching supports across SR-3–5."""
import json
from pathlib import Path
import pytest
from srkg.kb import load_knowledge_base
from srkg.schema import AUTHORING_BLOCK_KINDS
from srkg.content_units import ContentReference,ContentExplanation
ROOT=Path(__file__).resolve().parents[3]
BASELINE=json.loads((ROOT/'domains/sr/docs/reading_tree_authoring_baseline.json').read_text())
MODULES=['sr.variational_and_field_theory','sr.electromagnetic_structure_gauge_and_stress_energy','sr.field_dynamics_conservation_and_radiation']
@pytest.fixture(scope='module')
def kb():return load_knowledge_base(ROOT/'data',domains=['sr','math'],include_graphics=False)
def walk(parts,path=()):
 for part in parts:
  yield part,path
  if isinstance(part,ContentExplanation):yield from walk(part.parts,path+(part.slot,))
@pytest.mark.parametrize('module',MODULES)
def test_field_units_are_self_contained_and_canonically_stable(kb,module):
 owners=set(kb.module(module).members)
 for owner in owners:
  blocks=kb.content_blocks_for(owner)
  assert {'definition','explanation'}<={b.kind for b in blocks},owner
  assert sum(b.kind=='graphic' for b in blocks)==1
  for b in blocks:
   assert b.kind in AUTHORING_BLOCK_KINDS and b.statement and b.title and b.body,b.block_id
   assert not any(isinstance(p,ContentReference) for p,_ in walk(kb.content_units[b.block_id].parts))
 for old in BASELINE['blocks']:
  if old['owner'] not in owners and old['owner']!=module:continue
  unit=kb.content_units[old['block_id']]
  paths={path+(p.slot,) for p,path in walk(unit.parts) if isinstance(p,ContentExplanation)}
  assert {tuple(p) for p in old['local_slots']}<=paths,old['block_id']
 assert all(b.statement and b.kind in AUTHORING_BLOCK_KINDS for b in kb.module_content_blocks_for(module))
@pytest.mark.parametrize('module',MODULES)
def test_field_foundation_routes_remain_acyclic(kb,module):
 outgoing={}
 for e in kb.edges_df.itertuples():
  if e.relation in {'DERIVES_FROM','CONSTRUCTED_FROM','REQUIRES'}:outgoing.setdefault(e.source,[]).append(e.target)
 def visit(owner,path):
  assert owner not in path,f'Cyclic support: {path} -> {owner}'
  for child in outgoing.get(owner,[]):visit(child,path|{owner})
 for owner in kb.module(module).members:visit(owner,set())
