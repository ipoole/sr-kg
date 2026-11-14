"""Body figures share registered artwork and retain explicit occurrence identity."""
import pandas as pd
import pytest

from srkg.content_units import ContentFigure, ContentExplanation, build_content_registry, parse_content
from srkg.figures import Figure, load_figures
from srkg.model import Concept, ContentBlock
from srkg.schema import KnowledgeBaseLoadError

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><path d="M0 0L100 50"/></svg>'


def source(body, preview=''):
    block = ContentBlock('gr.demo.intuition', 'gr.demo', 10, 'intuition', 'A fixed arrow', body,
                         statement='The vector stays fixed.', preview_figure=preview)
    return Concept('gr.demo', 'Demo', content_blocks=[block])


def test_body_figure_and_nested_figure_parse_without_changing_text():
    parts = parse_content(r'Before\figure{main}{gr.figure.arrow}After'
                          r'\explanation{why}{Why?}{\figure{local}{gr.figure.arrow}}')
    assert parts[1] == ContentFigure('main', 'gr.figure.arrow')
    assert parts[0].text == 'Before' and parts[2].text == 'After'
    assert isinstance(parts[3], ContentExplanation)
    assert parts[3].parts == (ContentFigure('local', 'gr.figure.arrow'),)
    assert parts[1].to_viewer_data() == {'type': 'figure', 'slot': 'main', 'figure_id': 'gr.figure.arrow'}


def test_preview_designates_a_main_body_occurrence_not_another_asset():
    unit = source(r'Intro\figure{main}{gr.figure.arrow}After', 'main')
    figures = {'gr.figure.arrow': Figure('gr.figure.arrow', SVG, 'An unchanged vector.', 'A blue arrow.')}
    registry = build_content_registry([unit], [], domains=['gr'], figures=figures)
    assert registry['gr.demo.intuition'].to_viewer_data()['preview_figure'] == 'main'
    assert registry['gr.demo.intuition'].parts[1].figure_id in registry.figures
    with pytest.raises(KnowledgeBaseLoadError, match='preview'):
        build_content_registry([source(r'\figure{main}{gr.figure.arrow}', 'absent')], [], domains=['gr'], figures=figures)
    with pytest.raises(KnowledgeBaseLoadError, match='preview'):
        build_content_registry([source(r'\explanation{why}{Why?}{\figure{main}{gr.figure.arrow}}', 'main')], [], domains=['gr'], figures=figures)


def test_missing_loaded_figure_is_an_error_but_excluded_domain_is_a_warning():
    unit = source(r'\figure{main}{math.figure.arrow}')
    with pytest.raises(KnowledgeBaseLoadError, match='math.figure.arrow'):
        build_content_registry([unit], [], domains=['gr', 'math'])
    registry = build_content_registry([unit], [], domains=['gr'])
    assert [(w.domain, w.kind) for w in registry.warnings] == [('math', 'figure-reference')]


@pytest.mark.parametrize('body', [r'\figure{bad/slot}{gr.figure.a}', r'\figure{a}{no_namespace}',
                                r'\figure{a}{gr.figure.a}\figure{a}{gr.figure.a}', r'\figure{a}'])
def test_invalid_figure_references_fail_at_load_time(body):
    with pytest.raises(KnowledgeBaseLoadError):
        parse_content(body)


def test_registered_svg_is_domain_local_and_optional_for_text_only_loading(tmp_path):
    (tmp_path/'arrow.svg').write_text(SVG)
    frame = pd.DataFrame([dict(figure_id='gr.figure.arrow', svg_path='arrow.svg',
                               caption='Fixed.', alt='A blue arrow.', _asset_root=str(tmp_path))])
    assert load_figures(frame)['gr.figure.arrow'].svg == SVG
    assert load_figures(frame, include_svg=False)['gr.figure.arrow'].svg == ''
    frame.loc[0, 'svg_path'] = '../outside.svg'
    with pytest.raises(KnowledgeBaseLoadError, match='escapes'):
        load_figures(frame)
