"""Figures: lining and tabular (every figure one width, so columns of
numbers and clocks don't shift). The zero is plain, told from O by its
narrow oval (O is half as wide again)."""

import copy
import math

from engine import direction, ellipse, mul, sub
from glyph import Master, ends, glyph, shaped
from parts import bar, bottom_line, part_of, place, point_of, quarter, ring, stem, through

FIGURES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def F(name, *unicodes):
    return glyph(name, *unicodes, upper=True)


def tab(P):
    """the figures' one width (the family's, where it has one; smaller for
    small figures)"""
    width = P.target([0x30]) if hasattr(P, "target") else None
    return (width or P.t(548, 560, 648)) * P.C / Master.C


def fig_nib(g):
    return g.nib.scaled(0.97)


def top(P):
    return P.C + P.uov - P.ub * 0.97


def bottom(P):
    return -P.uov + P.ub * 0.97


def figure_width(P):
    """the outline's width, inside the tabular width"""
    import glyph as G
    return P.cw(300) * G.STYLE.figures + 2 * P.ustem


@F("zero", 0x30)
def zero(g):
    P = g.P
    import glyph as G
    w = figure_width(P) - P.cw(14)
    ring(g, 0, w, bottom(P), top(P), k=shaped(0.6, (P.ks - 0.04, P.kt + 0.07)))
    if G.STYLE.mono:
        # a dot inside, so 0 isn't O in a font where both are one width:
        # an upright oval, which stays clear at text sizes, where a round
        # dot shrinks to a speck; no bigger than a share of the counter, so
        # heavy weights keep room round it
        from engine import bounds
        inner = min(g.strokes[-1].outline(), key=lambda c: abs(bounds([c])[2] - bounds([c])[0]))
        x0, y0, x1, y1 = bounds([inner])
        rx = min(P.ustem * 0.5, (x1 - x0) * 0.2)
        ry = min(P.ustem * 1.15, (y1 - y0) * 0.3)
        g.shape(ellipse(w / 2, P.C / 2, rx, ry))
    g.fixed(tab(P))


@F("one", 0x31)
def one(g):
    """a flag, and a foot: with the l's tail and the plain I, the three
    can't be taken for one another, and the foot fills the figure's width"""
    P = g.P
    nib = fig_nib(g)
    w = tab(P) - 2 * P.t(64, 62, 52) * P.C / Master.C
    xs = w * 0.54
    import glyph as G
    stem(g, xs, 0, P.C, nib=nib)
    if G.STYLE.one_foot and G.STYLE.mono:
        from lower import mono_slab
        mono_slab(g, w * 0.14, w * 0.94, 0, top=False, upper=True)
    elif G.STYLE.one_foot:
        bar(g, w * 0.14, w * 0.94, nib.b * 0.96, s=0.96, nib=nib)
    # the flag leaves the stem a little below its top, down to the left
    d = direction(210)
    n = (d[1], -d[0])  # the normal on the flag's upper side
    edge = (xs - nib.a, P.C - P.ustem * 0.78)
    off = nib.half(n)
    c = (edge[0] - n[0] * off, edge[1] - n[1] * off)  # a point on its centre line
    k0 = (xs - c[0]) / d[0]
    start = (c[0] + d[0] * k0, c[1] + d[1] * k0)
    length = P.cw(205) + P.ustem * 0.4
    end = (start[0] + d[0] * length, start[1] + d[1] * length)
    through(g, start, end, s0=1.0, s1=0.92, nib=nib, cap0=90, cap1=None)
    # centred on its foot (and stem), whatever the flag reaches; with no
    # foot, the stem a little right of the middle
    if G.STYLE.one_foot:
        g.fixed(tab(P), centre=max(0.0, (w * 0.14 - (end[0] - nib.a * 0.5)) / 2))
    else:
        bw = xs + nib.a - (end[0] - nib.a * 0.6)
        g.fixed(tab(P), centre=0.05 * tab(P) - (bw / 2 - nib.a))


