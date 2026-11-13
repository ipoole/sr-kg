"""A synthetic diamond exercises sharing without converting domain content."""
from unittest.mock import patch

import pandas as pd
import pytest

from srkg.content_units import parse_content

from conftest import (_write_browser_fixture, _prepare_browser_output,
    _open_browser_graph, _use_stub_mathjax)


@pytest.fixture(scope='session')
def shared_explanation_output(tmp_path_factory):
    root = tmp_path_factory.mktemp('shared-explanations')
    _write_browser_fixture(root)
    (root / 'tutorials.yaml').unlink()
    ids = {'1.1': 'test.alpha', '2.1': 'test.beta', '2.2': 'test.gamma', '3.1': 'test.delta'}
    for path in root.glob('*.csv'):
        text = path.read_text()
        for old, new in ids.items():
            text = text.replace(old, new)
        path.write_text(text)
    path = root / 'content_blocks.csv'
    frame = pd.read_csv(path).fillna('')
    frame['statement'] = ''
    frame['graphic'] = ''
    bodies = {
        'test.alpha.definition': r'Root argument. \explain{left}{test.beta.definition}{Beta}{Why beta?}'
            r'\explain{right}{test.gamma.definition}{Gamma}{Why gamma?}'
            r'\explanation{algebra}{Local algebra}{\[x^2+y^2=z^2\]'
            '\\explanation{step}{One more step}{First paragraph.\nSecond paragraph.}}'
            r'\explain{absent}{other.absent.result}{An external result}{What is missing?}'
            r'\explain{module}{test.m01_foundations.overview}{Module overview}{Why this module?}',
        'test.beta.definition': r'Left explanation. \explain{shared}{test.delta.definition}{Delta}{Why delta?}',
        'test.gamma.definition': r'Right explanation. \explain{shared}{test.delta.definition}{Delta}{Why delta?}'
            r'\explain{picture}{test.gamma.picture}{Picture}{Show a picture}',
        'test.delta.definition': r'Shared reasoning: \(dT_p(v)=v[T]\). \explanation{deeper}{Why exactly?}{Deep shared reason.}'
            r'\explain{cycle}{test.alpha.definition}{Root}{Back to the argument}',
    }
    for id, body in bodies.items():
        frame.loc[frame.block_id == id, 'body'] = body
        frame.loc[frame.block_id == id, 'statement'] = r'\(v[f]\) is a local rate.' if id.endswith('delta.definition') else 'A concise result.'
    extra = dict(block_id='test.gamma.picture', concept_id='test.gamma', sequence=99,
        kind='graphic', title='Local picture', body='A guide to this picture.',
        statement='A tangent direction.', graphic='detail')
    frame = pd.concat([frame, pd.DataFrame([extra])], ignore_index=True)
    frame.to_csv(path, index=False)
    path = root / 'module_content_blocks.csv'
    frame = pd.read_csv(path)
    frame['statement'] = 'A module result.'
    frame.loc[frame.block_id == 'test.m01_foundations.overview', 'body'] = (
        r'Module argument. \explain{delta}{test.delta.definition}{Delta}{Use a concept result}')
    frame.to_csv(path, index=False)
    def graphic(id, variant='icon'):
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-labelledby="picture-title"><title id="picture-title">Picture</title><defs><linearGradient id="paint"><stop stop-color="blue"/></linearGradient></defs><circle cx="50" cy="50" r="30" fill="url(#paint)"/></svg>' if id=='test.gamma' else None
    with patch('srkg.graphic_enrichment.createSvgGraphic', side_effect=graphic):
        output = _prepare_browser_output(root, root, 'Shared explanation fixture')
    return output


@pytest.fixture
def shared_explanation_graph(shared_explanation_output, playwright_browser):
    api, browser = playwright_browser
    output = shared_explanation_output.with_name('shared-fast.html')
    output.write_text(_use_stub_mathjax(shared_explanation_output.read_text()))
    with _open_browser_graph(api, browser, output) as graph:
        graph.click_concept('test.alpha')
        # These tests exercise legacy sharing inside an explicitly opened block.
        graph.page.locator('#info_panel > details[data-content-block-id="test.alpha.definition"]').evaluate('e=>e.open=true')
        yield graph


def _reference(page, slot):
    return page.locator(f'#info_panel details.kg-shared-explanation[data-content-slot="{slot}"]')


def _open(disclosure):
    disclosure.evaluate("""element => {
        let parent=element.parentElement;
        while(parent){ if(parent.tagName==='DETAILS')parent.open=true; parent=parent.parentElement; }
    }""")
    disclosure.locator(':scope > summary').click()


