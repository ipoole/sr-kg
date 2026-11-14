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


def varied_histories():
    from math import pi, sin
    body = [text(450, 43, 'Nearby paths, no first-order action change', 30)]
    for left in (20, 460):
        body.append(_rect(left, 80, 420, 390, rx=18, fill='#f8fbff', stroke='#cfdaea'))
    def point(t, q): return 85+285*t, 400-240*q
    body += [line(*point(0, 0), *point(1.08, 0), MUTED, 2),
             line(*point(0, 0), *point(0, 1.14), MUTED, 2),
             text(390, 430, 't / T', 25, MUTED), text(64, 120, 'q / d', 25, MUTED)]
    for a, colour in [(.23,GOLD),(-.23,GREEN),(0,BLUE)]:
        body.append(_polyline([point(i/60, i/60+a*sin(pi*i/60)) for i in range(61)],
                              fill='none', stroke=colour, stroke_width=4))
    for t in (0,1):body.append(_circle(*point(t,t),7,fill=RED))
    body += [text(220, 452, 'Same endpoints and duration', 24),
             text(670, 125, 'S / S₀', 27)]
    def graph(a, s): return 670+300*a, 405-245*(s-.9)
    body += [line(*graph(-.48,.9),*graph(.48,.9), MUTED,2),
             line(*graph(0,.9),*graph(0,1.85), MUTED,2),
             _polyline([graph(a,1+pi*pi*a*a/2) for a in [-.38+i*.76/80 for i in range(81)]],
                       fill='none',stroke=BLUE,stroke_width=4),
             _circle(*graph(0,1),7,fill=RED),text(670,445,'0',23,MUTED),
             text(795,445,'a / d',25,MUTED),text(715,335,'zero slope',25,BLUE),
             text(450,530,'A free-particle example: a minimum here, not a general minimum rule.',24)]
    return canvas('Smooth fixed-endpoint variations around a straight free-particle history',body)


def field_action_cells():
    body = [text(450, 43, 'A field history contributes throughout spacetime', 30),
            text(260, 102, 'One spatial dimension; c = 1', 26),
            line(75,425,465,425,MUTED,2),line(75,425,75,145,MUTED,2),
            text(482,433,'x',27,MUTED),text(57,140,'t',27,MUTED)]
    for i in range(5):
        for j in range(4):
            x,y=100+65*i,155+60*j
            fill='#e4eef9' if (i+j)%3 else '#edf6ee'
            if (i,j) in [(2,2),(3,2)]:fill='#f7e5c8'
            body += [_rect(x,y,65,60,fill=fill,stroke='#abbdd0',stroke_width=1),
                     _circle(x+32.5,y+30,4,fill=BLUE)]
    body += [line(262,305,327,305,GOLD,5),
             text(270,475,'A spatial difference uses neighbours',23,GOLD),
             _rect(530,125,350,350,rx=18,fill='#f8fbff',stroke='#cfdaea'),
             text(705,179,'Local contribution',27),text(705,232,'ℒ × Δt Δx',34,BLUE),
             text(705,307,'Add over all cells',27),text(705,359,'S ≈ Σ ℒ Δt Δx',31,BLUE),
             text(705,430,'per unit transverse area',23,MUTED),
             text(450,535,'The grid is a calculation aid, not a physical spacetime lattice.',25)]
    return canvas('Sampling a trial scalar-field history to approximate its local action integral',body)


def observer_field_split():
    defs = [_arrow_marker('electric', colour=BLUE, size=6)]
    body = [text(450,43,'One field, different electric and magnetic readings',29)]
    for left, frame, length in [(20,'S',135),(460,'S′ moving at +0.6c',168.75)]:
        cx, cy = left+160, 325
        body += [_rect(left,80,420,390,rx=18,fill='#f8fbff',stroke='#cfdaea'),
                 text(left+210,122,frame,28),
                 line(cx-45,cy,cx+120,cy,MUTED,1.5),line(cx,cy+20,cx,cy-185,MUTED,1.5),
                 line(cx,cy,cx,cy-length,BLUE,6,marker_end='url(#electric)'),
                 text(cx+30,cy-length+10,'E' if left==20 else 'E′',30,BLUE,anchor='start'),
                 text(left+210,413,'E = E₀; B = 0' if left==20 else 'E′ = 1.25E₀; cB′ = −0.75E₀',25)]
        if left==460:
            bx,by=left+315,240
            body += [_circle(bx,by,24,fill='none',stroke=GOLD,stroke_width=3),
                     line(bx-12,by-12,bx+12,by+12,GOLD,3),line(bx-12,by+12,bx+12,by-12,GOLD,3),
                     text(bx,by+64,'B′ into page',22,GOLD)]
        body += [text(cx+124,cy+28,'x′' if left==460 else 'x',23,MUTED),
                 text(cx-24,cy-187,'y′' if left==460 else 'y',23,MUTED)]
    body += [text(450,530,'Both descriptions: E² − c²B² = E₀²',29)]
    return canvas('Electric and magnetic field readings under a transverse Lorentz boost',body,defs)


