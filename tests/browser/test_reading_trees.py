"""Generated reading paths use canonical blocks and the actual Context graph."""
import pandas as pd
import pytest

from conftest import (
    _open_browser_graph, _prepare_browser_output, _use_stub_mathjax,
    _write_browser_fixture,
)


@pytest.fixture(scope="session")
def reading_tree_output(tmp_path_factory):
    root = tmp_path_factory.mktemp("reading-trees")
    _write_browser_fixture(root, include_constructed_from=True)
    (root / "tutorials.yaml").unlink()
    edges = pd.read_csv(root / "edges.csv").fillna("")
    edges.loc[len(edges)] = {"source": "1.1", "target": "3.1",
        "relation": "DERIVES_FROM", "note": "A deliberate ancestor cycle."}
    edges.to_csv(root / "edges.csv", index=False)
    blocks = pd.read_csv(root / "content_blocks.csv").fillna("")
    blocks["statement"] = ""
    blocks.loc[blocks.block_id == "3.1.definition", "statement"] = "A concise root statement."
    blocks.loc[blocks.block_id == "1.1.definition", "statement"] = r"A local result \(x=1\)."
    blocks.loc[blocks.block_id == "1.1.definition", "body"] = (
        "First paragraph.\nSecond paragraph."
        r"\explanation{algebra}{A closer look}{Local reasoning.}")
    # Deliberately interleave native kinds, including two Explanation blocks.
    for suffix, kind, sequence in [('example', 'example', 1), ('intuition', 'intuition', 2),
                                    ('explanation.first', 'explanation', 20),
                                    ('explanation.second', 'explanation', 30)]:
        blocks.loc[len(blocks)] = {'block_id': '3.1.' + suffix, 'concept_id': '3.1',
            'sequence': sequence, 'kind': kind, 'title': suffix,
            'body': 'Fixture teaching content.', 'statement': 'A fixture result.'}
    blocks.to_csv(root / "content_blocks.csv", index=False)
    output = _prepare_browser_output(root, root, "Reading-tree fixture")
    fast = root / "fast.html"
    fast.write_text(_use_stub_mathjax(output.read_text()))
    return fast


@pytest.fixture
def reading_graph(reading_tree_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, reading_tree_output) as graph:
        graph.click_concept("3.1")
        graph.page.locator("#kg_view_select").select_option("details")
        graph.page.locator("#kg_controls_toggle").click()
        yield graph


def _open_concept(element):
    element.locator(":scope > .kg-reading-concept-title > button").click()


@pytest.mark.browser
def test_initial_depth_and_session_recipe_choice(reading_graph):
    page = reading_graph.page
    card = page.locator('[data-reading-recipe="teaching"].kg-reading-tree')
    card.locator(':scope > summary').click()
    depth = card.locator('[data-reading-depth]')
    assert depth.input_value() == 'three-hops'
    depth.select_option('one-hop')
    reading_graph.click_concept('2.1')
    reading_graph.click_concept('3.1')
    card.locator(':scope > summary').click()
    assert depth.input_value() == 'one-hop'
    other = page.locator('[data-reading-recipe="derivation"].kg-reading-tree')
    other.locator(':scope > summary').click()
    assert other.locator('[data-reading-depth]').input_value() == 'three-hops'


