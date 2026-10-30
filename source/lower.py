"""The lowercase."""

from glyph import ends, glyph, shaped
from parts import (arch, bar, bottom_line, bowl, edge_line, edges, part_of, place, point_of,
                   quarter, ring, stem, through, top_line, x_at, zigzag)
from engine import unit
from serifs import ball, end, foot, head


def marks(g, x, top=None, bottom=0):
    """where accents go: above the x-height (or top) and under the baseline"""
    g.anchor("top", x, g.P.X if top is None else top)
    g.anchor("bottom", x, bottom)


def mono_slab(g, x0, x1, y, top=True, upper=False):
    """a one-width font's flag or foot: a plain bar nearly a stem thick,
    its top (or its foot) at y"""
    from engine import polygon
    P = g.P
    h = (P.ustem if upper else P.stem) * 0.88
    y0, y1 = (y - h, y) if top else (y, y + h)
    g.shape(polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))


def dot_radius(P):
    return P.stem * shaped(0.6, P.t(0.83, 0.656, 0.46))


def i_dot(g, x):
    """i's and j's dot, under the ascender but never nearer the stem than
    the stem is wide, or small sizes run the two together"""
    P = g.P
    r = dot_radius(P)
    y = max(P.A - r - P.t(4, 4, 0), P.X + P.stem * 1.0 + r)
    if shaped(False, True):
        y = max(P.t(700, 730, 738) - r, P.X + P.stem * 0.8 + r)
    g.dot(x, y, r)


# ---------------------------------------------------------------- stems and arches


@glyph("n", 0x6E)
def n(g):
    P = g.P
    xl = P.a
    xr = P.stem + P.cw(shaped(290, 264)) + P.a
    stem(g, xl, 0, P.X)
    arch(g, xl, xr)
    head(g, xl, P.X)
    foot(g, xl)
    foot(g, xr)
    marks(g, (xl + xr) / 2)
    g.space(1.0, 0.88)


@glyph("h", 0x68)
def h(g):
    P = g.P
    xl = P.a
    xr = P.stem + P.cw(shaped(290, 264)) + P.a
    stem(g, xl, 0, P.A)
    arch(g, xl, xr)
    head(g, xl, P.A)
    foot(g, xl)
    foot(g, xr)
    marks(g, (xl + xr) / 2, top=P.A)
    g.space(1.0, 0.88)


@glyph("m", 0x6D)
def m(g):
    P = g.P
    c = P.cw(shaped(236, 226))
    x1 = P.a
    x2 = x1 + P.stem + c
    x3 = x2 + P.stem + c
    stem(g, x1, 0, P.X)
    arch(g, x1, x2, apex=0.52)
    arch(g, x2, x3, apex=0.52)
    head(g, x1, P.X)
    for x in (x1, x2, x3):
        foot(g, x)
    marks(g, x2)
    g.space(1.0, 0.88)


@glyph("u", 0x75)
def u(g):
    P = g.P
    xl = P.a
    xr = P.stem + P.cw(shaped(290, 264)) + P.a
    stem(g, xr, 0, P.X)
    yb = bottom_line(P)
    s = g.stroke((xl, P.X))
    s.line((xl, P.X * 0.44))
    s.arc((xl + (xr - xl) * shaped(0.5, 0.44), yb), "v", k=(0.60, 0.62))
    s.to((xr, shaped(P.t(140, 150, 205), P.t(190, 200, 240))), 0, shaped(60, 62), k=shaped((0.56, 0.40), (0.50, 0.34)),
         s=P.join)
    head(g, xl, P.X)
    head(g, xr, P.X)
    foot(g, xr, side="right")
    marks(g, (xl + xr) / 2)
    g.space(0.88, 1.0)