@F("two", 0x32)
def two(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P)
    a, b = nib.a, nib.b
    yt = top(P)
    xr = w - a
    cx = w * 0.48
    s = g.stroke((a * 1.05 + P.cw(10), P.C * 0.76), nib=nib, **ends(18))
    s.to((cx, yt), 64, 0, k=(0.40, 0.55))
    s.arc((xr, P.C * 0.68), "h", k=(0.6, 0.56))
    s.to((a * 1.25 + P.cw(4), b * 0.96), 270, 224, k=(0.34, 0.48), s=1.0)
    s.end(cap=0)
    bar(g, 0, w + P.cw(8), b * 0.96, s=0.96, nib=nib)
    g.fixed(tab(P))


@F("three", 0x33)
def three(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P)
    a = nib.a
    yt, yb = top(P), bottom(P)
    ym = P.C * 0.555
    cx = w * 0.47
    xr1, xr2 = w - a * 1.08 - w * 0.03, w - a
    s = g.stroke((a + P.cw(14), P.C * 0.80), nib=nib, **ends(18))
    s.to((cx, yt), 60, 0, k=(0.40, 0.55))
    s.arc((xr1, (yt + ym) / 2), "h", k=0.58, s=1.0)
    s.arc((cx - w * 0.06, ym), "v", k=(0.58, 0.62), s=0.94)
    s.line((cx - w * 0.16, ym), s=0.94)
    t = g.stroke((cx - w * 0.12, ym), nib=nib, s=0.94)
    t.line((cx - w * 0.02, ym), s=0.94)
    t.arc((xr2, (ym + yb) / 2), "h", k=0.6, s=1.0)
    t.arc((cx - w * 0.04, yb), "v", k=0.6, s=1.0)
    t.to((a * 0.95, P.C * 0.16), 180, 140, k=(0.46, 0.3))
    t.end(**ends(18))
    g.fixed(tab(P))


@F("four", 0x34)
def four(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P) + P.cw(30)
    xs = w - nib.a - P.cw(70)
    yb = P.C * 0.27
    stem(g, xs, 0, P.C, nib=nib)
    bar(g, 0, w, yb, s=0.94, nib=nib)
    dn = nib.scaled(0.92)
    c0, c1 = place(dn, (0, yb), (xs + nib.a, P.C), -1, 1)
    through(g, c0, c1, nib=dn)
    g.fixed(tab(P))


@F("five", 0x35)
def five(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P)
    a, b = nib.a, nib.b
    yb = bottom(P)
    xv = a + P.cw(26)
    bar(g, xv - a * 0.9, w - P.cw(6), P.C - b * 0.96, s=0.96, nib=nib)
    yj = P.C * 0.56
    top_b = P.C * 0.64 - b
    xr = w - a
    cx = w * 0.48
    # the bowl starts at the upright's right edge, cut upright against it
    s = g.stroke((xv + a * 0.8, yj), s=P.join + 0.1, nib=nib, cap=90)
    s.to((cx, top_b), 22, 0, k=(0.4, 0.5), s=1.0)
    s.arc((xr, (top_b + yb) / 2), "h", k=0.6, s=1.03)
    s.arc((cx - w * 0.03, yb), "v", k=0.6, s=1.0)
    s.to((a * 0.95, P.C * 0.15), 180, 140, k=(0.46, 0.3))
    s.end(**ends(18))
    # the upright, leaning a little, into the bowl: its foot cut along the
    # bowl's underside where the two meet, so they run on with no step
    x1, x2 = xv + a, xv + a + 3  # (its slope right there)
    y1, y2 = underside(s.outline(), x1, yj), underside(s.outline(), x2, yj)
    slope = (y2 - y1) / (x2 - x1)
    xf = xv + a * 0.04
    yf = y1 + (xf - x1) * slope
    cut = math.degrees(math.atan(slope))
    through(g, (xf, yf), (xv + P.cw(10), P.C - b * 0.96), nib=nib, cap0=cut, cap1=None)
    g.fixed(tab(P))


