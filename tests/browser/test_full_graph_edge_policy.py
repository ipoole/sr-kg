import pytest


KEY_RELATIONS = {'REQUIRES', 'DERIVES_FROM', 'CONSTRUCTED_FROM'}


def visible_relations(page):
    return set(page.evaluate("""() => edges.get().filter(e => !e.hidden).flatMap(e =>
      e.isModuleEdge ? Object.keys(e.relationCounts) : [e.relation])"""))


@pytest.mark.browser
@pytest.mark.parametrize('folded', [False, True])
@pytest.mark.parametrize('selection', ['concept', 'module'])
def test_full_graph_filters_edges_and_focused_restores_them(browser_graph, folded, selection):
    page = browser_graph.page
    before = page.evaluate('() => kgGlobalLayoutSnapshot()')
    assert visible_relations(page) <= KEY_RELATIONS
    browser_graph.open_control_section('kg_modules_section')
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    if folded:
        page.locator('#kg_modules_collapse_all').click()
    if selection == 'concept':
        browser_graph.click_concept('2.1')
        assert 'RELATED' in visible_relations(page)
    else:
        assert visible_relations(page) <= KEY_RELATIONS
    for _ in range(2):
        page.locator('#kg_graph_view_select').select_option('focused')
        assert 'RELATED' in visible_relations(page)
        page.locator('#kg_graph_view_select').select_option('all')
        if selection == 'concept':
            assert 'RELATED' in visible_relations(page)
        else:
            assert visible_relations(page) <= KEY_RELATIONS
    assert page.evaluate('() => kgGlobalLayoutSnapshot()') == before
    page.locator('#kg_clear_selection').click()
    assert visible_relations(page) <= KEY_RELATIONS


@pytest.mark.browser
def test_real_full_graph_filters_internal_and_projected_edges(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page
    assert visible_relations(page) == KEY_RELATIONS
    shared_repo_browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_modules_expand_all').click()
    assert visible_relations(page) == KEY_RELATIONS
    assert page.evaluate('() => edges.get().some(e => !e.isModuleEdge && e.relation === "RELATED")')
    module_id = 'gr.foundations_and_spacetime_geometry'
    expected = page.evaluate("""id => {
      const members = new Set(moduleData[id].members);
      return edges.get().filter(e => !e.isModuleEdge && (members.has(e.from) || members.has(e.to)))
        .map(e => e.id).sort();
    }""", module_id)
    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator('#kg_graph_view_select').select_option('focused')
    actual = page.evaluate('() => edges.get().filter(e => !e.hidden).map(e => e.id).sort()')
    assert actual == expected
