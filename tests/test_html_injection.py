import pytest

from srkg.html_injection import inject_controls, require_html_marker


def _base_pyvis_html():
    return "<html><head></head><body><div id=\"mynetwork\"></div></body></html>"


def test_require_html_marker_raises_clear_error_for_missing_marker():
    with pytest.raises(ValueError) as exc:
        require_html_marker("<html></html>", "</body>")

    assert str(exc.value) == "Generated PyVis HTML is missing expected marker: </body>"


@pytest.mark.parametrize("html_text", [
    "<html><body></body></html>",
    "<html><head></head></html>",
    "<html><head></head><body></html>",
])
def test_inject_controls_requires_expected_pyvis_markers(html_text):
    with pytest.raises(ValueError, match="Generated PyVis HTML is missing expected marker"):
        inject_controls(html_text, {}, {}, "Title")


def test_inject_controls_adds_viewer_shell_and_escapes_title():
    injected = inject_controls(
        _base_pyvis_html(),
        {},
        {},
        "SR <Graph> & Fields",
    )

    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in injected
    assert '<div id="kg_view_title">SR &lt;Graph&gt; &amp; Fields</div>' in injected
    assert "<h2>SR &lt;Graph&gt; &amp; Fields</h2>" in injected
    assert 'id="kg_controls"' in injected
    assert 'id="info_panel"' in injected
    assert 'coloneqq: "\\\\mathrel{:=}"' in injected
    assert "function kgAfterReady()" in injected
    assert "var kgModuleGeometry =" in injected
    assert "global.kgCreatePersonalDataStore = createStore" in injected
    assert injected.index("var kgModuleGeometry =") < injected.index("var conceptData =")
    assert "var conceptData = {};" in injected
    assert "var moduleData = {};" in injected
    assert 'var publishedLayout = {"schema_version": 1, "revision": "unpublished", "concepts": {}, "modules": {}};' in injected
    assert "var edgeKey = {};" in injected
    assert '"globalLayout": "srkg.layout.global.v1"' in injected
    assert '"studyProgress": "srkg.studyProgress.v1"' in injected
    assert '"contentReadProgress": "srkg.contentReadProgress.v1"' in injected
    assert '"personalData": "srkg.personalData.v1"' in injected
    assert '"personalDataDevice": "srkg.personalData.device.v1"' in injected


def test_viewer_omits_redundant_tools_details_toggle_and_includes_credit():
    injected = inject_controls(_base_pyvis_html(), {}, {}, "Title")

    assert "kg_info_toggle" not in injected
    assert "kgToggleInfoPanel" not in injected
    assert 'id="kg_details_view_select"' in injected
    assert injected.count("Select a concept or module, or double-click a module to expand it.") == 2
    assert 'class="kg-splash-credit"' in injected
    assert 'href="https://www.linkedin.com/in/ipoole/" target="_blank" rel="noopener noreferrer">Ian Poole</a>' in injected
    assert "with AI assistance via OpenAI Codex." in injected


def test_inject_controls_serializes_json_without_literal_script_closers():
    injected = inject_controls(
        _base_pyvis_html(),
        {
            "1.1": {
                "label": "Closing </script><b>tag</b>",
            },
        },
        {
            "REL": {
                "meaning": "Also </script><i>unsafe</i>",
                "directed": True,
            },
        },
        "Title",
        module_data={
            "module.one": {
                "title": "Module </script><em>unsafe</em>",
            },
        },
        published_layout={
            "schema_version": 1,
            "revision": "test-1",
            "concepts": {"1.1": {"x": 10, "y": 20}},
            "modules": {},
        },
    )

    assert "Closing <\\/script><b>tag<\\/b>" in injected
    assert "Also <\\/script><i>unsafe<\\/i>" in injected
    assert "Module <\\/script><em>unsafe<\\/em>" in injected
    assert 'var publishedLayout = {"schema_version": 1, "revision": "test-1"' in injected
    assert "Closing </script><b>tag</b>" not in injected
    assert "Also </script><i>unsafe</i>" not in injected
    assert "Module </script><em>unsafe</em>" not in injected
