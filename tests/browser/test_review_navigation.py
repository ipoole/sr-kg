import pytest

pytestmark = pytest.mark.browser


@pytest.mark.parametrize('mode', ['full', 'folded', 'core', 'maths', 'context', 'practice'])
def test_module_overview_survives_concept_filter(browser_graph, mode):
    page = browser_graph.page
    browser_graph.click_concept('2.2')
    page.locator('#kg_details_view_select').select_option(mode)
    page.locator('#info_panel .concept-module-chip').click()
    assert page.locator('#kg_details_view_select').input_value() == mode
    overview = page.locator('#info_panel .module-content-block')
    assert overview.count() == 1
    if mode == 'folded':
        assert not overview.evaluate('el => el.open')
        overview.locator('summary').click()
    assert overview.locator('.content-block-body, .content-block-fold-body').is_visible()
    if mode == 'folded':
        page.locator('#info_panel .module-members > summary').click()
    page.locator('#info_panel .module-member-concept[data-edge-concept-id="2.2"]').click()
    assert page.locator('#kg_details_view_select').input_value() == mode
    assert page.locator('#info_panel').get_attribute('data-reading-mode') == mode


def test_module_overview_does_not_replace_other_filtered_blocks(browser_graph):
    page = browser_graph.page
    page.evaluate("""() => {
      moduleData['test.m02_applications'].content_blocks.push(
        {block_id:'test.result', kind:'result', title:'Module result', body:'A useful result', sequence:20},
        {block_id:'test.warning', kind:'warning', title:'Module warning', body:'A warning', sequence:30}
      );
    }""")
    browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_module_list [data-module-id="test.m02_applications"]').click()
    page.locator('#kg_details_view_select').select_option('maths')
    assert page.locator('#info_panel .module-content-block').count() == 2
    assert page.locator('#info_panel .module-content-block.content-block-result').count() == 1
    assert page.locator('#info_panel .module-content-block.content-block-warning').count() == 0
    page.locator('#kg_details_view_select').select_option('hide')
    assert not page.locator('#info_panel').is_visible()


def test_component_direction_labels_preserve_traversal(clean_repo_browser_graph):
    page = clean_repo_browser_graph.page
    cases = [
        ('sr.electric_field', 'outgoing', ['sr.field_tensor']),
        ('sr.field_tensor', 'incoming', ['sr.electric_field', 'sr.magnetic_field']),
    ]

    for concept, direction, expected in cases:
        clean_repo_browser_graph.click_concept(concept)
        page.locator('#kg_graph_view_select').select_option('focused')
        if not page.locator('#kg_focus_lens').is_visible():
            page.locator('#kg_focus_lens_toggle').click()
        lens = page.locator('#kg_focus_lens')
        lens.locator('button[data-lens-mode="manual"]').click()
        while lens.locator('.kg-focus-lens-rule-toggle:checked').count():
            lens.locator('.kg-focus-lens-rule-toggle:checked').first.click()
        rule = lens.locator(f'.kg-focus-lens-rule-toggle[data-relation="COMPONENT_OF"][data-direction="{direction}"]')
        label = 'Part of' if direction == 'outgoing' else 'Parts of this'
        assert label in rule.get_attribute('aria-label')
        rule.click()
        visible = page.evaluate('nodes.get().filter(n => !n.hidden).map(n => n.id)')
        assert concept in visible
        assert all(item in visible for item in expected)
        if direction == 'incoming':
            backlink_ids = page.locator('#info_panel .concept-backlinks .edge-detail-concept').evaluate_all(
                "nodes => nodes.map(node => node.getAttribute('data-edge-concept-id'))"
            )
            assert all(item in backlink_ids for item in expected)


def test_auto_component_context_is_named_part_of(clean_repo_browser_graph):
    page = clean_repo_browser_graph.page
    clean_repo_browser_graph.click_concept('sr.electric_field')
    page.locator('#kg_focus_lens_toggle').click()
    page.locator('#info_panel .concept-toc-link[data-section-role="components"]').first.click()
    assert page.locator('#kg_focus_lens').get_attribute('data-lens-label') == 'Part of'
    assert page.locator(
        '#kg_focus_lens .kg-focus-lens-relation[data-relation="COMPONENT_OF"][data-direction="outgoing"]'
    ).get_attribute('data-state') == 'immediate'
