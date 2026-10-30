"""The Sans's own drawing of the letters that set it apart: its round
strokes flatten as they end, and are cut upright; its hooks stay round; its
G stands on an upright, and its 2 and 6 are one sweep of the pen. install()
puts these in place of the shared letters, for a family that's humanist."""

import math

import glyph as G
from engine import unit
from figures import bottom, fig_nib, tab, top, underside
from lower import c_curves, i_dot, marks
from parts import bar, bottom_line, bowl, edges, place, quarter, ring, stem, through, top_line, x_at
from upper import marks as cap_marks

# how a round stroke ends: its height against the x-height (capitals and
# figures end nearer their tops), and how far it's still climbing there
# (degrees from level, about twice the slope of the way there, so the curve
# bends one way all along)
LOW, HIGH, CAP_LOW, CAP_HIGH = 0.125, 0.88, 0.10, 0.90
# (heavy strokes climb less, or their inner corners turn to beaks)


def climb(P):
    return P.t(30, 30, 12)


# how long the curve's handles are, at the end and at the top of the round
AT_END, AT_TOP = 0.30, 0.34


# ---------------------------------------------------------------- rounds


def left_round(P, a, w, height, yt, yb):
    """the top-to-foot left side of an open round, its top and foot nearer
    the opening than the middle, so its ends carry the curve on"""
    xl, cx, cy = a * P.rnd, w * 0.55, height / 2
    return quarter((cx, yt), (xl, cy), "h", (0.60, 0.56)), quarter((xl, cy), (cx, yb), "v", (0.56, 0.60))


