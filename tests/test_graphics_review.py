from tools.show_graphics import Concept, render_html


def test_review_sheet_resolves_graphics_by_semantic_id():
    concept = Concept(
        id="sr.time_dilation", display_id="SR-1.9", label="Time dilation",
        icon_caption="", detail_caption="",
    )
    html = render_html([concept], ["SR-1.9"])
    assert html.count("<svg") == 2
    assert 'class="missing"' not in html
