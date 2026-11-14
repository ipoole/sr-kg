"""Domain-owned, named SVG illustrations embedded once in a generated viewer."""
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from srkg.domain_references import domain_namespace
from srkg.schema import KnowledgeBaseLoadError


@dataclass(frozen=True)
class Figure:
    figure_id: str
    svg: str
    caption: str
    alt: str

    def to_viewer_data(self):
        return dict(svg=self.svg, caption=self.caption, alt=self.alt)


def load_figures(table, *, include_svg=True):
    if table is None:
        return {}
    required = {'figure_id', 'svg_path', 'caption', 'alt', '_asset_root'}
    if not required <= set(table.columns):
        raise KnowledgeBaseLoadError('Figure table needs figure_id, svg_path, caption and alt columns')
    figures = {}
    for row in table.to_dict('records'):
        figure_id = str(row['figure_id']).strip()
        domain_namespace(figure_id, 'figure')
        if figure_id in figures:
            raise KnowledgeBaseLoadError(f'Duplicate figure ID: {figure_id}')
        root = Path(row['_asset_root']).resolve()
        relative = Path(str(row['svg_path']))
        if relative.is_absolute():
            raise KnowledgeBaseLoadError(f'{figure_id}: SVG path must be relative to its domain')
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise KnowledgeBaseLoadError(f'{figure_id}: SVG path escapes owning domain')
        if path.suffix.lower() != '.svg' or not str(row['alt']).strip():
            raise KnowledgeBaseLoadError(f'{figure_id}: needs an SVG file and descriptive alt text')
        try:
            svg = path.read_text(encoding='utf-8')
            element = ElementTree.fromstring(svg)
            if element.tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError('expected an SVG document')
        except (OSError, ValueError, ElementTree.ParseError) as exc:
            raise KnowledgeBaseLoadError(f'{figure_id}: could not load SVG: {exc}') from exc
        figures[figure_id] = Figure(figure_id, svg if include_svg else '',
                                    str(row['caption']).strip(), str(row['alt']).strip())
    return figures