@glyph("r", 0x72)
def r(g):
    """a short arm, ending almost level"""
    import glyph as G
    if G.STYLE.mono:
        return r_mono(g)
    P = g.P
    xl = P.a
    stem(g, xl, 0, P.X)
    yt = top_line(P)
    yj = P.X - P.t(140, 150, 205)
    xt = xl + P.a + P.cw(96)
    s = g.stroke((xl, yj), s=P.join)
    s.to((xt, yt), 60, 0, k=(0.40, 0.56), s=1.0)
    s.to((xt + P.cw(76) + P.a * 0.4, yt - P.t(12, 14, 22)), 0, -10, k=0.34, s=0.95)
    s.end(**ends(8))
    ball(g, s)
    head(g, xl, P.X)
    foot(g, xl, reach=1.2)
    marks(g, xl + P.a + P.cw(60))
    g.space(1.0, 0.24)


def r_mono(g):
    """the one-width r: a flag and a foot as the i has, so it sits in its
    cell, and a short arm of the full weight leaving the stem on a solid
    shoulder"""
    P = g.P
    w = mono_cell(P)
    xs = w * 0.40
    stem(g, xs, 0, P.X)
    mono_slab(g, w * 0.16, xs, P.X)
    mono_slab(g, w * 0.14, w * 0.80, 0, top=False)
    yt = top_line(P)
    yj = P.X - P.t(150, 160, 200)
    xt = xs + P.a + w * 0.16
    s = g.stroke((xs, yj), s=0.85)
    s.to((xt, yt), 60, 0, k=(0.40, 0.56), s=1.0)
    s.to((w * 0.85, yt - P.t(14, 16, 24)), 0, -12, k=0.36, s=1.0)
    s.end(**ends(8))
    marks(g, xs + P.a + w * 0.1)
    g.fixed(w)


# ---------------------------------------------------------------- rounds


def o_width(P):
    return P.cw(shaped(300, 318)) + 2 * P.stem * P.rnd


@glyph("o", 0x6F)
def o(g):
    P = g.P
    w = o_width(P)
    ring(g, 0, w, bottom_line(P), top_line(P))
    marks(g, w / 2)
    g.space(0.6, 0.6)


def c_curves(P, w, mid=None):
    """the four quarters of the round c and e are cut from"""
    xl, xr = P.a * P.rnd, w - P.a * P.rnd
    cx = w / 2
    cy = P.X * 0.5 if mid is None else mid
    yt, yb = top_line(P), bottom_line(P)
    up, flat = (P.ks, P.kt), (P.kt, P.ks)
    return (
        quarter((xr, cy), (cx, yt), "v", up),
        quarter((cx, yt), (xl, cy), "h", flat),
        quarter((xl, cy), (cx, yb), "v", up),
        quarter((cx, yb), (xr, cy), "h", flat),
    )


