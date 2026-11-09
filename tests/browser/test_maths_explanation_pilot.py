"""Read the real Maths-only argument, without importing the other domains."""
import pytest

from conftest import REPO_ROOT, _prepare_browser_output, _open_browser_graph


@pytest.fixture(scope='session')
def maths_pilot_output(tmp_path_factory):
    root = tmp_path_factory.mktemp('maths-pilot')
    return _prepare_browser_output(root, REPO_ROOT / 'data', 'Maths explanation pilot', domains=['math'])


def _block(page, id):
    return page.locator(f'#info_panel [data-content-block-id="{id}"]')


def _use(container, slot):
    return container.locator(f'details.kg-shared-explanation[data-content-slot="{slot}"]')


def _open(element):
    element.locator(':scope > summary').click()


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_real_maths_argument_supports_both_reading_paths(maths_pilot_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, maths_pilot_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.evaluate('''() => {
          const now='2026-11-08T12:00:00Z';
          const note=(id,targetId,section,anchor)=>({id,targetType:'concept',targetId,
            conceptId:targetId,placement:'anchor',section,anchor,title:'Saved note',
            body:'A personal observation.',createdAt:now,updatedAt:now});
          kgPersonalData.replaceNotes([
            note('old-calculation-note','math.cotangent_space','The same temperature change on two grids',
              {blockId:'math.cotangent_space.units_example',sectionKey:'',blockIndex:0}),
            note('old-tangent-picture-note','math.tangent_space','Graphic',
              {blockId:'',sectionKey:'graphic',blockIndex:0})
          ]);
          kgContentReadProgress.setRead('math.tangent_space.definition',true);
        }''')
        page.reload(wait_until='load')
        graph.click_concept('math.cotangent_space')
        page.locator('#kg_view_select').select_option('details')
        assert len(page.evaluate('Object.keys(conceptData)')) == 9
        assert _block(page, 'math.cotangent_space.units_example').locator(
            'details.user-note[data-note-id="old-calculation-note"]').count() == 1
        assert page.locator('#info_panel .kg-unmatched-notes').count() == 0
        assert page.evaluate('Object.keys(conceptData).every(id=>id.startsWith("math."))')
        page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise === "function"')
        argument = _block(page, 'math.cotangent_space.gradient_example')
        board = _block(page, 'math.cotangent_space.basis')
        rate = _block(page, 'math.cotangent_space.terrain_survey')
        for block in (argument, board, rate):
            assert block.evaluate('e=>e.open')
            block.locator(':scope > .content-block-body mjx-container').first.wait_for()
        before = page.evaluate('kgPersonalData.getSnapshot()')
        axes = page.evaluate('({state:kgViewerStateSnapshot(),hash:location.hash})')
        tangent = _use(argument, 'tangent')
        assert not tangent.evaluate('e=>e.open')
        assert tangent.locator('.kg-shared-body .kg-shared-explanation').count() == 0
        _open(tangent)
        chart1 = _use(tangent, 'chart')
        _open(chart1)
        deeper1 = chart1.locator('details[data-content-slot="overlap"]')
        _open(deeper1)
        _open(tangent)
        chart2 = _use(board, 'chart')
        _open(chart2)
        deeper2 = chart2.locator('details[data-content-slot="overlap"]')
        assert not deeper2.evaluate('e=>e.open')
        assert deeper1.evaluate('e=>e.open')
        _open(tangent)
        assert deeper1.evaluate('e=>e.open')
        picture1, picture2 = _use(tangent, 'picture'), _use(rate, 'picture')
        _open(picture1); _open(picture2)
        for picture in (picture1, picture2):
            picture.locator('.concept-graphic > svg').wait_for()
            picture.locator('.concept-graphic-caption mjx-container').first.wait_for()
            assert picture.locator(':scope > summary .kg-note-block-action').count() == 1
        linearity = argument.locator('details[data-content-slot="linearity"]')
        _open(linearity)
        _open(linearity.locator('details[data-content-slot="first-order"]'))
        _open(board.locator('details[data-content-slot="algebra"]'))
        _open(rate.locator('details[data-content-slot="centimetres"]'))
        page.wait_for_function('''needles => {
          const panel=document.getElementById('info_panel');
          return needles.every(needle=>!panel.innerText.includes(needle));
        }''', arg=[r'\(', r'\['])
        assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0
        assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
        assert page.locator('#info_panel [id]').evaluate_all('els=>new Set(els.map(e=>e.id)).size===els.length')
        assert page.evaluate('kgPersonalData.getSnapshot()') == before
        assert page.evaluate('({state:kgViewerStateSnapshot(),hash:location.hash})') == axes
        assert not graph.page_errors
        graph.click_concept('math.tangent_space')
        graphic = _block(page, 'math.tangent_space.graphic')
        assert graphic.evaluate('e=>e.open')
        graphic.locator('.concept-graphic-caption mjx-container').first.wait_for()
        assert page.locator('#info_panel .concept-graphic').count() == 1
        assert graphic.locator('details.user-note[data-note-id="old-tangent-picture-note"]').count() == 1
        assert _block(page, 'math.tangent_space.definition').locator(
            ':scope > summary .content-block-read-toggle').is_checked()
        source = _block(page, 'math.tangent_space.directional_derivative')
        assert source.locator(':scope > .content-block-body > .kg-content-statement').count() == 1
        assert source.locator(':scope > .content-block-body > .concept-line').count() > 0


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_maths1_shared_reading_controls_and_complete_routes(maths_pilot_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, maths_pilot_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        for concept in ('manifold', 'coordinate_chart', 'coordinate_transformation',
                        'worldline', 'tangent_space', 'cotangent_space'):
            graph.click_concept('math.' + concept)
            # Deliberately traverse every route in this small authored DAG.
            # Hydration is lazy, so reveal new children a layer at a time.
            for _ in range(12):
                closed = page.locator('#info_panel details.kg-content-framed:not([open])')
                if not closed.count():
                    break
                closed.evaluate_all('els=>els.forEach(e=>e.open=true)')
                page.wait_for_timeout(40)
            else:
                pytest.fail('Explanation routes did not terminate')
            page.wait_for_function('''needle => !document.getElementById('info_panel').innerText.includes(needle)''', arg=r'\[')
            assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            statements = page.locator('#info_panel .kg-content-statement')
            assert statements.count() > 0
            assert statements.first.evaluate('e=>getComputedStyle(e).color') == 'rgb(20, 88, 176)'
        graph.click_concept('math.tangent_space')
        graph.click_concept('math.cotangent_space')
        tangent = _use(_block(page, 'math.cotangent_space.gradient_example'), 'tangent')
        toggle = tangent.locator(':scope > summary .content-block-read-toggle')
        assert not tangent.evaluate('e=>e.open')
        toggle.check()
        assert not tangent.evaluate('e=>e.open')
        assert page.evaluate('kgContentReadProgress.isRead("math.tangent_space.directional_derivative")')
        # Saved progress survives reload, and appears on the native page.
        page.reload(wait_until='load')
        graph.click_concept('math.tangent_space')
        native = _block(page, 'math.tangent_space.directional_derivative').locator(
            ':scope > summary .content-block-read-toggle')
        assert native.is_checked()
        native.uncheck()
        graph.click_concept('math.cotangent_space')
        toggle = _use(_block(page, 'math.cotangent_space.gradient_example'), 'tangent').locator(
            ':scope > summary .content-block-read-toggle')
        assert not toggle.is_checked()
        # A borrowed module block uses its own durable source ID too.
        survey = _use(_block(page, 'math.cotangent_space.overview'), 'survey')
        survey.locator(':scope > summary .content-block-read-toggle').check()
        assert page.evaluate('kgContentReadProgress.isRead("math.m01_manifolds_and_coordinates.terrain_setup")')
        assert not graph.page_errors
