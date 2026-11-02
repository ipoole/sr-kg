import pytest


@pytest.mark.browser
@pytest.mark.parametrize("future_domain_graph", [False, True], indirect=True, ids=["desktop", "phone"])
def test_future_domain_collection_boots_and_navigates_without_physics_assumptions(future_domain_graph):
    graph=future_domain_graph
    page=graph.page
    assert page.evaluate("Object.keys(conceptData)") == ["molbio.one", "molbio.two"]
    assert page.evaluate("kgViewerConfig.domains[0].label") == "BIO"
    assert page.evaluate("kgViewerStateSnapshot().selection") == {"type": "module", "id": "molbio.m1"}
    page.evaluate("kgExecuteViewerCommand({command:'set-module-representation',target:'module:molbio.m1',value:'expanded'})")
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:molbio.one'})")
    assert page.locator("#info_panel").get_attribute("data-concept-id") == "molbio.one"
    assert page.evaluate("kgSequentialConceptIds()") == ["molbio.one", "molbio.two"]
    assert page.url.endswith("#concept-molbio.one")
    assert graph.page_errors == []
