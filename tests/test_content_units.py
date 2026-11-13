"""Contracts for shared sources, recursive local content and reading occurrences."""
import json

import pytest

from srkg.content_units import (
    ContentExplanation, ContentReference, ContentText, ContentUnit,
    OccurrencePath, build_content_registry, parse_content,
)
from srkg.model import Concept, ContentBlock, Module, ModuleContentBlock
from srkg.schema import KnowledgeBaseLoadError


def block(id, body='Explanation.', **kwargs):
    return ContentBlock(id, id.rsplit('.', 1)[0], 10, kwargs.pop('kind', 'explanation'),
                        'Short title', body, **kwargs)


def registry(*blocks, domains=('math',)):
    return build_content_registry(
        [Concept('math.alpha', 'Alpha', content_blocks=list(blocks))], [], domains=domains)


def test_old_and_new_blocks_use_one_model_without_invented_statements():
    old = block('math.alpha.old', r'Text \optional_details{Why?}{Because \(x^2\).}')
    new = block('math.alpha.new', statement=r'\(dT_p\) is linear.')
    units = registry(old, new)
    assert isinstance(units['math.alpha.old'], ContentUnit)
    assert units['math.alpha.old'].statement == ''
    assert units['math.alpha.old'].parts[0] == ContentText('Text ')
    assert isinstance(units['math.alpha.old'].parts[1], ContentExplanation)
    assert units['math.alpha.new'].statement == new.statement
    assert old.to_viewer_data() == dict(block_id=old.block_id, concept_id=old.concept_id,
        sequence=10, kind='explanation', title='Short title', body=old.body)
    assert new.to_viewer_data()['statement'] == new.statement


def test_brace_aware_parsing_preserves_maths_and_recurses_in_order():
    parts = parse_content(r'Before \explanation{algebra}{Why \(x\)?}{'
        r'\[\frac{x}{y}\]\explain{chart}{math.chart.definition}{Chart}{Which grid?}} After')
    assert isinstance(parts[0], ContentText)
    local = parts[1]
    assert local.slot == 'algebra'
    assert local.parts[0].text == r'\[\frac{x}{y}\]'
    assert local.parts[1] == ContentReference('chart', 'math.chart.definition', 'Chart', 'Which grid?')
    assert parts[2].text == ' After'
    # Slots need only be unique within their own parent.
    parse_content(r'\explanation{a}{A}{\explanation{x}{X}{One}}'
                  r'\explanation{b}{B}{\explanation{x}{X}{Two}}')


@pytest.mark.parametrize('body', [
    r'\explain{s}{math.a.b}{Label}',
    r'\explanation{s}{Title}{Unclosed',
    r'\explain{}{math.a.b}{Label}{Why?}',
    r'\explain{bad/slot}{math.a.b}{Label}{Why?}',
    r'\explain{s}{no_namespace}{Label}{Why?}',
    r'\explain{s}{math.a.b}{}{Why?}',
    r'\explain{s}{math.a.b}{Label}{}',
    r'\explanation{s}{}{Body}',
    r'\explanation{s}{Title}{}',
    r'\optional_details{}{Body}',
    r'\explanation{s}{Title}{Body}\explain{s}{math.a.b}{Label}{Why?}',
])
def test_bad_macros_and_ambiguous_slots_are_authoring_errors(body):
    with pytest.raises(KnowledgeBaseLoadError):
        parse_content(body)


def test_shared_sources_are_not_inlined_and_cycles_are_path_local():
    a = block('math.alpha.a', r'\explain{b}{math.alpha.b}{B}{Why B?}', statement='A.')
    b = block('math.alpha.b', r'\explain{a}{math.alpha.a}{A}{Why A?}', statement='B.')
    units = registry(a, b)
    ref = units[a.block_id].parts[0]
    assert units.resolve(ref, ancestors=(a.block_id,)).state == 'available'
    cycle = units.resolve(units[b.block_id].parts[0], ancestors=(a.block_id, b.block_id))
    assert cycle.state == 'cycle'
    assert cycle.unit is units[a.block_id]
    # Reaching B on a sibling route is not a cycle.
    assert units.resolve(ref, ancestors=(a.block_id,)).state == 'available'
    payload = units.to_viewer_data()
    assert payload[a.block_id]['parts'][0]['target_id'] == b.block_id
    assert 'parts' not in payload[a.block_id]['parts'][0]
    json.dumps(payload)


