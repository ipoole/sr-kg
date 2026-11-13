def test_display_equation_line_ending_does_not_add_a_blank_paragraph(browser_graph):
    for newline in ("\n", "\r\n", "\r"):
        for blank_lines in (0, 1, 2):
            source = "Before" + newline + r"\[x=1\]" + newline * (blank_lines + 1) + "After"
            blocks = browser_graph.page.evaluate(
                "text=>kgCreateContentMarkup({}).splitConceptBlocks(text)", source)
            assert [b['kind'] for b in blocks if b['text']] == ['text', 'display-math', 'text']
            assert sum(not b['text'] for b in blocks) == blank_lines


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
        '<div id="equation-fixture"><mjx-container display="true" id="wide-equation" tabindex="2" role="math" aria-label="Original equation"><svg style="width:900px;height:30px"></svg></mjx-container>' +
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
    # Repeated geometry notifications should neither repeat expensive work in
    # one frame nor rewrite unchanged equation accessibility attributes.
    counts = page.evaluate('''async () => {
      await new Promise(requestAnimationFrame);
      let measurements = 0, mutations = 0;
      const equation = document.querySelector('#wide-equation');
      const width = Object.getOwnPropertyDescriptor(Element.prototype, 'clientWidth').get;
      Object.defineProperty(equation, 'clientWidth', {
        configurable: true, get() { measurements++; return width.call(this); }
      });
      const observer = new MutationObserver(records => { mutations += records.length; });
      observer.observe(document.querySelector('#equation-fixture'), {
        subtree: true, attributes: true, attributeFilter: ['tabindex', 'role', 'aria-label']
      });
      for (let i = 0; i < 10; i++) { window.dispatchEvent(new Event('resize')); }
      await new Promise(requestAnimationFrame);
      await Promise.resolve();
      observer.disconnect();
      delete equation.clientWidth;
      return {measurements, mutations};
    }''')
    assert counts == {'measurements': 1, 'mutations': 0}
    page.locator('#kg_view_select').select_option('details')
    hint.wait_for(state='hidden')
    assert wide.get_attribute('tabindex') == '2'
    assert wide.get_attribute('role') == 'math'
    assert wide.get_attribute('aria-label') == 'Original equation'
    page.locator('#kg_view_select').select_option('both')
    hint.wait_for(state='visible')
    wide.evaluate('e=>e.scrollLeft=100')
    assert wide.evaluate('e=>e.scrollLeft') > 0
    # Refreshing must not nest wrappers or duplicate hints.
    page.evaluate("window.dispatchEvent(new Event('resize'))")
    assert page.locator('#equation-fixture .kg-equation-scroll').count() == 2