def c(g):
    P = g.P
    w = P.cw(256) + 2 * P.stem * P.rnd
    q2, q3 = left_round(P, P.a, w, P.X, top_line(P), bottom_line(P))
    xe = w - P.a * 0.3
    s = g.stroke((xe, P.X * HIGH), s=0.96, upright=True)
    s.to(q2[0], 180 - climb(P), 180, k=(AT_END, AT_TOP), s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    s.to((xe, P.X * LOW), 0, climb(P), k=(AT_TOP, AT_END), s=0.96)
    s.end(upright=True)
    marks(g, w / 2 + P.a * 0.3)
    g.space(0.6, 0.42)


def e(g):
    P = g.P
    w = P.cw(282) + 2 * P.stem * P.rnd
    xl, xr = P.a * P.rnd, w - P.a * P.rnd
    ybar = P.X * P.t(0.51, 0.5, 0.49)
    q1, q2, _, _ = c_curves(P, w)
    _, q3 = left_round(P, P.a, w, P.X, top_line(P), bottom_line(P))
    # the bowl starts at the bar's foot, so its outer edge runs on down to it
    hb = P.b * P.t(0.96, 0.96, 0.84)
    side = quarter((xr, ybar - hb), q1[3], "v", (P.ks, P.kt))
    s = g.stroke((xr, ybar - hb), s=P.rnd)
    s.curve(side[1], side[2], side[3], s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    s.to((w - P.a * 0.45, P.X * LOW), 0, climb(P), k=(AT_TOP, AT_END), s=0.96)
    s.end(upright=True)
    bar(g, xl, xr, ybar, s=P.t(0.96, 0.96, 0.84))
    marks(g, w / 2)
    g.space(0.6, 0.5)


def both_s(g, height, high, low, w, a, b, ov, nudge, lean):
    """s and S: two bowls, the lower a little the larger, on a diagonal
    spine; each end flattens and is cut upright"""
    P = g.P
    flat = P.t(1.0, 1.0, 0.84)
    yt = height + ov - b * flat
    yb = -ov + b * flat
    cx = w / 2
    xul, xlr = a + w * 0.015, w - a
    yu, yl = height * 0.745, height * 0.25
    side = P.t(1.02, 1.02, 0.94)
    st = g.stroke((w - a * 0.3 - w * 0.02, height * high), s=0.96 * flat, upright=True)
    st.to((cx + nudge, yt), 180 - climb(P), 180, k=(AT_END, AT_TOP), s=flat)
    st.arc((xul, yu), "h", k=(P.kt, P.ks), s=side)
    st.to((cx, height * 0.5), 270, lean, k=(0.40, 0.44), s=P.t(1.04, 1.04, 0.86))
    st.to((xlr, yl), lean, 270, k=(0.44, 0.40), s=side)
    st.arc((cx - nudge, yb), "v", k=(P.ks, P.kt), s=flat)
    st.to((a * 0.3, height * low), 180, 180 - climb(P), k=(AT_TOP, AT_END), s=0.96 * flat)
    st.end(upright=True)
    return cx


def s_(g):
    P = g.P
    w = P.cw(190) + 2 * P.stem
    marks(g, both_s(g, P.X, HIGH, LOW, w, P.a, P.b, P.ov, w * 0.02, P.t(-30, -30, -22)))
    g.space(0.62, 0.62)


def S(g):
    P = g.P
    w = P.cw(290) + 2 * P.ustem
    cap_marks(g, both_s(g, P.C, CAP_HIGH, CAP_LOW, w, P.ua, P.ub, P.uov, w * 0.02, P.t(-32, -32, -24)))
    g.space(0.6, 0.6)


def C(g):
    P = g.P
    w = P.cw(452) + 2 * P.ustem * P.rnd
    q2, q3 = left_round(P, P.ua, w, P.C, top_line(P, True), bottom_line(P, True))
    xe = w - P.ua * 0.3
    s = g.stroke((xe, P.C * CAP_HIGH), s=0.96, upright=True)
    s.to(q2[0], 180 - climb(P), 180, k=(AT_END, AT_TOP), s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    s.to((xe, P.C * CAP_LOW), 0, climb(P), k=(AT_TOP, AT_END), s=0.96)
    s.end(upright=True)
    cap_marks(g, w / 2 + P.ua * 0.3)
    g.space(0.6, 0.4)


def G_(g):
    """the bowl rises to meet a straight upright low down, and the bar runs
    in from the left along the upright's top"""
    P = g.P
    w = P.cw(486) + 2 * P.ustem * P.rnd
    q2, q3 = left_round(P, P.ua, w, P.C, top_line(P, True), bottom_line(P, True))
    xr = w - P.ua
    top_y = P.C * 0.53
    s = g.stroke((w - P.ua * 0.3, P.C * CAP_HIGH), s=0.96, upright=True)
    s.to(q2[0], 180 - climb(P), 180, k=(AT_END, AT_TOP), s=1.0)
    s.curve(q2[1], q2[2], q2[3], s=P.rnd)
    s.curve(q3[1], q3[2], q3[3], s=1.0)
    s.to((xr + P.ua, P.C * 0.095), 0, climb(P), k=(AT_TOP, AT_END), s=0.92)
    s.end(upright=True)
    stem(g, xr, P.C * 0.07, top_y)
    bar(g, xr - P.ua - P.cw(148), xr + P.ua, top_y - P.ub * 0.92, s=0.92)
    cap_marks(g, w / 2)
    g.space(0.6, 0.9)


# ---------------------------------------------------------------- hooks


def g_(g):
    P = g.P
    xo = P.a * P.rnd
    xs = xo + P.a * P.rnd + P.cw(292) + P.a
    bowl(g, xs, xo, flip=True)
    yb = bottom_line(P, base=P.D + 7)
    s = g.stroke((xs, P.X))
    s.line((xs, P.X * 0.02))
    s.arc(((xs + xo) / 2 + P.a * 0.2, yb), "v", k=(0.58, 0.56))
    s.to((xo + P.a * 0.35, yb + P.t(30, 32, 30)), 180, 180 - climb(P), k=(AT_TOP, AT_END), s=0.98)
    s.end(upright=True)
    marks(g, (xs + xo) / 2 - P.a * 0.3, bottom=P.D)
    g.space(0.6, 1.0)


def j_body(g):
    P = g.P
    xs = P.a + P.cw(140)
    yb = bottom_line(P, base=P.D + 7)
    s = g.stroke((xs, P.X))
    s.line((xs, -P.X * 0.05))
    s.to((xs - P.a - P.cw(120), yb + P.t(26, 28, 26)), 270, 180 - climb(P) * 0.7, k=(0.72, 0.5))
    s.end(upright=True)
    marks(g, xs, bottom=P.D)
    g.space(-0.5, 1.0)
    return xs


def j(g):
    i_dot(g, j_body(g))


def l(g):
    P = g.P
    xs = P.a
    yb = bottom_line(P)
    s = g.stroke((xs, P.A))
    s.line((xs, yb + P.t(126, 134, 176)))
    s.to((xs + P.a + P.cw(86), yb + P.t(12, 13, 12)), 270, climb(P) * 0.7, k=(0.70, 0.42), s=0.95)
    s.end(upright=True)
    g.space(1.0, 0.4)
    marks(g, xs + P.a * 0.4, top=P.A)


def t(g):
    P = g.P
    left = P.cw(58)
    xs = P.a + left
    yb = bottom_line(P)
    top_y = P.X + P.t(145, 148, 155)
    s = g.stroke((xs, top_y), cap=G.STYLE.t_top)
    s.line((xs, yb + P.t(126, 134, 176)))
    s.to((xs + P.a + P.cw(108), yb + P.t(12, 13, 12)), 270, climb(P) * 0.7, k=(0.70, 0.42), s=0.95)
    s.end(upright=True)
    bar(g, xs - P.a - left, xs + P.a + P.cw(112), P.X - P.b * 0.9, s=0.9)
    marks(g, xs, top=top_y)
    g.space(0.2, 0.3)


def f(g):
    P = g.P
    left = P.cw(60)
    xs = P.a + left
    yt = top_line(P) + (P.A - P.X)
    s = g.stroke((xs, 0))
    s.line((xs, P.A - P.t(170, 176, 220)))
    s.arc((xs + P.a + P.cw(52), yt), "v", k=(0.6, 0.58))
    s.to((xs + P.a + P.cw(P.t(120, 120, 170)), yt - P.t(8, 8, 10)), 0, -6, k=0.4, s=0.96)
    s.end(upright=True)
    bar(g, xs - P.a - left, xs + P.a + P.cw(104), P.X - P.b * 0.9, s=0.9)
    marks(g, xs, top=P.A)
    g.space(0.2, 0.0)


def r(g):
    P = g.P
    xl = P.a
    stem(g, xl, 0, P.X)
    yt = top_line(P)
    xt = xl + P.a + P.cw(84)
    s = g.stroke((xl, P.X - P.t(200, 210, 250)), s=P.join)
    s.to((xt, yt), 62, 0, k=(0.34, 0.50), s=1.0)
    s.to((xt + P.cw(64) + P.a * 0.3, yt - P.t(10, 12, 14)), 0, -8, k=0.36, s=0.96)
    s.end(upright=True)
    marks(g, xl + P.a + P.cw(60))
    g.space(1.0, 0.24)


def y(g):
    """the right stroke runs on down, turning left into a short, flat tail"""
    P = g.P
    w = P.stem * 1.8 + P.cw(314)
    nib = g.nib.scaled(0.95)
    xm = w / 2 + P.a * 0.25
    c0, c1 = place(nib, (xm + P.stem * 0.25, 0), (w, P.X), 1, 1)
    d = unit((c1[0] - c0[0], c1[1] - c0[1]))
    bend = (c0[0] + d[0] * (P.D * 0.34 / d[1]), P.D * 0.34)
    yb = bottom_line(P, base=P.D + 7)
    tail = g.stroke(c1, nib=nib, cap=0)
    tail.line(bend)
    tail.to((bend[0] - P.cw(P.t(96, 96, 170)) - P.a, yb + P.t(24, 26, 24)), (-d[0], -d[1]), 180 - climb(P) * 0.7,
            k=(AT_TOP, AT_END))
    tail.end(upright=True)
    # the left one ends where its left edge meets the right one's
    meet_x = x_at(edges(nib, c0, c1)[0], 0)
    a0, a1 = place(nib, (0, P.X), (meet_x, 0), -1, -1, 1.0, 0.88)
    through(g, a1, a0, s0=0.88, s1=1.0, nib=nib)
    marks(g, w / 2, bottom=P.D)
    g.space(0.14, 0.14)


def J(g):
    P = g.P
    yb = bottom_line(P, True)
    xs = P.ua + P.cw(150)
    s = g.stroke((xs, P.C))
    s.line((xs, P.C * 0.28))
    s.to((xs - P.ua - P.cw(132), yb + P.t(28, 30, 28)), 270, 180 - climb(P) * 0.7, k=(0.72, 0.46))
    s.end(upright=True)
    cap_marks(g, xs - P.cw(40))
    g.space(0.3, 1.0)


# ---------------------------------------------------------------- figures


def figure(P, n):
    """a figure's outline width, with counters of n (narrower in the
    heaviest weights, where the strokes take the room)"""
    return P.cw(n) * {"Bold": 0.8, "ExtraBold": 0.7}.get(P.name, 1.0) + 2 * P.ustem


def rising(g, nib, x, cx, yt):
    """a figure's top left: an upright cut, rising to the top of its curve"""
    s = g.stroke((x, g.P.C * CAP_HIGH), nib=nib, s=0.96, upright=True)
    s.to((cx, yt), climb(g.P), 0, k=(AT_END, AT_TOP), s=1.0)
    return s


def falling(s, g, nib):
    """a figure's foot: from the bottom of its curve out to an upright cut"""
    s.to((nib.a * 0.3, g.P.C * CAP_LOW), 180, 180 - climb(g.P), k=(AT_TOP, AT_END), s=0.96)
    s.end(upright=True)


def two(g):
    """one sweep from the top, down a curving neck, landing upright on the
    foot's left end"""
    P = g.P
    nib = fig_nib(g)
    w = figure(P, 295)
    a, b = nib.a, nib.b
    xr = w - a
    s = rising(g, nib, a * 0.5 + P.cw(6), w * 0.47, top(P))
    s.arc((xr, P.C * 0.70), "h", k=(P.kt, P.ks), s=1.03)
    s.to((a, 0), 270, 270, k=(0.50, 0.34), s=1.0)
    s.end(cap=0)
    bar(g, a, w + P.cw(8), b * 0.96, s=0.96, nib=nib)
    g.fixed(tab(P))


def three(g):
    P = g.P
    nib = fig_nib(g)
    w = figure(P, 265)
    a = nib.a
    yt, yb = top(P), bottom(P)
    ym = P.C * 0.545
    cx = w * 0.47
    xr1, xr2 = w - a * 1.08 - w * 0.03, w - a
    s = rising(g, nib, a * 0.45 + P.cw(8), cx, yt)
    s.arc((xr1, (yt + ym) / 2), "h", k=(P.kt, P.ks), s=1.0)
    s.arc((cx - w * 0.06, ym), "v", k=(P.ks, P.kt), s=0.94)
    s.line((cx - w * 0.16, ym), s=0.94)
    t2 = g.stroke((cx - w * 0.12, ym), nib=nib, s=0.94)
    t2.line((cx - w * 0.02, ym), s=0.94)
    t2.arc((xr2, (ym + yb) / 2), "h", k=(P.kt, P.ks), s=1.0)
    t2.arc((cx - w * 0.04, yb), "v", k=(P.ks, P.kt), s=1.0)
    falling(t2, g, nib)
    g.fixed(tab(P))


def five(g):
    P = g.P
    nib = fig_nib(g)
    w = figure(P, 250)
    a, b = nib.a, nib.b
    yb = bottom(P)
    xv = a + P.cw(30)
    xtop = xv + P.cw(10)
    bar(g, xtop - a, w - P.cw(10), P.C - b * 0.96, s=0.96, nib=nib)
    yj = P.C * 0.55
    top_b = P.C * 0.635 - b
    xr = w - a
    cx = w * 0.46
    # the bowl starts at the upright's right edge, cut upright against it
    s = g.stroke((xv + a * 0.6, yj), s=P.join + 0.1, nib=nib, upright=True)
    s.to((cx, top_b), 20, 0, k=(0.4, 0.5), s=1.0)
    s.arc((xr, (top_b + yb) / 2), "h", k=(P.kt, P.ks), s=1.03)
    s.arc((cx - w * 0.03, yb), "v", k=(P.ks, P.kt), s=1.0)
    falling(s, g, nib)
    # the upright, leaning a little, into the bowl: its foot cut along the
    # bowl's underside where the two meet
    x1, x2 = xv + a, xv + a + 3
    y1, y2 = underside(s.outline(), x1, yj), underside(s.outline(), x2, yj)
    slope = (y2 - y1) / (x2 - x1)
    xf = xv + a * 0.04
    yf = y1 + (xf - x1) * slope
    through(g, (xf, yf), (xtop, P.C - b * 0.96), nib=nib, cap0=math.degrees(math.atan(slope)), cap1=None)
    g.fixed(tab(P))


def six_stroke(g):
    """one round stroke: from the top, down the long left side, under the
    bowl and back over it, thinning into the side"""
    P = g.P
    nib = fig_nib(g)
    w = figure(P, 309)
    a = nib.a
    yt, yb = top(P), bottom(P)
    xl, xr = a * 1.04, w - a * 1.04
    yr = P.C * 0.635 - nib.b
    s = g.stroke((w - a * 0.45 - P.cw(10), P.C * 0.93), nib=nib, s=0.96, upright=True)
    s.to((w * 0.62, yt), 180 - climb(P) * 0.5, 180, k=0.34, s=1.0)
    s.arc((xl, P.C * 0.46), "h", k=(0.60, 0.54), s=1.04)
    s.arc((w * 0.5, yb), "v", k=(0.54, 0.60), s=1.0)
    s.arc((xr, (yb + yr) / 2), "h", k=(P.kt, P.ks), s=1.04)
    s.arc((w * 0.53, yr), "v", k=(P.ks, P.kt), s=1.0)
    s.to((xl + a * 0.2, P.C * 0.46), 180, 242, k=(0.46, 0.40), s=P.join + 0.1)
    return w


def six(g):
    six_stroke(g)
    g.fixed(tab(g.P))


def nine(g):
    """the six, turned half round about the figure's middle"""
    P = g.P
    w = six_stroke(g)
    cx, cy = w / 2, P.C / 2
    turn = lambda p: (2 * cx - p[0], 2 * cy - p[1])  # noqa: E731
    for st in g.strokes:
        st.points = [turn(p) for p in st.points]
        st.segs = [(seg[0], *(turn(p) for p in seg[1:])) for seg in st.segs]
    g.fixed(tab(P))


def seven(g):
    P = g.P
    nib = fig_nib(g)
    w = figure(P, 309)
    b = nib.b
    bar(g, P.cw(8), w, P.C - b * 0.96, s=0.96, nib=nib)
    dn = nib.scaled(0.98)
    c0, c1 = place(dn, (w * 0.26, 0), (w, P.C - b * 1.92), -1, 1, 0.96, 1.0)
    s = g.stroke(c0, nib=dn, s=0.96, cap=0)
    s.to(c1, 74, 56, k=0.36, s=1.0)
    s.end(0)
    g.fixed(tab(P))


def eight(g):
    """two rings, the upper smaller, sharing one stroke where they meet"""
    P = g.P
    w = figure(P, 316)
    ym = P.C * 0.54
    inset = w * 0.06
    ring(g, inset, w - inset, ym, top(P))
    ring(g, 0, w, bottom(P), ym)
    g.fixed(tab(P))


# each letter's side bearings, as multiples of the master's straight side
SIDES = {"a": (0.57, 0.88), "b": (1.01, 0.60), "c": (0.60, 0.51), "d": (0.60, 1.04), "e": (0.60, 0.51),
         "f": (0.32, -0.19), "g": (0.60, 1.04), "h": (1.01, 0.92), "i": (0.88, 0.85), "j": (-1.14, 0.85),
         "k": (1.01, 0.03), "m": (1.01, 0.92), "n": (1.01, 0.92), "o": (0.60, 0.60), "p": (1.01, 0.60),
         "q": (0.60, 1.04), "r": (1.01, 0.06), "s": (0.63, 0.54), "t": (0.25, 0.35), "u": (0.88, 1.04),
         "v": (0.09, 0.09), "w": (0.16, 0.16), "x": (0.16, 0.19), "y": (0.09, 0.09), "z": (0.19, 0.28),
         "A": (0.10, 0.13), "B": (0.96, 0.55), "C": (0.47, 0.55), "D": (0.96, 0.49), "E": (0.96, 0.47),
         "F": (0.96, 0.44), "G": (0.47, 0.76), "H": (0.96, 0.96), "I": (0.96, 0.96), "J": (0.10, 0.91),
         "K": (0.96, 0.03), "L": (0.96, 0.18), "M": (0.96, 0.96), "N": (0.96, 0.96), "O": (0.47, 0.49),
         "P": (0.96, 0.42), "Q": (0.47, -0.13), "R": (0.96, 0.08), "S": (0.62, 0.52), "T": (0.21, 0.21),
         "U": (0.86, 0.86), "V": (0.10, 0.10), "W": (0.13, 0.13), "X": (0.13, 0.16), "Y": (0.10, 0.08),
         "Z": (0.16, 0.21), "dotlessi": (0.88, 0.85), "dotlessj": (-1.14, 0.85)}

OWN = {"c": c, "e": e, "s": s_, "g": g_, "j": j, "dotlessj": j_body, "l": l, "t": t, "f": f, "r": r, "y": y,
       "C": C, "G": G_, "S": S, "J": J, "two": two, "three": three, "five": five, "six": six, "nine": nine,
       "seven": seven, "eight": eight}


def spaced(drawing, sides):
    def draw(g):
        result = drawing(g)
        g.space(*sides)
        return result
    return draw


def install():
    for name, drawing in OWN.items():
        unicodes, upper, _ = G.GLYPHS[name]
        G.GLYPHS[name] = (unicodes, upper, drawing)
    for name, sides in SIDES.items():
        unicodes, upper, drawing = G.GLYPHS[name]
        G.GLYPHS[name] = (unicodes, upper, spaced(drawing, sides))