def gauge_representatives():
    defs=[_arrow_marker('potential',colour=BLUE,size=5)]
    body=[text(450,43,'Different potentials, the same magnetic field',30)]
    for left,formula in [(20,'A₁ = (−By/2, Bx/2, 0)'),(460,'A₂ = (0, Bx, 0)')]:
        cx,cy=left+210,285
        body += [_rect(left,80,420,390,rx=18,fill='#f8fbff',stroke='#cfdaea'),
                 text(cx,124,formula,27),line(cx-150,cy,cx+150,cy,MUTED,1),
                 line(cx,cy+115,cx,cy-115,MUTED,1)]
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                px,py=cx+85*x,cy-75*y
                vx,vy=(-y/2,x/2) if left==20 else (0,x)
                body.append(_circle(px,py,3,fill=BLUE))
                if vx or vy:
                    body.append(line(px,py,px+48*vx,py-48*vy,BLUE,3,marker_end='url(#potential)'))
        for dx,dy in [(-155,-95),(155,-95),(-155,95),(155,95)]:
            px,py=cx+dx,cy+dy
            body += [_circle(px,py,13,fill='none',stroke=GOLD,stroke_width=2),_circle(px,py,3,fill=GOLD)]
        body.append(text(cx,440,'curl A = B ẑ',28,GOLD))
    body += [text(450,530,'Blue: potential arrows. Gold: magnetic field out of the page.',25)]
    return canvas('Two gauge-related vector potentials with the same uniform magnetic field',body,defs)


def translation_symmetry():
    from math import pi,sin
    body=[text(450,43,'A sideways shift leaves this model unchanged',30)]
    for left,shift,header in [(20,0,'One trial history'),(460,55,'Shift the whole history')]:
        body += [_rect(left,80,420,365,rx=18,fill='#f8fbff',stroke='#cfdaea'),text(left+210,123,header,26)]
        for y in [170,210,250,290,330,370]:
            body.append(_rect(left+20,y,380,40,fill='#eaf1f8' if y in [170,370] else '#f5f8fc',stroke='none'))
        points=[(left+45+shift+240*t,285-75*sin(2*pi*t)) for t in [i/80 for i in range(81)]]
        body += [_polyline(points,fill='none',stroke=BLUE,stroke_width=4),
                 _circle(*points[0],6,fill=RED),_circle(*points[-1],6,fill=RED),
                 text(left+210,429,'Same V(y), no x dependence',24,MUTED)]
    body += [text(450,491,'∂L/∂x = 0  ⇒  pₓ = mẋ is constant',29,BLUE),
             text(450,535,'The transverse force changes pᵧ; horizontal momentum stays fixed.',24)]
    return canvas('Translation symmetry of a particle model with a transverse harmonic potential',body)


def charge_flux():
    defs=[_arrow_marker('incoming',colour=BLUE,size=6),_arrow_marker('outgoing',colour=GOLD,size=6)]
    body=[text(450,43,'More charge leaves than enters',32),
          _rect(245,135,410,230,rx=18,fill='#f8fbff',stroke=MUTED,stroke_width=2),
          text(450,182,'Fixed region',28),text(450,247,'10 C → 8 C',36),
          text(450,301,'after one second',26),
          line(50,250,225,250,BLUE,6,marker_end='url(#incoming)'),
          line(675,250,850,250,GOLD,6,marker_end='url(#outgoing)'),
          text(130,204,'3 A in',29,BLUE),text(770,204,'5 A out',29,GOLD),
          text(450,408,'No charge flux through the other faces',25,MUTED),
          text(450,474,'dQ/dt = 3 − 5 = −2 C/s',32),
          text(450,531,'Positive net outward current means decreasing enclosed charge.',25)]
    return canvas('Charge accumulation in a fixed region balances incoming and outgoing currents',body,defs)


BUILDERS = {'interval_components': interval_components, 'rod_slices': rod_slices,
            'emission_energy': emission_energy,
            'varied_histories': varied_histories, 'field_action_cells': field_action_cells,
            'observer_field_split': observer_field_split, 'gauge_representatives': gauge_representatives,
            'translation_symmetry': translation_symmetry, 'charge_flux': charge_flux}


def write_assets():
    output = Path(__file__).with_name('figures')
    output.mkdir(exist_ok=True)
    for name, build in BUILDERS.items():
        (output/(name+'.svg')).write_text(build(), encoding='utf-8')


if __name__ == '__main__':
    write_assets()
