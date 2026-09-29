import pytest


KEY_RELATIONS = {'REQUIRES', 'DERIVES_FROM', 'CONSTRUCTED_FROM'}


def visible_relations(page):
    return set(page.evaluate("""() => edges.get().filter(e => !e.hidden).flatMap(e =>
      e.isModuleEdge ? Object.keys(e.relationCounts) : [e.relation])"""))


@pytest.mark.browser
@pytest.mark.parametrize('folded', [False, True])
@pytest.mark.parametrize('selection', ['concept', 'module'])
def test_context_relation_filter_survives_scope_and_folding(browser_graph, folded, selection):
    page = browser_graph.page
    before = page.evaluate('() => kgGlobalLayoutSnapshot()')
    assert visible_relations(page) <= KEY_RELATIONS
    page.locator('#kg_context_preset_select').select_option('connections')
    assert 'RELATED' in visible_relations(page)
    browser_graph.open_control_section('kg_modules_section')
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    if folded:
        page.locator('#kg_modules_collapse_all').click()
    if selection == 'concept':
        browser_graph.click_concept('2.1')
        assert 'RELATED' in visible_relations(page)
    else:
        assert 'RELATED' in visible_relations(page)
    for _ in range(2):
        page.locator('#kg_display_scope_select').select_option('context')
        assert 'RELATED' in visible_relations(page)
        page.locator('#kg_display_scope_select').select_option('full')
        assert 'RELATED' in visible_relations(page)
    assert page.evaluate('() => kgGlobalLayoutSnapshot()') == before
    page.locator('#kg_clear_selection').click()
    assert 'RELATED' in visible_relations(page)


@pytest.mark.browser
def test_real_full_graph_filters_internal_and_projected_edges(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page
    assert visible_relations(page) == KEY_RELATIONS
    page.locator('#kg_context_preset_select').select_option('prerequisites')
    assert visible_relations(page) == {'REQUIRES'}
    shared_repo_browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_modules_expand_all').click()
    assert visible_relations(page) == {'REQUIRES'}
    assert page.evaluate('() => edges.get().some(e => !e.isModuleEdge && e.relation === "RELATED")')
    module_id = 'gr.foundations_and_spacetime_geometry'
    expected = page.evaluate("""id => kgComputeContext(
      {type: 'module', id},
      {preset: 'prerequisites', depth: 'one-hop'}
    ).edgeIds.sort()""", module_id)
    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator('#kg_display_scope_select').select_option('context')
    actual = page.evaluate('() => edges.get().filter(e => !e.hidden).map(e => e.id).sort()')
    assert actual == expected