def test_references_need_a_declared_statement_not_an_extracted_sentence():
    a = block('math.alpha.a', r'\explain{b}{math.alpha.b}{B}{Why?}')
    with pytest.raises(KnowledgeBaseLoadError, match='statement'):
        registry(a, block('math.alpha.b'))


def test_missing_loaded_target_errors_but_external_namespace_warns():
    body = r'\explanation{local}{Local}{\explain{b}{sr.beta.result}{Result B}{Why B?}}'
    units = registry(block('math.alpha.a', body))
    assert units.warnings[0].domain == 'sr'
    assert units.warnings[0].kind == 'content-reference'
    ref = units['math.alpha.a'].parts[0].parts[0]
    result = units.resolve(ref)
    assert result.state == 'unavailable' and result.unit is None
    assert ref.target_label == 'Result B' and ref.hook == 'Why B?'
    with pytest.raises(KnowledgeBaseLoadError, match='sr.beta.result'):
        registry(block('math.alpha.a', body), domains=('math', 'sr'))


@pytest.mark.parametrize('statement', [
    r'\explain{b}{math.alpha.b}{B}{Why?}',
    r'\optional_details{Why?}{More}',
    r'\explanation{why}{Why?}{More}',
])
def test_statements_cannot_hide_more_disclosures(statement):
    with pytest.raises(KnowledgeBaseLoadError, match='statement'):
        registry(block('math.alpha.a', statement=statement))


def test_concepts_modules_and_graphics_have_the_same_source_contract():
    c = block('math.alpha.graphic', 'How to read this picture.', kind='graphic',
              statement='A local tangent plane.', graphic='detail')
    m = Module('math.module', 'math', 'Module', 1, content_blocks=[
        ModuleContentBlock('math.module.intro', 'math.module', 1, 'overview', 'Intro',
            r'\explain{picture}{math.alpha.graphic}{Tangent plane}{Picture it}')])
    units = build_content_registry([Concept('math.alpha', 'Alpha', content_blocks=[c])],
                                   [m], domains=('math',))
    assert units[c.block_id].graphic == 'detail'
    graphic = units.to_viewer_data()[c.block_id]['graphic']
    assert graphic == {'owner_type': 'concept', 'owner_id': c.concept_id, 'variant': 'detail'}
    assert units['math.module.intro'].owner_type == 'module'
    with pytest.raises(KnowledgeBaseLoadError, match='Duplicate'):
        build_content_registry([Concept('math.alpha', 'Alpha', content_blocks=[c, c])], [], domains=('math',))


@pytest.mark.parametrize('kind,graphic', [('graphic', ''), ('explanation', 'detail'), ('graphic','icon')])
def test_graphic_wrappers_are_explicit_and_only_wrap_the_owners_detail(kind, graphic):
    with pytest.raises(KnowledgeBaseLoadError, match='graphic'):
        registry(block('math.alpha.g', kind=kind, graphic=graphic))


def test_occurrence_identity_is_independent_of_fold_state_and_never_conflates_routes():
    root = OccurrencePath('math.root.argument')
    left = root.child('left', 'math.alpha.a').child('shared', 'math.beta.b')
    right = root.child('right', 'math.alpha.a').child('shared', 'math.beta.b')
    assert left.key != right.key
    assert left == root.child('left', 'math.alpha.a').child('shared', 'math.beta.b')
    assert root.child('left', 'math.alpha.a').key != root.child('left', 'math.other.a').key
    assert root.child('local').key != root.child('local', 'math.alpha.a').key


def test_pathological_local_nesting_has_a_useful_authoring_error():
    body = 'Leaf'
    for _ in range(102):
        body = r'\explanation{child}{More}{' + body + '}'
    with pytest.raises(KnowledgeBaseLoadError, match='nesting exceeds'):
        parse_content(body)


def test_malformed_legacy_disclosure_remains_available_to_editorial_diagnostics():
    body = r'\optional_details{Missing body} and \(unclosed maths'
    unit = registry(block('math.alpha.old', body))['math.alpha.old']
    assert unit.parts == (ContentText(body),)
