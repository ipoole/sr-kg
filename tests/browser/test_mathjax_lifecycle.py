def test_details_mathjax_is_cleared_before_content_is_replaced(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.wait_for_selector('#info_panel[data-concept-id="2.1"]')
    page.wait_for_function("window.MathJax && typeof MathJax.typesetClear === 'function'")

    page.evaluate("""() => {
      const panel = document.getElementById("info_panel");
      const marker = document.createElement("span");
      marker.id = "kg-old-details-marker";
      panel.appendChild(marker);
      window.__kgMathClearObservations = [];
      window.__kgOriginalTypesetClear = MathJax.typesetClear.bind(MathJax);
      MathJax.typesetClear = elements => {
        if (Array.from(elements || []).includes(panel)) {
          window.__kgMathClearObservations.push({
            markerConnected: marker.isConnected,
            currentConceptId: panel.getAttribute("data-concept-id")
          });
        }
        return window.__kgOriginalTypesetClear(elements);
      };
    }""")

    browser_graph.click_concept("2.2")
    page.wait_for_selector('#info_panel[data-concept-id="2.2"]')

    observations = page.evaluate("window.__kgMathClearObservations")
    assert observations
    assert observations[0] == {
        "markerConnected": True,
        "currentConceptId": "2.1",
    }
