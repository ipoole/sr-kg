import pytest


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_k_logo_restores_starting_view_without_changing_personal_data(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 900})
    initial = page.evaluate('kgCaptureTutorialPresentation()')
    page.evaluate("""()=>{
      kgContentReadProgress.setRead('2.2.definition',true);
      kgStudyProgress.recordAttempt('2.1.q1','correct');
      kgExecuteViewerCommand({command:'select',target:'concept:2.2'});
      kgExecuteViewerCommand({command:'set-all-module-representations',value:'expanded'});
      kgExecuteViewerCommand({command:'set-display-scope',value:'overview'});
      kgExecuteViewerCommand({command:'set-context',preset:'connections',depth:'transitive'});
      kgExecuteViewerCommand({command:'set-view',value:'details'});
    }""")
    personal = page.evaluate('kgPersonalData.getSnapshot()')
    page.locator('#kg_brand_home').click()
    page.wait_for_function("kgViewerStateSnapshot().view==='both'")
    restored = page.evaluate('kgCaptureTutorialPresentation()')
    for key in ['selection','view','displayScope','contextRule','moduleRepresentation']:
        assert restored[key] == initial[key], key
    assert page.evaluate('kgPersonalData.getSnapshot()') == personal
    assert page.locator('#kg_splash_dialog[open]').count() == 0
    assert page.evaluate('kgReadingTrees.snapshot().position') is None
    assert not browser_graph.page_errors
