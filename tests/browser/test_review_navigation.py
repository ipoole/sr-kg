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
