import pytest

pytestmark = pytest.mark.browser




def test_module_details_include_all_authored_blocks(browser_graph):
    page = browser_graph.page
    page.evaluate("""() => {
      moduleData['test.m02_applications'].content_blocks.push(
        {block_id:'test.result', kind:'result', title:'Module result', body:'A useful result', sequence:20},
        {block_id:'test.warning', kind:'warning', title:'Module warning', body:'A warning', sequence:30}
      );
    }""")
    browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_module_list [data-module-id="test.m02_applications"]').click()
    assert page.locator('#info_panel .module-content-block').count() == 3
    assert page.locator('#info_panel .module-content-block.content-block-result').count() == 1
    assert page.locator('#info_panel .module-content-block.content-block-warning').count() == 1
    page.locator('#kg_view_select').select_option('graph')
    assert not page.locator('#info_panel').is_visible()
