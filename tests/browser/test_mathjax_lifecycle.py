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


def test_wide_equations_advertise_scrolling_only_while_overflowing(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    page.locator('#info_panel').evaluate('''panel => {
      panel.insertAdjacentHTML('beforeend',
        '<div id="equation-fixture"><mjx-container display="true" id="wide-equation"><svg style="width:900px;height:30px"></svg></mjx-container>' +
        '<mjx-container display="true" id="short-equation"><svg style="width:40px;height:30px"></svg></mjx-container></div>');
      window.dispatchEvent(new Event('resize'));
    }''')
    wide = page.locator('#wide-equation')
    short = page.locator('#short-equation')
    hint = page.locator('#equation-fixture .kg-equation-scroll').first.locator('.kg-equation-scroll-hint')
    hint.wait_for(state='visible')
    assert wide.get_attribute('tabindex') == '0'
    assert wide.get_attribute('role') == 'region'
    assert short.get_attribute('tabindex') is None
    assert page.locator('#equation-fixture .kg-equation-scroll').count() == 2
    page.locator('#kg_view_select').select_option('details')
    hint.wait_for(state='hidden')
    assert wide.get_attribute('tabindex') is None
    page.locator('#kg_view_select').select_option('both')
    hint.wait_for(state='visible')
    wide.evaluate('e=>e.scrollLeft=100')
    assert wide.evaluate('e=>e.scrollLeft') > 0
    # Refreshing must not nest wrappers or duplicate hints.
    page.evaluate("window.dispatchEvent(new Event('resize'))")
    assert page.locator('#equation-fixture .kg-equation-scroll').count() == 2
