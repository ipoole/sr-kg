from pathlib import Path
import pytest


@pytest.mark.browser
def test_missing_cref_is_plain_text_and_known_nested_label_remains_a_link(playwright_browser):
    _api,browser=playwright_browser
    page=browser.new_page()
    try:
        page.add_script_tag(path=str(Path(__file__).parents[2]/"srkg/viewer_assets/content_markup.js"))
        rendered=page.evaluate(r'''() => {
          const markup=kgCreateContentMarkup({concept:id => id==='local.one' ? {} : null,hash:id=>'#concept-'+id});
          return {
            missing: markup.renderConceptText('Before \\cref{a {nested} label}{absent.one} after.'),
            known: markup.renderConceptText('\\cref{a {nested} label}{local.one}'),
            escaped: markup.renderConceptText('\\cref{<unsafe>}{absent.one}')
          };
        }''')
        page.set_content('<main>'+rendered['missing']+'</main>')
        assert page.locator('main').inner_text() == 'Before a {nested} label after.'
        assert page.locator('main a, main strong').count() == 0
        page.set_content(rendered['known'])
        assert page.locator('a').get_attribute('data-concept-id') == 'local.one'
        assert page.locator('a').inner_text() == 'a {nested} label'
        assert rendered['escaped'] == '&lt;unsafe&gt;'
    finally:
        page.close()


@pytest.mark.browser
@pytest.mark.parametrize("gr_repo_browser_graph",[False,True],indirect=True,ids=["desktop","phone"])
def test_gr_only_viewer_has_no_dangling_graph_or_prose_links(gr_repo_browser_graph):
    graph=gr_repo_browser_graph
    page=graph.page
    assert page.evaluate("Object.keys(conceptData).length > 0 && Object.keys(conceptData).every(id => id.startsWith('gr.'))")
    assert page.evaluate("Object.keys(moduleData).every(id => id.startsWith('gr.'))")
    assert page.evaluate("edges.get().every(edge => nodes.get(edge.from) && nodes.get(edge.to))")
    assert page.evaluate("kgSequentialConceptIds().every(id => id.startsWith('gr.'))")
    sample=page.evaluate(r'''() => {
      for (const [id,concept] of Object.entries(conceptData)) {
        for (const block of concept.content_blocks || []) {
          const expression = /\\cref\{([^{}]*)\}\{([^{}]*)\}/g;
          let match;
          while ((match=expression.exec(block.body))) {
            if (!conceptData[match[2]]) return {id,blockId:block.block_id,label:match[1],target:match[2]};
          }
        }
      }
      return null;
    }''')
    if sample:
        page.evaluate("id => kgExecuteViewerCommand({command:'select',target:'concept:'+id})",sample['id'])
        page.evaluate("id => kgExecuteViewerCommand({command:'open-details-block',target:'block:'+id})",sample['blockId'])
        block=page.locator('[data-content-block-id="'+sample['blockId']+'"]')
        assert sample['label'] in block.inner_text()
        assert block.locator('a[data-concept-id="'+sample['target']+'"]').count() == 0
        assert '\\cref' not in block.inner_text()
    assert graph.page_errors == []