@glyph("c", 0x63)
def c(g):
    P = g.P
    w = P.cw(268) + 2 * P.stem * P.rnd
    q1, q2, q3, q4 = c_curves(P, w)
    import glyph as G
    ap = G.STYLE.aperture
    t0, t1 = P.t(0.42, 0.40, 0.36) / ap, 1 - (1 - P.t(0.62, 0.62, 0.66)) / ap
    s = g.stroke(point_of(q1, t0), s=1.0, **ends(24))
    part_of(s, q1, t0, 1.0, s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    part_of(s, q4, 0.0, t1, s=1.0)
    s.end(**ends(22))
    ball(g, s, start=True)
    marks(g, w / 2 + P.a * 0.3)
    g.space(0.6, 0.42)
    if G.STYLE.mono:
        g.max_fit = 1.15  # narrower than o, as a c should be


@glyph("e", 0x65)
def e(g):
    P = g.P
    w = P.cw(292) + 2 * P.stem * P.rnd
    xl, xr = P.a * P.rnd, w - P.a * P.rnd
    ybar = P.X * P.t(0.53, 0.52, 0.50)
    q1, q2, q3, q4 = c_curves(P, w)
    # the top from the bar's end round to the bottom
    # the bowl starts at the bar's foot, so its outer edge runs on down to it
    hb = P.b * P.t(0.92, 0.9, 0.82)
    top = quarter((xr, ybar - hb), q1[3], "v", P.k)
    s = g.stroke((xr, ybar - hb), s=P.rnd)
    s.curve(top[1], top[2], top[3], s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    import glyph as G
    part_of(s, q4, 0.0, 1 - (1 - P.t(0.64, 0.64, 0.50)) / G.STYLE.aperture, s=1.0)
    s.end(**ends(P.t(22, 22, 10)))
    bar(g, xl, xr, ybar, s=P.t(0.92, 0.9, 0.82))
    marks(g, w / 2)
    g.space(0.6, 0.5)


def a_parts(g, stem_down=True):
    """a's hook and bowl; returns the stem's centre line (æ joins its e
    there)"""
    P = g.P
    w = P.cw(shaped(250, 238)) + 2 * P.stem
    xs = w - P.a
    yt = top_line(P)
    # the hook over the top, into the stem (in the interface letters it
    # flattens and is cut upright, as their other rounds do)
    import glyph as G
    if G.STYLE.humanist:
        s = g.stroke((P.a * 0.75 + P.cw(10), P.X * 0.88), s=0.96, upright=True)
        s.to((w * 0.50, yt), 28, 0, k=(0.30, 0.40), s=1.0)
    else:
        s = g.stroke((P.a * 1.1 + P.cw(20), P.X * P.t(0.80, 0.80, 0.78)), s=1.0, **ends(P.t(22, 22, 12)))
        s.to((w * 0.50, yt), P.t(58, 58, 34), 0, k=(0.42, 0.52))
    ball(g, s, start=True)
    s.arc((xs, P.X * 0.56), "h", k=(0.62, 0.58))
    if stem_down and G.STYLE.a == "spur":
        # the stem turns out into a short spur at its foot
        yb = bottom_line(P)
        s.line((xs, P.X * 0.16))
        s.arc((xs + P.a + P.cw(26), yb + P.b * 0.2), "v", k=(0.55, 0.6), s=0.9)
        s.end(**ends(10))
    else:
        s.line((xs, 0 if stem_down else P.X * 0.40))
    # the bowl, from the stem round and back
    ybt = P.X * P.t(0.60, 0.60, 0.62) - P.b * 0.85
    yb = bottom_line(P)
    xbl = P.a * P.rnd
    xm = xbl + (xs - xbl) * 0.42
    if G.STYLE.humanist:  # (its top falls a little away from the stem)
        b = g.stroke((xs, ybt + P.b * 0.5), s=0.86)
        b.to((xs - (xs - xbl) * 0.42, ybt), 188, 180, k=0.4)
    else:
        b = g.stroke((xs, ybt), s=0.86)
        b.line((xs - (xs - xbl) * 0.42, ybt))
    side = P.t(P.rnd, P.rnd, 0.92)
    b.arc((xbl, (ybt + yb) * 0.5), "h", k=(0.60, 0.62), s=side)
    b.arc((xm, yb), "v", k=(0.62, 0.60), s=1.0)
    b.to((xs, P.t(100, 106, 150)), 0, 30, k=(0.5, 0.4), s=P.join)
    return xs


@glyph("a", 0x61)
def a(g):
    xs = a_parts(g)
    foot(g, xs, side="right")
    w = xs + g.P.a
    marks(g, w * 0.5)
    g.space(0.62, 1.0)


@glyph("b", 0x62)
def b(g):
    P = g.P
    xs = P.a
    xo = xs + P.a + P.cw(shaped(292, 296)) + P.a * P.rnd
    stem(g, xs, 0, P.A)
    bowl(g, xs, xo)
    head(g, xs, P.A)
    marks(g, (xs + xo) / 2 + P.a * 0.3, top=P.A)
    g.space(1.0, 0.6)


@glyph("d", 0x64)
def d(g):
    P = g.P
    xo = P.a * P.rnd
    xs = xo + P.a * P.rnd + P.cw(shaped(292, 296)) + P.a
    stem(g, xs, 0, P.A)
    bowl(g, xs, xo, flip=True)
    head(g, xs, P.A)
    foot(g, xs, side="right")
    marks(g, (xs + xo) / 2 - P.a * 0.3, top=P.A)
    g.space(0.6, 1.0)


@glyph("p", 0x70)
def p(g):
    P = g.P
    xs = P.a
    xo = xs + P.a + P.cw(shaped(292, 296)) + P.a * P.rnd
    stem(g, xs, P.D, P.X)
    bowl(g, xs, xo)
    head(g, xs, P.X)
    foot(g, xs, P.D)
    marks(g, (xs + xo) / 2 + P.a * 0.3)
    g.space(1.0, 0.6)


@glyph("q", 0x71)
def q(g):
    P = g.P
    xo = P.a * P.rnd
    xs = xo + P.a * P.rnd + P.cw(shaped(292, 296)) + P.a
    stem(g, xs, P.D, P.X)
    bowl(g, xs, xo, flip=True)
    foot(g, xs, P.D)
    marks(g, (xs + xo) / 2 - P.a * 0.3)
    g.space(0.6, 1.0)


@glyph("g", 0x67)
def g_(g):
    import glyph as G
    if G.STYLE.g == "double":
        return g_double(g)
    P = g.P
    xo = P.a * P.rnd
    xs = xo + P.a * P.rnd + P.cw(286) + P.a
    bowl(g, xs, xo, flip=True)
    yb = bottom_line(P, base=P.D)
    s = g.stroke((xs, P.X))
    s.line((xs, P.D * 0.30))
    s.arc(((xs + xo) / 2 + P.a * 0.2, yb), "v", k=(0.62, 0.58))
    s.line((xo + P.a * 0.2 + P.cw(30), yb), s=0.96)
    marks(g, (xs + xo) / 2 - P.a * 0.3, bottom=P.D)
    g.space(0.6, 1.0)


def g_double(g):
    """a double-storey g: a bowl in the x-height with an ear, a link down
    to the left, and a loop below the baseline"""
    P = g.P
    w = P.cw(300) + 2 * P.stem * P.rnd
    a, b = P.a, P.b
    # the bowl
    xb0, xb1 = P.cw(14), w - P.cw(46)
    ring(g, xb0, xb1, P.X * 0.30 + b, top_line(P))
    # the ear, off its top right
    ear = g.stroke((xb1 - a * 1.3, P.X - b * 0.9), s=0.9)
    ear.line((w + P.cw(26), P.X - b * 0.9), s=0.86)
    # the link and the loop, one stroke from the bowl's foot
    yk = -P.X * 0.02 + b
    yl = bottom_line(P, base=P.D)
    xl, xr = a, w - a
    s = g.stroke((xb0 + a + P.cw(44), P.X * 0.30 + b), s=0.9)
    s.to((xl + P.cw(16), yk + P.X * P.t(0.2, 0.2, 0.26)), 236, 270, k=(0.4, 0.4), s=0.94)
    s.arc((w * 0.5, yk), "v", k=0.58, s=0.96)
    s.arc((xr, (yk + yl) / 2), "h", k=0.58, s=P.rnd)
    s.arc((w * 0.5, yl), "v", k=0.58, s=1.0)
    s.arc((xl, (yk + yl) / 2), "h", k=0.58, s=P.rnd)
    s.to((xl + P.cw(110), yk - b * 0.3), 90, 20, k=(0.4, 0.4), s=0.94)
    marks(g, (xb0 + xb1) / 2, bottom=P.D)
    g.space(0.6, 0.12)


@glyph("s", 0x73)
def s_(g):
    """two even bowls on an even spine, the ends cut near upright"""
    import glyph as G
    P = g.P
    mono = G.STYLE.mono
    w = P.cw(230) + 2 * P.stem
    # heavy weights thin the s's level strokes, or its counters close (in
    # one-width fonts, heavier, to match its spine and the rest)
    flat = P.t(1.0, 1.0, 0.84) * (P.t(1.1, 1.1, 0.95) if mono else 1.0)
    yt = P.X + P.ov - P.b * flat
    yb = -P.ov + P.b * flat
    a = P.a
    cx = w / 2
    xul, xur = a * 1.02 + w * 0.02, w - a * 1.0 - w * 0.01
    yu = P.X * (P.t(0.73, 0.73, 0.726) if mono else P.t(0.74, 0.74, 0.726))
    xll, xlr = a + w * 0.01, w - a * 1.04
    yl = P.X - yu if mono else P.X * P.t(0.26, 0.26, 0.274)
    up_right = quarter((xur, yu), (cx, yt), "v", 0.58)
    up_left = quarter((cx, yt), (xul, yu), "h", 0.6)
    lo_right = quarter((xlr, yl), (cx, yb), "v", 0.6)
    lo_left = quarter((cx, yb), (xll, yl), "h", 0.58)
    ap = G.STYLE.aperture
    t0, t1 = P.t(0.34, 0.34, 0.40) / ap, 1 - (1 - P.t(0.66, 0.66, 0.60)) / ap
    side = P.t(1.02, 1.02, 0.92)
    cut = 12 if G.STYLE.mono else 26
    st = g.stroke(point_of(up_right, t0), s=0.98 * flat, **ends(cut))
    part_of(st, up_right, t0, 1.0, s=flat)
    st.curve(up_left[1], up_left[2], up_left[3], s=side)
    # the spine: in heavy weights flatter and lighter, the one way its
    # turns stay rounder than the pen in the room there is (in one-width
    # fonts, where the s is narrower against its weight, a little steeper,
    # and leaving its bowls sooner: long handles there fold its inside)
    if mono:
        spine = P.t(-34, -34, -33)
        k = P.t((0.36, 0.40), (0.36, 0.40), (0.32, 0.36))
        weight = P.t(1.0, 1.0, 0.95)
    else:
        spine = P.t(-30, -30, -20)
        k = P.t((0.44, 0.48), (0.44, 0.48), (0.5, 0.25))
        weight = P.t(1.04, 1.04, 0.84)
    st.to((cx, P.X * 0.5), 270, spine, k=k, s=weight)
    st.to((xlr, yl), spine, 270, k=k[::-1], s=side)
    st.curve(lo_right[1], lo_right[2], lo_right[3], s=flat)
    part_of(st, lo_left, 0.0, t1, s=0.98 * flat)
    st.end(**ends(cut))
    marks(g, cx)
    g.space(0.62, 0.62)
    if G.STYLE.mono:
        # widened to fill the cell, its spine flattens into a wave: it
        # keeps its own width instead, even and balanced
        g.max_fit = 1.04


# ---------------------------------------------------------------- i j l t f

@glyph("space", 0x20)
def space(g):
    from punct import word_space
    g.fixed(word_space(g.P))


def mono_cell(P):
    return P.target([0x69]) or 600


def i_body(g):
    """i's stem; in one-width fonts, with a serif at its top left and a
    slab at its foot, so it fills its width"""
    import glyph as G
    P = g.P
    if not G.STYLE.mono:
        stem(g, P.a, 0, P.X)
        head(g, P.a, P.X)
        foot(g, P.a)
        return P.a
    w = mono_cell(P)
    xs = w * 0.54
    stem(g, xs, 0, P.X)
    mono_slab(g, w * 0.24, xs, P.X)
    mono_slab(g, w * 0.16, w * 0.86, 0, top=False)
    return xs


@glyph("dotlessi", 0x131)
def dotlessi(g):
    xs = i_body(g)
    marks(g, xs)
    g.space(1.0, 1.0)


@glyph("i", 0x69)
def i(g):
    xs = i_body(g)
    i_dot(g, xs)
    marks(g, xs)
    g.space(1.0, 1.0)


def j_body(g):
    P = g.P
    xs = P.a + P.cw(150)
    yb = bottom_line(P, base=P.D)
    s = g.stroke((xs, P.X))
    s.line((xs, P.D * 0.36))
    s.arc((xs - P.a - P.cw(70), yb), "v", k=(0.6, 0.6))
    s.line((xs - P.a - P.cw(140), yb), s=0.96)
    ball(g, s)
    import glyph as G
    if G.STYLE.mono:
        mono_slab(g, xs - P.a - P.cw(120), xs, P.X)  # its flag
        g.max_fit = 1.3
    head(g, xs, P.X)
    marks(g, xs, bottom=P.D)
    # (in one-width fonts, the hook kept inside the cell, the j centred)
    g.space(1.0, 1.0) if G.STYLE.mono else g.space(-0.5, 1.0)
    return xs


@glyph("dotlessj", 0x237)
def dotlessj(g):
    j_body(g)


@glyph("j", 0x6A)
def j(g):
    xs = j_body(g)
    i_dot(g, xs)


@glyph("l", 0x6C)
def l(g):
    P = g.P
    xs = P.a
    yb = bottom_line(P)
    s = g.stroke((xs, P.A))
    s.line((xs, P.t(150, 160, 210)))
    s.arc((xs + P.a + P.cw(52), yb), "v", k=(0.58, 0.6))
    s.line((xs + P.a + P.cw(92), yb), s=0.95)
    import glyph as G
    if G.STYLE.mono:
        mono_slab(g, xs - P.a - P.cw(110), xs, P.A)  # its flag
        g.max_fit = 1.12
        g.space(1.0, 1.0)
    else:
        g.space(1.0, 0.3)
    head(g, xs, P.A)
    marks(g, xs + P.a * 0.4, top=P.A)


@glyph("t", 0x74)
def t(g):
    P = g.P
    xs = P.a + P.cw(66)
    yb = bottom_line(P)
    top = P.X + P.t(150, 156, 160)
    import glyph as G
    s = g.stroke((xs, top), cap=G.STYLE.t_top)
    s.line((xs, P.t(150, 160, 210)))
    s.arc((xs + P.a + P.cw(56), yb), "v", k=(0.58, 0.6))
    s.line((xs + P.a + P.cw(112), yb), s=0.95)
    bar(g, xs - P.a - P.cw(66), xs + P.a + P.cw(118), P.X - P.b * 0.9, s=0.9)
    marks(g, xs, top=top)
    g.space(0.2, 0.3)


@glyph("f", 0x66)
def f(g):
    P = g.P
    xs = P.a + P.cw(72)
    yt = top_line(P) + (P.A - P.X)
    s = g.stroke((xs, 0))
    s.line((xs, P.A - P.t(170, 180, 230)))
    s.arc((xs + P.a + P.cw(66), yt), "v", k=(0.6, 0.58))
    s.to((xs + P.a + P.cw(P.t(156, 156, 190)), P.A - P.t(40, 44, 96)), 0, P.t(-30, -30, -36), k=0.36, s=0.95)
    s.end(**ends(16))
    ball(g, s)
    bar(g, xs - P.a - P.cw(70), xs + P.a + P.cw(120), P.X - P.b * 0.9, s=0.9)
    foot(g, xs, reach=1.2)
    marks(g, xs, top=P.A)
    g.space(0.2, 0.0)


# ---------------------------------------------------------------- diagonals


@glyph("k", 0x6B)
def k(g):
    P = g.P
    xs = P.a
    w = P.stem + P.cw(shaped(330, 318))
    stem(g, xs, 0, P.A)
    nib = P.nib.scaled(0.96)
    yj = P.X * 0.32
    c0, c1 = place(nib, (xs, yj), (w - P.cw(20), P.X), 0, 1)
    through(g, c0, c1, nib=nib, cap0=90, cap1=0)
    # the leg leaves the arm and runs to the baseline
    t = 0.40
    lx, ly = c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t
    d0, d1 = place(nib, (w, 0), (lx - P.a * shaped(0.4, 0.1), ly + P.b * shaped(0.2, -0.3)), 1, 0, 1.0, 0.9)
    through(g, d0, d1, s0=1.0, s1=0.9, nib=nib, cap0=0, cap1=0)
    head(g, xs, P.A)
    foot(g, xs)
    end(g, c1, P.X)
    end(g, d0, 0)
    marks(g, w * 0.5, top=P.A)
    g.space(1.0, 0.12)


@glyph("v", 0x76)
def v(g):
    P = g.P
    w = P.stem * 1.8 + P.cw(shaped(326, 314))
    nib = g.nib.scaled(0.95)
    cuts = zigzag(g, [(0, P.X), (w / 2, 0, P.stem * 0.5), (w, P.X)], [(1.0, 0.9), (0.9, 1.0)], nib)
    end(g, cuts[0][0], P.X)
    end(g, cuts[-1][1], P.X)
    marks(g, w / 2)
    g.space(0.14, 0.14)


@glyph("w", 0x77)
def w(g):
    """two even vees, the middle one reaching the x-height"""
    P = g.P
    wd = P.stem * 3.2 + P.cw(shaped(560, 536))
    nib = g.nib.scaled(0.92)
    flat = P.stem * 0.46
    q = wd / 4
    cuts = zigzag(g, [(0, P.X), (q + q * 0.05, 0, flat), (wd / 2, P.X, flat * 0.8),
                      (3 * q - q * 0.05, 0, flat), (wd, P.X)],
                  [(1.0, 0.94), (0.94, 0.94), (0.94, 0.94), (0.94, 1.0)], nib)
    end(g, cuts[0][0], P.X)
    end(g, cuts[-1][1], P.X)
    marks(g, wd / 2)
    g.space(0.12, 0.12)
    import glyph as G
    if G.STYLE.mono:
        g.min_fit = 0.25  # its four strokes take most of a cell

@glyph("x", 0x78)
def x(g):
    P = g.P
    w = P.stem * 1.6 + P.cw(shaped(310, 300))
    nib = g.nib.scaled(0.95)
    for st in (edge_line(g, (w * 0.03, P.X), (w, 0), -1, 1, nib=nib),
               edge_line(g, (w * 0.97, P.X), (0, 0), 1, -1, nib=nib)):
        end(g, st.points[0], 0)
        end(g, st.points[1], P.X)
    marks(g, w / 2)
    g.space(0.1, 0.1)


@glyph("y", 0x79)
def y(g):
    P = g.P
    w = P.stem * 1.8 + P.cw(326)
    nib = g.nib.scaled(0.95)
    xm = w / 2 + P.a * 0.25
    import glyph as G
    # the right stroke runs on into the descender, straight, or curving
    # to the left in a tail
    c0, c1 = place(nib, (xm + P.stem * 0.25, 0), (w, P.X), 1, 1)
    d = unit((c1[0] - c0[0], c1[1] - c0[1]))
    if G.STYLE.y == "curved":
        bend = (c0[0] + d[0] * (P.D * 0.28 / d[1]), P.D * 0.28)
        yb = bottom_line(P, base=P.D)
        t = g.stroke(c1, nib=nib, cap=0)
        t.line(bend)
        t.to((bend[0] - P.cw(150) - P.a, yb), (-d[0], -d[1]), 180, k=(0.5, 0.45))
        t.line((bend[0] - P.cw(200) - P.a, yb), s=0.94)
    else:
        tail = (c0[0] + d[0] * (P.D / d[1]), P.D)
        through(g, tail, c1, nib=nib)
    # the left one ends where its left edge meets the right one's
    meet_x = x_at(edges(nib, c0, c1)[0], 0)
    a0, a1 = place(nib, (0, P.X), (meet_x, 0), -1, -1, 1.0, 0.88)
    through(g, a1, a0, s0=0.88, s1=1.0, nib=nib)
    end(g, c1, P.X)
    end(g, a0, P.X)
    marks(g, w / 2, bottom=P.D)
    g.space(0.14, 0.14)


@glyph("z", 0x7A)
def z(g):
    P = g.P
    w = P.stem * 1.2 + P.cw(300)
    hb = P.b * 0.96
    xr = w - P.a * 0.4
    bar(g, P.cw(16), xr, P.X - hb, s=0.96)
    bar(g, 0, w, hb, s=0.96)
    # the diagonal meets the top bar's lower corner and the bottom one's upper
    edge_line(g, (xr, P.X - 2 * hb), (0, 2 * hb), 1, -1, nib=g.nib.scaled(1.02))
    marks(g, w / 2)
    g.space(0.4, 0.4)