@pytest.mark.browser
def test_native_reading_and_independent_lazy_branches(shared_explanation_graph):
    graph = shared_explanation_graph
    page = graph.page
    root = page.locator('[data-content-block-id="test.alpha.definition"]')
    assert root.evaluate('e=>e.open')
    assert 'Root argument.' in root.inner_text()
    assert root.locator(':scope > summary > .kg-content-statement').count()==1
    left, right = _reference(page, 'left'), _reference(page, 'right')
    assert left.count()==right.count()==1
    assert not left.evaluate('e=>e.open')
    assert page.locator('[data-content-slot="shared"]').count()==0  # Not eagerly expanded.
    _open(left)
    first = left.locator('details.kg-shared-explanation[data-content-slot="shared"]')
    _open(first)
    deeper = first.locator('details[data-content-slot="deeper"]')
    _open(deeper)
    _open(right)
    second = right.locator('details.kg-shared-explanation[data-content-slot="shared"]')
    assert not second.evaluate('e=>e.open')
    _open(second)
    assert not second.locator('details[data-content-slot="deeper"]').evaluate('e=>e.open')
    assert deeper.evaluate('e=>e.open')
    assert first.get_attribute('id') != second.get_attribute('id')
    _open(left); _open(left)
    assert deeper.evaluate('e=>e.open')
    assert first.locator(':scope > summary .kg-note-block-action').count()==1
    assert not graph.page_errors


@pytest.mark.browser
def test_cycles_unavailable_targets_and_graph_axes_are_quiet(shared_explanation_graph):
    page = shared_explanation_graph.page
    before = page.evaluate('({state:kgViewerStateSnapshot(),pos:network.getViewPosition(),scale:network.getScale(),hash:location.hash})')
    _open(_reference(page, 'left'))
    _open(_reference(page, 'shared'))
    link = page.locator('.kg-content-return')
    link.wait_for()
    assert link.count()==1
    link.click()
    assert page.locator('#info_panel details[open]').count()<12
    assert page.locator('.kg-shared-unavailable').count()==1
    assert 'An external result' in page.locator('.kg-shared-unavailable').inner_text()
    after = page.evaluate('({state:kgViewerStateSnapshot(),pos:network.getViewPosition(),scale:network.getScale(),hash:location.hash})')
    assert after == before


@pytest.mark.browser
def test_native_source_and_graphic_have_no_extra_disclosure(shared_explanation_graph):
    graph=shared_explanation_graph
    graph.click_concept('test.gamma')
    page=graph.page
    native=page.locator('[data-content-block-id="test.gamma.definition"]')
    native.evaluate('e=>e.open=true')
    assert 'Right explanation.' in native.inner_text()
    picture=page.locator('[data-content-block-id="test.gamma.picture"]')
    if not picture.evaluate('e=>e.open'): _open(picture)
    assert picture.locator('svg').count()==1
    assert page.locator('#info_panel .concept-graphic').count()==1  # No duplicate hero.
    _open(_reference(page,'picture'))
    _reference(page,'picture').locator('svg').wait_for()
    assert _reference(page,'picture').locator('svg').count()==1
    assert page.locator('#info_panel [id]').evaluate_all('els=>new Set(els.map(e=>e.id)).size===els.length')
    assert page.locator('#info_panel .concept-graphic svg').evaluate_all('''svgs=>svgs.every(svg=>{
      const title=svg.getAttribute('aria-labelledby');
      const paint=svg.querySelector('circle').getAttribute('fill').slice(5,-1);
      return svg.querySelector('[id="'+title+'"]') && svg.querySelector('[id="'+paint+'"]');
    })''')


@pytest.mark.browser
def test_read_marks_notes_and_open_paths_survive_same_page_refresh(shared_explanation_graph):
    graph=shared_explanation_graph
    page=graph.page
    _open(_reference(page,'left'))
    _open(_reference(page,'shared'))
    deeper=_reference(page,'shared').locator('details[data-content-slot="deeper"]')
    _open(deeper)
    root=page.locator('[data-content-block-id="test.alpha.definition"]')
    root.locator(':scope > summary .content-block-read-toggle, :scope > .kg-content-body > .kg-content-footer .content-block-read-toggle').check()
    root.locator(':scope > summary .kg-note-block-action').click()
    root.locator(':scope > .content-block-body > .concept-line').first.click()
    page.locator('.user-note-body-input').fill('A note on this argument.')
    page.locator('.user-note-close').click()
    assert deeper.evaluate('e=>e.open')
    assert root.locator(':scope > summary .content-block-read-toggle, :scope > .kg-content-body > .kg-content-footer .content-block-read-toggle').is_checked()
    assert page.locator('#info_panel .kg-unmatched-notes').count()==0
    assert page.locator('#info_panel .user-note').count()==1
    graph.click_concept('test.beta'); graph.click_concept('test.alpha')
    assert not _reference(page,'left').evaluate('e=>e.open')  # New page visit.
    assert root.locator(':scope > summary .content-block-read-toggle, :scope > .kg-content-body > .kg-content-footer .content-block-read-toggle').is_checked()