@pytest.mark.browser
@pytest.mark.parametrize("width", [390, 1280])
def test_blocks_and_graph_generated_routes(reading_graph, width):
    page = reading_graph.page
    page.set_viewport_size({"width": width, "height": 950})
    native = page.locator('#info_panel > [data-content-block-id="3.1.definition"]')
    assert not native.evaluate("e=>e.open")
    assert native.locator(":scope > summary .kg-content-statement").is_visible()
    before = page.evaluate("({state:kgViewerStateSnapshot(),camera:network.getViewPosition(),scale:network.getScale()})")
    for recipe, preset in [("derivation", "derivation"), ("teaching", "foundations")]:
        card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
        assert not card.evaluate("e=>e.open")
        card.locator(":scope > summary").click()
        page.wait_for_function("id=>document.getElementById(id).hasAttribute('data-reading-loaded')", arg=card.get_attribute("id"))
        card.locator("[data-reading-depth]").select_option("transitive")
        for _ in range(12):
            closed = card.locator(".kg-reading-concept:not([open])")
            if not closed.count():
                break
            closed.evaluate_all("es=>es.forEach(e=>e.open=true)")
            page.wait_for_function("""selector=>[...document.querySelectorAll(selector)]
                .filter(e=>e.open).every(e=>e.hasAttribute('data-reading-loaded'))""",
                arg=f'[data-reading-recipe="{recipe}"] .kg-reading-concept')
        else:
            pytest.fail("Reading tree failed to terminate")
        expected = page.evaluate("""preset=>kgComputeContext({type:'concept',id:'3.1'},
            {preset,depth:'transitive'})""", preset)
        actual = card.locator("[data-reading-edge]").evaluate_all(
            "es=>[...new Set(es.map(e=>e.dataset.readingEdge))]")
        assert set(actual) == set(expected["edgeIds"])
        assert card.locator(".kg-reading-concept-container > .kg-reading-boundary").count() > 0
        assert card.locator(".kg-reading-block[open]").count() == 0
        assert card.locator(".kg-content-statement").count() > 0
    after = page.evaluate(
        "({state:kgViewerStateSnapshot(),camera:network.getViewPosition(),scale:network.getScale()})"
    )
    assert after["state"] == before["state"]
    assert after["camera"] == pytest.approx(before["camera"], rel=0, abs=1e-9)
    assert after["scale"] == pytest.approx(before["scale"], rel=0, abs=1e-9)
    assert page.evaluate("document.getElementById('info_panel').scrollWidth<=document.getElementById('info_panel').clientWidth+1")
    assert not reading_graph.page_errors


