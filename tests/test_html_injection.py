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
    assert "function kgAfterReady()" in injected
    assert "var conceptData = {};" in injected
    assert "var edgeKey = {};" in injected


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
    )

    assert "Closing <\\/script><b>tag<\\/b>" in injected
    assert "Also <\\/script><i>unsafe<\\/i>" in injected
    assert "Closing </script><b>tag</b>" not in injected
    assert "Also </script><i>unsafe</i>" not in injected
