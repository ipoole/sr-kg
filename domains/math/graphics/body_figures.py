"""Deterministic MATHS body illustrations, separate from canonical concept art.

Rebuild with: conda run -n sr-kg python -m domains.math.graphics.body_figures
"""
from html import escape
from math import cos, pi, sin
from pathlib import Path
from srkg.svg_graphics.primitives import (
    _arrow_marker, _circle, _line, _path, _polyline, _rect, _text,
)

BLUE='#2056b5'
GOLD='#ae6b16'
GREEN='#438774'
INK='#293f51'
MUTED='#63788a'
RED='#bd443e'


def text(x,y,label,size=27,colour=INK,anchor='middle'):
    return _text(x,y,escape(label),font_size=size,fill=colour,text_anchor=anchor)


def line(x1,y1,x2,y2,colour=BLUE,width=3,**attrs):
    return _line(x1,y1,x2,y2,stroke=colour,stroke_width=width,stroke_linecap='round',**attrs)


def canvas(title,body,defs=()):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" width="900" height="560">\n'
            '<title>'+escape(title)+'</title>\n<defs>'+''.join(defs)+'</defs>\n'
            '<g font-family="Arial, sans-serif">\n'+'\n'.join(body)+'\n</g>\n</svg>\n')


def overlapping_charts():
    def ground(x,y):
        z=.35*cos(1.2*x)*cos(y)+.25
        return 250+100*x+40*y,340+55*y-90*z
    body=[text(450,42,'One ground peg, two coordinate records',30),
          text(250,115,'Curved ground surface M',28,GREEN)]
    # The two chart domains are overlapping discs in the parameter plane,
    # drawn on one smooth terrain patch. Coordinate images are shown separately.
    for centre,colour in [(-.5,BLUE),(.5,GOLD)]:
        pts=[ground(centre+cos(i*pi/40),sin(i*pi/40)) for i in range(81)]
        body.append(_polyline(pts,fill=colour,fill_opacity='.13',stroke=colour,stroke_width=2))
    for i in range(9):
        x=-1.6+i*.4
        body.append(_polyline([ground(x,-1+2*j/40) for j in range(41)],fill='none',stroke='#aac7bd',stroke_width=1.5))
    for i in range(7):
        y=-1+i/3
        body.append(_polyline([ground(-1.6+3.2*j/60,y) for j in range(61)],fill='none',stroke='#aac7bd',stroke_width=1.5))
    px,py=ground(0,0)
    body += [_circle(px,py,9,fill=RED),text(px-18,py-15,'p',30,RED),
             text(135,333,'U',30,BLUE),text(377,334,'V',30,GOLD),
             text(250,422,'p lies in both chart domains',25,MUTED),
             _rect(570,70,310,208,rx=15,fill='#f7faff',stroke='#c9d9ed'),
             _rect(570,305,310,220,rx=15,fill='#fffcf5',stroke='#e3d4bc'),
             text(725,102,'Board A: coordinate image',24,BLUE),
             text(725,337,'Board B: coordinate image',24,GOLD)]
    for x in [600,650,700,750,800,850]:body.append(line(x,125,x,250,'#d6e1ef',1))
    for y in [130,180,230]:body.append(line(590,y,860,y,'#d6e1ef',1))
    body += [line(650,250,650,125,BLUE,2),line(590,230,860,230,BLUE,2),
             _circle(750,180,7,fill=RED),text(755,158,'p: (2, 1)',25,RED),
             text(855,259,'x¹',24,BLUE),text(631,130,'x²',24,BLUE),
             text(700,252,'1',18,MUTED),text(750,252,'2',18,MUTED)]
    # The second straight grid is oblique. Its drawn point has labels (5,-1).
    def board(u,v):return 650+32*u+15*v,380-35*v
    for u in range(-1,7):body.append(line(*board(u,-2),*board(u,1),colour='#e6d7bd',width=1))
    for v in [-2,-1,0,1]:body.append(line(*board(-1,v),*board(6,v),colour='#e6d7bd',width=1))
    body += [line(*board(-1,0),*board(6,0),colour=GOLD,width=2),
             line(*board(0,-2),*board(0,1),colour=GOLD,width=2),
             _circle(*board(5,-1),7,fill=RED),text(785,461,'p: (5, −1)',25,RED),
             text(853,372,'y¹',24,GOLD),text(644,357,'y²',24,GOLD)]
    for x,y,colour in [(750,180,BLUE),(795,415,GOLD)]:
        body.append(line(px+10,py,x-12,y,colour,2,stroke_dasharray='7 7'))
    body += [text(275,498,'Only the labels change.',27),
             text(275,533,'Neither picture flattens the ground.',23,MUTED)]
    return canvas('A peg in overlapping surface charts has two sets of board coordinates',body)