@pytest.mark.browser
@pytest.mark.parametrize('width',[390,1280])
def test_keyboard_and_phone_layout(shared_explanation_graph,width):
    page=shared_explanation_graph.page
    page.set_viewport_size({'width':width,'height':844})
    page.locator('#kg_view_select').select_option('details')
    left=_reference(page,'left')
    left.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    assert left.evaluate('e=>e.open')
    assert left.locator(':scope > summary').evaluate('e=>e===document.activeElement')
    _open(_reference(page,'shared'))
    _open(_reference(page,'shared').locator('details[data-content-slot="deeper"]'))
    assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
    assert not shared_explanation_graph.page_errors


@pytest.mark.browser
def test_browser_and_loader_agree_on_the_recursive_source_model(shared_explanation_graph):
    texts = [
        r'Before \optional_details{Why?}{With \(x^{2}\) and \optional_details{Deeper}{A reason.}} After',
        r'\explanation{algebra}{Why \(x\)?}{\[\frac{x}{y}\]\explain{chart}{test.chart.result}{A chart}{Which one?}}',
        r'\explain{left}{test.a.result}{A}{Why A?}\explain{right}{test.b.result}{B}{Why B?}',
    ]
    expected = [[part.to_viewer_data() for part in parse_content(text)] for text in texts]
    actual = shared_explanation_graph.page.evaluate('''texts => {
      const markup=kgCreateContentMarkup({concept:()=>null, hash:id=>id});
      return texts.map(text=>markup.parseContent(text));
    }''', texts)
    assert actual == expected


@pytest.mark.browser
def test_local_explanations_use_the_same_paragraph_layout(shared_explanation_graph):
    page = shared_explanation_graph.page
    _open(page.locator('[data-content-slot="algebra"]'))
    child = page.locator('[data-content-slot="step"]')
    _open(child)
    assert child.locator(':scope > .optional-detail-body .concept-line').count() == 2


@pytest.mark.browser
def test_modules_can_borrow_and_supply_explanations(shared_explanation_graph):
    graph = shared_explanation_graph
    page = graph.page
    _open(_reference(page, 'module'))
    _reference(page, 'module').locator('[data-content-slot="delta"]').wait_for()
    graph.open_control_section('kg_modules_section')
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    native = page.locator('[data-content-block-id="test.m01_foundations.overview"]')
    native.evaluate('e=>e.open=true')
    assert 'Module argument.' in native.inner_text()
    _open(_reference(page, 'delta'))
    _reference(page, 'delta').locator('[data-content-slot="deeper"]').wait_for()
    assert not graph.page_errors


@pytest.mark.browser
def test_existing_graphic_notes_stay_with_the_explicit_native_graphic(shared_explanation_graph):
    graph = shared_explanation_graph
    page = graph.page
    page.evaluate('''() => kgPersonalData.replaceNotes([{
      id:'legacy-graphic-note', targetType:'concept', targetId:'test.gamma',
      conceptId:'test.gamma', placement:'anchor', section:'Graphic',
      anchor:{blockId:'',sectionKey:'graphic',blockIndex:0,contextBefore:'',contextAfter:''},
      title:'My picture note',body:'A saved observation.',
      createdAt:'2026-11-08T12:00:00Z',updatedAt:'2026-11-08T12:00:00Z'
    }])''')
    page.reload(wait_until='load')
    graph.click_concept('test.gamma')
    picture = page.locator('[data-content-block-id="test.gamma.picture"]')
    assert picture.locator('details.user-note[data-note-id="legacy-graphic-note"]').count() == 1
    assert picture.locator(':scope > summary .kg-note-block-action').get_attribute('data-note-state') == 'present'
    assert page.locator('#info_panel .kg-unmatched-notes').count() == 0


@pytest.mark.browser
@pytest.mark.browser_full
def test_lazy_explanations_typeset_real_maths(shared_explanation_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, shared_explanation_output,
                             {'viewport': {'width': 390, 'height': 844}}) as graph:
        graph.click_concept('test.alpha')
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise === "function"')
        _open(_reference(page, 'left'))
        _open(_reference(page, 'shared'))
        shared = _reference(page, 'shared')
        shared.locator(':scope > .kg-shared-body mjx-container').first.wait_for()
        _open(page.locator('[data-content-slot="algebra"]'))
        page.locator('[data-content-slot="algebra"] mjx-container[display="true"]').wait_for()
        assert page.locator('mjx-merror,[data-mjx-error]').count() == 0
        assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
        assert not graph.page_errors


