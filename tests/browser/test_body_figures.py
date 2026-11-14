"""Body artwork and folded previews share assets without new navigation/read state."""
import csv
import pytest
from conftest import _write_browser_fixture, _prepare_browser_output, _open_browser_graph, _use_stub_mathjax
from test_maths_reading_trees import _reveal_tree


@pytest.fixture(scope='session')
def figure_output(tmp_path_factory):
    root = tmp_path_factory.mktemp('body-figures')
    _write_browser_fixture(root)
    (root/'arrow.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
    <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z"/></marker></defs>
    <path d="M20 50L180 50" stroke="blue" stroke-width="4" marker-end="url(#arrow)"/></svg>''')
    with (root/'figures.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['figure_id', 'svg_path', 'caption', 'alt'])
        w.writeheader(); w.writerow(dict(figure_id='test.figure.arrow', svg_path='arrow.svg',
                                        caption='One physical arrow.', alt='An unchanged rightward arrow.'))
    p = root/'content_blocks.csv'
    with p.open() as f:
        reader = csv.DictReader(f); fields = list(reader.fieldnames)+['statement', 'preview_figure']; rows = list(reader)
    for row in rows:
        if row['block_id'] == '2.1.explanation':
            row.update(statement='The vector is unchanged.', preview_figure='vector',
                       body='Before the figure.\n\n'+r'\figure{vector}{test.figure.arrow}'+'\n\nAfter the figure.\n\n'+
                       r'\explanation{local}{A closer look}{Local prose.\figure{local-vector}{test.figure.arrow}}')
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    output = _prepare_browser_output(root, root, 'Body figures')
    output.write_text(_use_stub_mathjax(output.read_text()))
    return output


def block(page):
    return page.locator('#info_panel > [data-content-block-id="2.1.explanation"]')


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_thumbnail_body_and_reading_tree_share_figure_without_duplicate_svg_ids(figure_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, figure_output, {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page; graph.click_concept('2.1'); page.locator('#kg_view_select').select_option('details')
        unit = block(page); thumb = unit.locator(':scope > summary .kg-content-preview')
        assert thumb.is_visible() and thumb.get_attribute('aria-hidden') == 'true'
        rect = thumb.locator('svg').bounding_box()
        assert rect['height'] <= 121 and abs(rect['width']/rect['height']-2) < .02
        assert thumb.locator('figcaption').count() == 0
        assert not unit.locator('.kg-body-figure').first.is_visible()
        thumb.click()
        assert not thumb.is_visible()
        assert unit.locator('.kg-body-figure').first.is_visible()
        assert unit.locator('.kg-body-figure [role="img"]').first.get_attribute('aria-label')
        assert unit.locator('.kg-body-figure').first.locator('figcaption').is_visible()
        unit.locator('.kg-local-explanation > summary').click()
        assert unit.locator('.kg-body-figure').count() == 2
        ids = unit.locator('svg [id]').evaluate_all('es=>es.map(e=>e.id)')
        assert len(ids) == len(set(ids))
        unit.locator(':scope > summary .content-block-read-toggle').check()
        unit.locator(':scope > summary').click()
        assert thumb.is_visible()
        unit.locator(':scope > summary').focus()
        page.keyboard.press('Enter')
        assert not thumb.is_visible()
        assert unit.locator('.kg-body-figure').first.is_visible()
        # Opening a reading-tree occurrence leaves selection and its block identity intact.
        graph.click_concept('3.1')
        tree = page.locator('details[data-reading-recipe="teaching"]')
        _reveal_tree(page, tree)
        copy = tree.locator('[data-content-block-id="2.1.explanation"]')
        assert copy.locator(':scope > summary .kg-content-preview').is_visible()
        assert copy.locator(':scope > summary .content-block-read-toggle').is_checked()
        copy.locator(':scope > summary').click()
        assert copy.locator('.kg-body-figure').first.is_visible()
        assert not page.locator('#info_panel .kg-unmatched-notes').count()
        assert not graph.page_errors


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_notes_after_figures_and_existing_paragraphs_survive_figure_insertion(figure_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, figure_output, {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page; graph.click_concept('2.1'); page.locator('#kg_view_select').select_option('details')
        unit = block(page)
        for selector, title in [('.kg-body-figure', 'Figure observation'), ('.concept-line', 'Passage observation')]:
            unit.locator(':scope > summary .kg-note-block-action').click()
            line = (unit.locator('.kg-body-figure').first.locator('xpath=ancestor::div[contains(@class,"concept-line")][1]')
                    if selector == '.kg-body-figure' else unit.locator('.concept-line').filter(has_text='After the figure.').first)
            line.click(position={'x': 3, 'y': 3})
            unit.locator('.user-note-title-input').fill(title)
            unit.locator('.user-note-body-input').fill('Saved observation.')
            unit.locator('.user-note-close').click()
        page.evaluate("""addition => {
          const source=conceptData['2.1'].content_blocks.find(b=>b.block_id==='2.1.explanation');
          source.body=source.body.replace('Before the figure.', 'Before the figure.'+addition);
        }""", "\n\n"+r"\figure{inserted}{test.figure.arrow}"+"\n\n")
        graph.click_concept('1.1'); graph.click_concept('2.1')
        unit = block(page); unit.locator(':scope > summary').click()
        assert unit.locator('.kg-body-figure').count() == 3
        assert unit.locator('.user-note').count() == 2
        assert not page.locator('#info_panel .kg-unmatched-notes').count()
        paragraph = unit.locator('.concept-line').filter(has_text='After the figure.').first
        assert paragraph.evaluate("e=>e.nextElementSibling.matches('.user-note') && e.nextElementSibling.textContent.includes('Passage observation')")
        figure_line = unit.locator('.kg-body-figure[data-figure-slot="vector"]').first.locator('xpath=ancestor::div[contains(@class,"concept-line")][1]')
        assert figure_line.evaluate("e=>e.nextElementSibling.matches('.user-note') && e.nextElementSibling.textContent.includes('Figure observation')")
        assert not graph.page_errors