@pytest.mark.browser
def test_sync_prepares_context_then_reading_position_leaves_camera_alone(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    card.locator(":scope > summary").click()
    page.wait_for_function("id=>document.getElementById(id).hasAttribute('data-reading-loaded')", arg=card.get_attribute("id"))
    card.locator(".kg-reading-sync").check()
    page.wait_for_function("kgViewerStateSnapshot().displayScope==='context'")
    page.wait_for_timeout(500)
    camera = page.evaluate("({pos:network.getViewPosition(),scale:network.getScale(),folds:kgViewerStateSnapshot().selection})")
    assert page.evaluate("kgViewerStateSnapshot().contextRule.preset") == "foundations"
    assert page.evaluate("kgReadingTrees.snapshot().synchronised") == "teaching"
    assert page.locator("#kg_display_scope_select").input_value() == "context"
    assert page.locator("#kg_view_select").input_value() == "both"
    concept = card.locator('.kg-reading-concept-container[data-reading-concept="2.2"]').first
    _open_concept(concept)
    page.wait_for_function("kgReadingTrees.snapshot().position==='2.2'")
    assert page.evaluate("kgViewerStateSnapshot().selection") == {"type": "concept", "id": "3.1"}
    assert page.evaluate("({pos:network.getViewPosition(),scale:network.getScale(),folds:kgViewerStateSnapshot().selection})") == camera
    assert page.evaluate("kgReadingMarkerSnapshot().conceptId") == "2.2"
    page.locator("#kg_view_select").select_option("both")
    page.locator("#kg_context_preset_select").select_option("connections")
    assert page.evaluate("kgReadingTrees.snapshot().synchronised") is None
    assert page.evaluate("kgReadingMarkerSnapshot()") is None
    assert concept.locator(":scope > .justification").is_visible()
    assert not reading_graph.page_errors


@pytest.mark.browser
def test_reading_occurrences_share_progress_notes_and_preserve_focus(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    card.locator(":scope > summary").click()
    page.wait_for_function("id=>document.getElementById(id).hasAttribute('data-reading-loaded')",
                           arg=card.get_attribute("id"))
    for _ in range(12):
        closed = card.locator(".kg-reading-concept:not([open])")
        if not closed.count():
            break
        closed.evaluate_all("es=>es.forEach(e=>e.open=true)")
        page.wait_for_function("""() => [...document.querySelectorAll('.kg-reading-concept[open]')]
            .every(e=>e.hasAttribute('data-reading-loaded'))""")
    copies = card.locator('[data-content-block-id="1.1.definition"]')
    assert copies.count() >= 2
    copies.first.locator(":scope > summary").click()
    copies.first.locator(":scope > summary .content-block-read-toggle").check()
    assert copies.locator(":scope > summary .content-block-read-toggle").evaluate_all(
        "es=>es.every(e=>e.checked)")
    assert page.evaluate("kgContentReadProgress.isRead('1.1.definition')")
    branch = card.locator('.kg-reading-concept-container[data-reading-concept="1.1"]').first
    branch.locator(":scope > details > .kg-reading-concept-body > .kg-reading-focus-button").click()
    assert page.evaluate("kgReadingTrees.snapshot().focusDepth") == 1
    focused = page.locator('#kg-reading-focus [data-content-block-id="1.1.definition"]')
    focused.locator(":scope > summary .kg-note-block-action").click()
    focused.locator(".kg-note-placement-target").first.click()
    page.locator(".user-note-body-input").fill("A canonical reading note.")
    page.locator(".user-note-close").click()
    assert page.evaluate("kgReadingTrees.snapshot().focusDepth") == 1
    assert page.locator("#kg-reading-focus .user-note").count() == 1
    clarification = page.locator("#kg-reading-focus .kg-local-explanation").first
    clarification.locator(":scope > summary").click()
    clarification.locator(":scope > .kg-content-body > .kg-reading-focus-button").click()
    assert page.evaluate("kgReadingTrees.snapshot().position") == "1.1"
    assert page.evaluate("kgReadingTrees.snapshot().focusDepth") == 2
    page.locator(".kg-reading-return").click()
    page.locator(".kg-reading-return").click()
    assert page.evaluate("kgReadingTrees.snapshot().focusDepth") == 0
    assert copies.locator(".user-note").count() == copies.count()
    assert card.locator(".kg-unmatched-notes").count() == 0
    reading_graph.click_concept("1.1")
    native = page.locator('#info_panel > [data-content-block-id="1.1.definition"]')
    assert native.locator(".user-note").count() == 1
    assert native.locator(":scope > summary .content-block-read-toggle").is_checked()
    assert not reading_graph.page_errors


@pytest.mark.browser
def test_recipe_orders_kinds_and_preserves_authored_order_within_kind(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    card.locator(':scope > summary').click()
    page.wait_for_function("id=>document.getElementById(id).hasAttribute('data-reading-loaded')", arg=card.get_attribute('id'))
    expected = ['3.1.definition', '3.1.explanation.first', '3.1.explanation.second',
                '3.1.intuition', '3.1.example']
    assert page.locator('#info_panel > [data-content-block-id]').evaluate_all(
        'es=>es.map(e=>e.dataset.contentBlockId)') == [
        '3.1.example', '3.1.intuition', '3.1.definition',
        '3.1.explanation.first', '3.1.explanation.second']
    assert card.locator(':scope > .kg-reading-tree-body > .kg-reading-root > .kg-reading-block').evaluate_all(
        'es=>es.map(e=>e.dataset.contentBlockId)') == expected


@pytest.mark.browser
def test_tutorial_reading_actions_and_checkpoint_preserve_the_reading_path(reading_graph):
    page = reading_graph.page
    def command(**values):
        return page.evaluate('(c)=>kgExecuteViewerCommand(c,{origin:"tutorial"})', values)
    command(command='open-reading-tree', recipe='teaching', depth='three-hops')
    command(command='open-reading-tree', recipe='teaching', target='concept:2.2')
    assert page.evaluate('kgReadingTrees.snapshot().position') == '2.2'
    saved = page.evaluate('kgCaptureTutorialPresentation()')
    command(command='open-reading-tree', recipe='teaching', synchronise=True)
    assert page.evaluate('kgReadingTrees.snapshot().synchronised') == 'teaching'
    assert page.evaluate('kgViewerStateSnapshot().selection.id') == '3.1'
    assert page.evaluate('kgReadingMarkerSnapshot().conceptId') == '2.2'
    command(command='select', target='concept:1.1')
    page.evaluate('(s)=>kgRestoreTutorialPresentation(s)', saved)
    assert page.evaluate('kgCaptureTutorialPresentation().reading') == saved['reading']
    card = page.locator('.kg-reading-tree[data-reading-recipe="teaching"]')
    assert card.evaluate('e=>e.open')
    assert card.locator('.kg-reading-concept[data-reading-node="2.2"]').first.evaluate('e=>e.open')
    assert page.evaluate('kgReadingTrees.snapshot().synchronised') is None
    command(command='select', target='concept:2.1')
    command(command='open-reading-tree', recipe='teaching', target='concept:1.1', synchronise=True)
    page.wait_for_timeout(100)
    assert page.evaluate('kgReadingMarkerSnapshot().conceptId') == '1.1'
    assert not reading_graph.page_errors


@pytest.mark.browser
def test_tutorial_checkpoint_restores_full_width_reading(reading_graph):
    from test_maths_reading_trees import _reveal_tree
    page = reading_graph.page
    card = page.locator('.kg-reading-tree[data-reading-recipe="teaching"]')
    _reveal_tree(page, card)
    branch = card.locator('[data-reading-concept="1.1"]').first
    branch.locator(':scope > details > .kg-reading-concept-body > .kg-reading-focus-button').click()
    saved = page.evaluate('kgCaptureTutorialPresentation()')
    assert saved['reading']['focus']
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:2.1'},{origin:'tutorial'})")
    page.evaluate('(s)=>kgRestoreTutorialPresentation(s)', saved)
    assert page.locator('#info_panel').evaluate('e=>e.classList.contains("kg-reading-focus-active")')
    assert page.evaluate('kgCaptureTutorialPresentation().reading') == saved['reading']
    assert not reading_graph.page_errors


@pytest.mark.browser_full
@pytest.mark.parametrize("width", [390, 1280])
def test_tutorial_reading_statements_are_typeset_before_framing(
    reading_tree_output, playwright_browser, width,
):
    """Programmatic expansion must typeset lazy content, including on resume."""
    from playwright.sync_api import expect

    api, browser = playwright_browser
    with _open_browser_graph(api, browser, reading_tree_output.with_name("viewer.html"),
                             context_options={"viewport": {"width": width, "height": 950}}) as graph:
        page = graph.page
        page.evaluate(r"""() => {
            for (const id of ['3.1', '2.1']) {
                conceptData[id].content_blocks.find(b => b.kind === 'definition').statement =
                    String.raw`A mathematical statement \(E_0=mc^2\).`;
            }
        }""")
        graph.click_concept("3.1")
        page.locator("#kg_view_select").select_option("details")
        page.evaluate("MathJax.startup.promise")
        # Finish the initial panel pass before any reading-tree DOM exists.
        page.evaluate("MathJax.typesetPromise([document.getElementById('info_panel')])")
        page.evaluate("""kgExecuteViewerCommand({command:'open-reading-tree',
            recipe:'teaching', depth:'three-hops', target:'concept:2.1'}, {origin:'tutorial'})""")

        def assert_statements_rendered():
            card = page.locator('.kg-reading-tree[data-reading-recipe="teaching"]')
            for node in ['3.1', '2.1']:
                statement = card.locator(
                    f'[data-content-block-id="{node}.definition"] > summary .kg-content-statement'
                ).first
                expect(statement.locator('mjx-container')).to_have_count(1)
                assert statement.locator('[data-mml-node="merror"]').count() == 0

        assert_statements_rendered()
        saved = page.evaluate('kgCaptureTutorialPresentation()')
        page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:1.1'},{origin:'tutorial'})")
        page.evaluate('(saved)=>kgRestoreTutorialPresentation(saved)', saved)
        assert_statements_rendered()
        assert not graph.page_errors