@pytest.mark.browser
def test_borrowed_read_marks_share_source_identity_and_preserve_reading(shared_explanation_graph):
    page = shared_explanation_graph.page
    _open(_reference(page, 'left'))
    _open(_reference(page, 'right'))
    copies = page.locator('.content-block-read-toggle[data-read-block-id="test.delta.definition"]')
    copies.nth(1).wait_for()
    assert copies.count() == 2
    before = page.evaluate('({state:kgViewerStateSnapshot(),hash:location.hash})')
    assert copies.first.is_disabled()
    _open(_reference(page, 'shared').first)
    opened = _reference(page, 'shared').first
    tick = opened.locator(':scope > .kg-content-body > .kg-content-footer .content-block-read-toggle')
    tick.check()
    assert copies.evaluate_all('es=>es.every(e=>e.checked)')
    assert page.evaluate('kgContentReadProgress.isRead("test.delta.definition")')
    assert not page.evaluate('kgContentReadProgress.isRead("test.alpha.definition")')
    assert opened.evaluate('e=>e.open')
    assert not _reference(page, 'shared').nth(1).evaluate('e=>e.open')
    page.evaluate('kgContentReadProgress.setRead("test.delta.definition", false)')
    assert not tick.is_checked()
    tick.focus()
    page.keyboard.press('Space')
    assert tick.is_checked()
    assert page.evaluate('({state:kgViewerStateSnapshot(),hash:location.hash})') == before
    graph = shared_explanation_graph
    graph.click_concept('test.delta')
    native = page.locator('[data-content-block-id="test.delta.definition"] > summary .content-block-read-toggle')
    assert native.is_checked()
    native.uncheck()
    graph.click_concept('test.alpha')
    _open(_reference(page, 'left'))
    assert not page.locator('.content-block-read-toggle[data-read-block-id="test.delta.definition"]').is_checked()


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_notes_in_shared_sources_and_named_local_clarifications(shared_explanation_graph, width):
    graph=shared_explanation_graph; page=graph.page
    page.set_viewport_size({'width':width,'height':900})
    page.locator('#kg_view_select').select_option('details')
    if page.locator('#kg_controls').is_visible():
        page.locator('#kg_controls_toggle').click()
    _open(_reference(page,'left')); _open(_reference(page,'right'))
    copies=_reference(page,'shared'); copies.nth(1).wait_for()
    _open(copies.first); _open(copies.nth(1))
    first,second=copies.first,copies.nth(1)
    first.locator(':scope > summary .kg-note-block-action').click()
    first.locator(':scope > .kg-shared-body > .concept-line').first.click()
    page.locator('.user-note-title-input').fill('Shared observation')
    page.locator('.user-note-body-input').fill(r'A remembered fact: \(x^2\).')
    page.locator('.user-note-close').click()
    assert first.locator('.user-note').count()==second.locator('.user-note').count()==1
    assert 'remembered fact' in second.locator('.user-note').inner_text()
    assert page.evaluate('kgPersonalData.getSnapshot().notes[0].targetId')=='test.delta'
    assert page.evaluate('kgPersonalData.getSnapshot().notes[0].anchor.blockId')=='test.delta.definition'
    second.locator('.user-note-edit').click()
    assert page.locator('.user-note-body-input').count()==1
    assert second.locator('.user-note-body-input').count()==1
    page.locator('.user-note-body-input').fill('Edited from the other branch.')
    assert 'Edited from the other branch' in first.locator('.user-note').inner_text()
    page.locator('.user-note-close').click()
    assert first.evaluate('e=>e.open') and second.evaluate('e=>e.open')
    local=second.locator('[data-content-slot="deeper"]')
    local.locator(':scope > summary .kg-note-block-action').click()
    local.locator(':scope > .optional-detail-body > .concept-line').first.click()
    page.locator('.user-note-title-input').fill('Local observation')
    page.locator('.user-note-body-input').fill('This belongs to the named clarification.')
    page.locator('.user-note-close').click()
    assert page.locator('#info_panel .kg-unmatched-notes').count()==0
    snapshot=page.evaluate('kgPersonalData.getSnapshot()')
    assert len(snapshot['notes'])==2
    assert snapshot['notes'][1]['anchor']['sectionKey'].startswith('explanation:')
    # Archive round trip must preserve local scope without a new storage field.
    page.evaluate('''() => {
      const before=kgPersonalData.getSnapshot();
      const restored=kgPersonalDataArchive.importBytes(kgPersonalDataArchive.exportBytes(before));
      window.restoredAnchors=restored.notes.map(n=>n.anchor);
    }''')
    assert page.evaluate('restoredAnchors')==[n['anchor'] for n in snapshot['notes']]
    graph.click_concept('test.delta')
    native=page.locator('[data-content-block-id="test.delta.definition"]')
    assert native.locator('.user-note').count()==2
    assert page.locator('#info_panel .kg-unmatched-notes').count()==0
    page.reload(wait_until='load'); graph.click_concept('test.delta')
    assert native.locator('.user-note').count()==2
    assert not graph.page_errors