def contour_readout():
    defs=[_arrow_marker('velocity-v',colour=BLUE,size=6),_arrow_marker('velocity-w',colour=GOLD,size=6),
          '<clipPath id="contour-window"><rect x="35" y="105" width="480" height="340"/></clipPath>']
    def point(x,y):return 230+240*x,390-240*y
    body=[text(450,42,'A temperature differential reads a direction',30),
          _rect(20,80,510,385,rx=18,fill='#f8fcfa',stroke='#cedfd6'),
          _rect(550,80,330,385,rx=18,fill='#f7faff',stroke='#cedbec'),
          '<g clip-path="url(#contour-window)">']
    for k in [-2,-1,0,1,2]:
        body.append(line(*point(-1,-2-k),*point(1.3,2.6-k),GREEN,2.5))
    body += ['</g>']
    for k in [-2,-1,0,1]:
        x=(k+(390-132)/240)/2
        body.append(text(*point(x,(390-132)/240),('T₀' if k==0 else 'T₀'+('+' if k>0 else '−')+str(abs(k))),23,GREEN))
    px,py=point(0,0)
    body += [line(*point(-.6,0),*point(1.1,0),MUTED,1.5),
             line(*point(0,-.2),*point(0,1.1),MUTED,1.5),
             line(px,py,*point(.5,.2),width=5,marker_end='url(#velocity-v)'),
             line(px,py,*point(.3,.6),GOLD,5,marker_end='url(#velocity-w)'),
             _circle(px,py,7,fill=RED),text(px-18,py+25,'p',27,RED),
             text(368,335,'v',31,BLUE),text(316,235,'w',31,GOLD),
             text(497,411,'x¹',24,MUTED),text(211,117,'x²',24,MUTED),
             text(715,122,'At the same point p',26),
             text(715,166,'derivatives: (2, −1) K/m',24),
             text(715,220,'v = (0.5, 0.2) m/s',26,BLUE),
             text(715,262,'dT(v) = 0.8 K/s',30,BLUE),
             text(715,327,'w = (0.3, 0.6) m/s',26,GOLD),
             text(715,369,'dT(w) = 0',30,GOLD),
             text(715,426,'w follows an isotherm',24,MUTED),
             text(450,507,'Crossing contours changes T; following one gives zero first-order change.',23),
             text(450,548,'A local coordinate picture: no metric or steepest-direction arrow is assumed.',22,MUTED)]
    return canvas('Temperature contours and two tangent velocities give different covector readouts at one point',body,defs)


def reciprocal_components():
    defs=[_arrow_marker('same-vector',colour=BLUE,size=6)]
    body=[text(450,42,'Change the component numbers, keep the readout',30)]
    for left,origin,divisions,header,omega in [(20,100,3,'x coordinates',8),
                                             (460,540,6,'x′ = 2x coordinates',4)]:
        centre=left+210
        body += [_rect(left,75,420,415,rx=18,fill='#f7faff',stroke='#ccdced'),
                 text(centre,118,header,28),text(centre,176,'V',36,BLUE),
                 line(origin,210,origin+270,210,width=6,marker_end='url(#same-vector)'),
                 _circle(origin,210,7,fill=RED),text(origin-20,229,'p',27,RED),
                 line(origin,285,origin+270,285,MUTED,2)]
        for i in range(divisions+1):
            x=origin+270*i/divisions
            body += [line(x,277,x,293,MUTED,2),text(x,324,str(i),25,MUTED)]
        body += [text(centre,375,f'vector component: {divisions}',27,BLUE),
                 text(centre,420,('ωₓ = ' if divisions==3 else 'ωₓ′ = ')+str(omega),30,GOLD),
                 text(centre,464,f'ω(V) = {omega} × {divisions} = 24',28)]
    body += [text(450,528,'The new basis unit is half as large; its covector readout halves too.',24,MUTED)]
    return canvas('The same vector and covector pairing under a one-dimensional coordinate rescaling',body,defs)


def write_assets():
    output=Path(__file__).with_name('figures');output.mkdir(exist_ok=True)
    for name,build in {'overlapping_charts':overlapping_charts,'contour_readout':contour_readout,
                       'reciprocal_components':reciprocal_components}.items():
        (output/(name+'.svg')).write_text(build(),encoding='utf-8')


if __name__=='__main__':write_assets()