def underside(contours, x, near):
    """the lowest point of an outline at x, of the part within a stem's
    reach of the height near (the underside of a stroke there)"""
    best = None
    for c in contours:
        for seg in c:
            pts = [seg[1], seg[2]] if seg[0] == "L" else [seg[1], seg[2], seg[3], seg[4]]
            prev = None
            for i in range(201):
                t = i / 200
                if seg[0] == "L":
                    q = (pts[0][0] + (pts[1][0] - pts[0][0]) * t, pts[0][1] + (pts[1][1] - pts[0][1]) * t)
                else:
                    u = 1 - t
                    q = tuple(u ** 3 * pts[0][k] + 3 * u * u * t * pts[1][k] + 3 * u * t * t * pts[2][k]
                              + t ** 3 * pts[3][k] for k in (0, 1))
                if prev and (prev[0] - x) * (q[0] - x) <= 0 and prev[0] != q[0]:
                    y = prev[1] + (q[1] - prev[1]) * (x - prev[0]) / (q[0] - prev[0])
                    if abs(y - near) < 200 and (best is None or y < best):
                        best = y
                prev = q
    return near if best is None else best


def six_like(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P)
    a = nib.a
    yt, yb = top(P), bottom(P)
    yr = P.C * 0.63 - nib.b * 0.97  # the bowl's top
    ring(g, 0, w, yb, yr, k=0.6)
    xl = a * 1.04
    cyr = (yb + yr) / 2
    s = g.stroke((xl, cyr), nib=nib, s=1.04)
    s.line((xl, P.C * 0.42), s=1.04)
    s.to((w * 0.56, yt), 90, 0, k=(0.42, 0.52), s=1.0)
    s.to((w - a * 1.1 - P.cw(8), P.C * 0.86), 0, -38, k=(0.42, 0.3), s=0.98)
    s.end(**ends(18))
    return w


@F("six", 0x36)
def six(g):
    six_like(g)
    g.fixed(tab(g.P))


@F("nine", 0x39)
def nine(g):
    P = g.P
    w = six_like(g)
    # turn every stroke and shape half round about the figure's middle
    cx, cy = w / 2, P.C / 2
    turn = lambda p: (2 * cx - p[0], 2 * cy - p[1])  # noqa: E731
    from engine import transform
    for st in g.strokes:
        st.points = [turn(p) for p in st.points]
        st.segs = [(s[0], *(turn(p) for p in s[1:])) for s in st.segs]
    g.contours = [transform(c, turn) for c in g.contours]
    g.fixed(tab(P))


@F("seven", 0x37)
def seven(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P)
    b = nib.b
    bar(g, P.cw(8), w, P.C - b * 0.96, s=0.96, nib=nib)
    dn = nib.scaled(0.98)
    c0, c1 = place(dn, (w * 0.28, 0), (w, P.C - b * 1.92), -1, 1, 0.96, 1.0)
    s = g.stroke(c0, nib=dn, s=0.96, cap=0)
    s.line(c1, s=1.0)
    s.end(0)
    g.fixed(tab(P))


@F("eight", 0x38)
def eight(g):
    P = g.P
    nib = fig_nib(g)
    w = figure_width(P) + P.cw(10)
    yt, yb = top(P), bottom(P)
    ym = P.C * 0.55
    inset = w * 0.06
    ring(g, inset, w - inset, ym - nib.b * 0.4, yt, k=0.58)
    ring(g, 0, w, yb, ym + nib.b * 0.4, k=0.6)
    g.fixed(tab(P))


# ---------------------------------------------------------------- small figures


def small(P, scale=0.6, weight=0.8):
    """a master for things drawn smaller (superscripts, fractions, the
    letters in © and ™): the same drawing scaled, its strokes weight times
    the master's"""
    from engine import Nib
    m = copy.copy(P)
    if scale < 0.8:
        weight *= P.t(1.0, 1.0, 0.8)  # small things in heavy weights need room
    for k in ("C", "X", "A", "D"):
        setattr(m, k, getattr(Master, k) * scale)
    m.stem, m.hair = P.stem * weight, P.hair * weight
    m.ustem, m.uhair = P.ustem * weight, P.uhair * weight
    m.a, m.b, m.ua, m.ub = m.stem / 2, m.hair / 2, m.ustem / 2, m.uhair / 2
    m.nib, m.unib = Nib(m.a, m.b), Nib(m.ua, m.ub)
    m.counter = P.counter * scale
    m.ov, m.uov = P.ov * scale, P.uov * scale
    m.sb, m.usb = P.sb * scale, P.usb * scale
    return m
