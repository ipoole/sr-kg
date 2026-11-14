"""Rebuild the GR teaching figures registered in data/figures.csv.

Run with: conda run -n sr-kg python -m domains.gr.graphics.body_figures
These are body illustrations, not replacements for concept icons or graphics.
"""
from html import escape
from math import cos, pi, sin
from pathlib import Path

BLUE = '#2056b5'
GOLD = '#b56d12'
INK = '#273d50'
MUTED = '#617487'


def _text(x, y, value, size=26, colour=INK, anchor='middle'):
    return (f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
            f'font-size="{size}" fill="{colour}">{escape(value)}</text>')


def _line(x1, y1, x2, y2, colour=BLUE, width=4, extra=''):
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{colour}" stroke-width="{width}" stroke-linecap="round" {extra}/>')


def _circle(x, y, radius=8, colour=BLUE):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{colour}"/>'


def _svg(title, body, defs=''):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" '
            'width="900" height="560">\n<title>'+escape(title)+'</title>\n'
            '<defs>'+defs+'</defs>\n<g font-family="Arial, sans-serif">\n'+
            '\n'.join(body)+'\n</g>\n</svg>\n')


def tidal_constellation():
    """Short-time point-mass tides in a comoving lab; show one spatial slice.

    With eps = GM dt²/(2 r³), displacements scale as x(1+2 eps),
    y(1-eps). The laboratory is small compared with r; eps is exaggerated.
    """
    marker = ('<marker id="tidal-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
              'markerWidth="6" markerHeight="6" orient="auto">'
              f'<path d="M0 0L10 5L0 10Z" fill="{GOLD}"/></marker>')
    body = [_text(450, 45, 'One freely falling laboratory', 30)]
    for left in (20, 460):
        body.append(f'<rect x="{left}" y="70" width="420" height="330" rx="20" '
                    'fill="#f7faff" stroke="#d4e0ec" stroke-width="2"/>')
    body += [_text(230, 112, 'Released at rest together', 25),
             _text(670, 112, 'A short time later', 25)]
    radius, eps, cy = 88, .2, 252
    for cx in (230, 670):
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
                    'stroke="#acb9c9" stroke-width="2" stroke-dasharray="7 7"/>')
        body.append(_circle(cx, cy, 6, INK))
    body.append(f'<ellipse cx="670" cy="{cy}" rx="{radius*(1+2*eps)}" '
                f'ry="{radius*(1-eps)}" fill="none" stroke="#bcd0e6" stroke-width="2"/>')
    for i in range(8):
        angle = i*pi/4
        dx, dy = radius*cos(angle), radius*sin(angle)
        body.append(_circle(230+dx, cy+dy))
        body.append(_circle(670+dx*(1+2*eps), cy+dy*(1-eps)))
    # On the initial cloud, arrows show differential acceleration relative
    # to its centre, not the inward gravitational acceleration of the lab.
    for dx, dy in [(radius, 0), (-radius, 0), (0, radius), (0, -radius)]:
        body.append(_line(230+dx, cy+dy, 230+dx*1.48, cy+dy*.68,
                          colour=GOLD, extra='marker-end="url(#tidal-arrow)"'))
    body += [_text(230, 435, 'Arrows: relative acceleration', 24, GOLD),
             _text(670, 435, 'Radial stretch, transverse squeeze', 24, BLUE),
             _line(320, 482, 580, 482, colour=MUTED, width=3),
             _line(320, 482, 333, 474, colour=MUTED, width=3),
             _line(320, 482, 333, 490, colour=MUTED, width=3),
             _line(580, 482, 567, 474, colour=MUTED, width=3),
             _line(580, 482, 567, 490, colour=MUTED, width=3),
             _text(450, 518, 'Radial direction — common fall removed', 25, MUTED)]
    return _svg('Tidal deformation of a released particle constellation', body, marker)


def write_assets():
    output = Path(__file__).with_name('figures')
    output.mkdir(exist_ok=True)
    for name, build in {'tidal_constellation': tidal_constellation}.items():
        (output/(name+'.svg')).write_text(build(), encoding='utf-8')


if __name__ == '__main__':
    write_assets()
