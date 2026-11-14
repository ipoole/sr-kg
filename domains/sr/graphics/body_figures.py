"""Deterministic SR teaching figures, separate from canonical concept artwork.

Rebuild: conda run -n sr-kg python -m domains.sr.graphics.body_figures
"""
from html import escape
from pathlib import Path
from srkg.svg_graphics.primitives import _arrow_marker, _circle, _line, _path, _polyline, _rect, _text

BLUE = '#2056b5'
GOLD = '#ae6b16'
GREEN = '#33816f'
INK = '#293f51'
MUTED = '#63788a'
RED = '#bd443e'


def text(x, y, label, size=27, colour=INK, anchor='middle'):
    return _text(x, y, escape(label), font_size=size, fill=colour, text_anchor=anchor)


def line(x1, y1, x2, y2, colour=BLUE, width=3, **attrs):
    return _line(x1, y1, x2, y2, stroke=colour, stroke_width=width, stroke_linecap='round', **attrs)


def canvas(title, body, defs=()):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" width="900" height="560">\n'
            '<title>'+escape(title)+'</title>\n<defs>'+''.join(defs)+'</defs>\n'
            '<g font-family="Arial, sans-serif">\n'+'\n'.join(body)+'\n</g>\n</svg>\n')


def interval_components():
    body = [text(450, 43, 'One event pair, two coordinate descriptions', 30)]
    # The frames are related by beta=.6; lengths are in metres, time as ct.
    for left, label, dt, dx in [(20, 'S: Δct = 5 m, Δx = 3 m', 5, 3),
                                (460, 'S′: Δct′ = 4 m, Δx′ = 0', 4, 0)]:
        ox, oy, scale = left+90, 405, 48
        body += [_rect(left, 76, 420, 405, rx=18, fill='#f8fbff', stroke='#cfdaea'),
                 text(left+210, 115, label, 25),
                 line(ox, oy, ox+255, oy, MUTED, 2), line(ox, oy, ox, oy-265, MUTED, 2),
                 text(ox+256, oy+30, 'x′' if dx==0 else 'x', 25, MUTED),
                 text(ox-25, oy-266, 'ct′' if dx==0 else 'ct', 25, MUTED),
                 line(ox, oy, ox+dx*scale, oy-dt*scale, BLUE, 5),
                 _circle(ox, oy, 7, fill=RED), _circle(ox+dx*scale, oy-dt*scale, 7, fill=RED),
                 text(ox-20, oy+25, 'A', 25, RED),
                 text(ox+dx*scale+20, oy-dt*scale-10, 'B', 25, RED),
                 text(left+210, 455, '25 − 9 = 16 m²' if dx else '16 − 0 = 16 m²', 29, BLUE)]
    body += [text(450, 530, 'A and B are unchanged. Their coordinate components are not.', 25)]
    return canvas('Two frames give the same interval square for one fixed pair of events', body)


def rod_slices():
    def point(x, ct): return 85+65*x, 430-65*ct
    body = [text(450, 43, 'A length measurement chooses an event pair', 30),
            text(300, 95, 'Rod at rest in S′; moving at 0.6c in S', 25)]
    for x0 in [0, 3.2]:
        body.append(line(*point(x0, 0), *point(x0+2.4, 4), MUTED, 4))
    body += [line(*point(-.3, 0), *point(6, 0), BLUE, 3),
             line(*point(0, 0), *point(6, 3.6), GOLD, 3)]
    for label, x, ct, dx, dy in [('A',0,0,-20,32),('B',3.2,0,0,32),('C',5,3,22,-10)]:
        px, py = point(x, ct)
        body += [_circle(px, py, 8, fill=RED), text(px+dx, py+dy, label, 27, RED)]
    body += [text(250, 490, 'A–B: simultaneous in S', 25, BLUE),
             text(350, 148, 'A–C: simultaneous in S′', 25, GOLD),
             _rect(540, 95, 340, 365, rx=18, fill='#f8fbff', stroke='#cfdaea'),
             text(710, 148, 'Rest length', 28, GOLD), text(710, 190, 'L₀ = 4 m', 33, GOLD),
             text(710, 260, 'Moving-frame length', 25, BLUE), text(710, 305, 'L = 3.2 m', 33, BLUE),
             text(710, 380, 'γ = 1.25', 27), text(710, 422, 'L = L₀ / γ', 29),
             text(450, 535, 'Different simultaneity slices, not a mechanically squashed rod.', 25)]
    return canvas('Two simultaneity slices select different endpoint events on a moving rod', body)


def emission_energy():
    defs = [_arrow_marker('pulse-left', colour=BLUE, size=6),
            _arrow_marker('pulse-right', colour=GOLD, size=6)]
    body = [text(450, 43, 'Light leaves without a kick', 32)]
    for left, header, eleft, eright, total in [
            (20, 'Body rest frame S', 'L / 2', 'L / 2', 'Energy out: L'),
            (460, 'S′: boost at −0.6c', 'L / 4', 'L', 'Energy out: 1.25L')]:
        cx = left+210
        body += [_rect(left, 80, 420, 350, rx=18, fill='#f8fbff', stroke='#cfdaea'),
                 text(cx, 125, header, 28),
                 _rect(cx-37, 202, 74, 74, rx=12, fill='#e7edf4', stroke=MUTED, stroke_width=2),
                 text(cx, 248, 'body', 22),
                 line(cx-58, 239, left+40, 239, BLUE, 5, marker_end='url(#pulse-left)'),
                 line(cx+58, 239, left+380, 239, GOLD, 5, marker_end='url(#pulse-right)'),
                 text(left+82, 194, eleft, 32, BLUE), text(left+338, 194, eright, 32, GOLD),
                 text(cx, 330, total, 30),
                 text(cx, 387, 'No change in body velocity', 24, MUTED)]
    body += [text(450, 482, 'Extra loss in S′ is lost kinetic energy: 0.25L.', 28),
             text(450, 530, 'Same emission; different observers’ energy accounts.', 25, MUTED)]
    return canvas('Opposite light pulses have different total energies in two inertial frames', body, defs)


BUILDERS = {'interval_components': interval_components, 'rod_slices': rod_slices,
            'emission_energy': emission_energy}


def write_assets():
    output = Path(__file__).with_name('figures')
    output.mkdir(exist_ok=True)
    for name, build in BUILDERS.items():
        (output/(name+'.svg')).write_text(build(), encoding='utf-8')


if __name__ == '__main__':
    write_assets()
