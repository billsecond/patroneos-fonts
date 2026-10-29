"""Box drawing and block elements, for the one-width font only: lines that
run to the cell's edges and the line's whole height, so they join from cell
to cell and row to row (as terminal programs draw their frames and bars).
They stay upright in the italics. Each is drawn from its Unicode name."""

import unicodedata

import glyph as G
from engine import orient, polygon
from glyph import glyph

DIRECTIONS = {"UP": ["up"], "DOWN": ["down"], "LEFT": ["left"], "RIGHT": ["right"],
              "VERTICAL": ["up", "down"], "HORIZONTAL": ["left", "right"]}
WEIGHTS = {"LIGHT", "HEAVY", "SINGLE", "DOUBLE"}
UNIT = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}
# for an arm, the two directions across it (its "+" side first)
ACROSS = {"left": ("up", "down"), "right": ("up", "down"), "up": ("right", "left"), "down": ("right", "left")}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}
# how far lines and blocks reach past the cell's edges, so that next to
# each other (rows set at fractions of a pixel included) they overlap
# rather than leave a pale seam
OVER_X, OVER_Y = 10, 20
EIGHTHS = {"ONE EIGHTH": 1, "ONE QUARTER": 2, "THREE EIGHTHS": 3, "HALF": 4, "FIVE EIGHTHS": 5,
           "THREE QUARTERS": 6, "SEVEN EIGHTHS": 7}


class Cell:
    """the cell's size and the lines' weights, in design units"""

    def __init__(self, P):
        F = G.STYLE
        k = 1000 / F.upm
        self.w = F.mono
        self.bottom, self.top = F.metrics["hheaDescender"] * k, F.metrics["hheaAscender"] * k
        self.cx, self.cy = self.w / 2, (self.bottom + self.top) / 2
        self.light = P.stem * 0.72
        self.heavy = self.light * 1.9
        self.gap = self.light * 1.3  # a double line's two lines, each side of the middle

    def thick(self, weight):
        return self.heavy if weight == "HEAVY" else self.light

    def reach(self, d):
        """how far a line runs from the middle, going d: to the cell's edge
        and a little past"""
        return {"up": self.top - self.cy + OVER_Y, "down": self.cy - self.bottom + OVER_Y,
                "left": self.cx + OVER_X, "right": self.w - self.cx + OVER_X}[d]

    def point(self, d, along, across):
        """a point along direction d from the middle, and across it (to its
        "+" side)"""
        ux, uy = UNIT[d]
        vx, vy = UNIT[ACROSS[d][0]]
        return (self.cx + ux * along + vx * across, self.cy + uy * along + vy * across)


def band(g, c, d, u0, u1, v0, v1):
    """a filled strip along direction d, from u0 to u1 out from the middle
    and from v0 to v1 across"""
    pts = [c.point(d, u0, v0), c.point(d, u1, v0), c.point(d, u1, v1), c.point(d, u0, v1)]
    g.shape(polygon(pts))


def start(g, name):
    """a box glyph: one cell wide, placed as drawn, upright"""
    g.keep_place = True
    g.advance = G.STYLE.mono
    g.upright = True
    return Cell(g.P)


def arms_of(name):
    """{direction: weight} from a name such as 'DOWN LIGHT AND RIGHT HEAVY'
    or 'LIGHT DOWN AND RIGHT' (a part without a weight takes the last one
    named)"""
    groups = []
    for part in name.split(" AND "):
        words = part.split()
        weight = next((w for w in words if w in WEIGHTS), None)
        dirs = [d for w in words if w in DIRECTIONS for d in DIRECTIONS[w]]
        groups.append((weight, dirs))
    out = {}
    last = next((w for w, _ in groups if w), "LIGHT")
    for weight, dirs in groups:
        last = weight or last
        for d in dirs:
            out[d] = last
    return out


def lines(g, c, arms):
    """the arms: single (light or heavy) ones a strip each, double ones two
    light strips that turn their corners as a pair"""
    def reach_in(arm):
        # how far a single arm runs past the middle, to cover the arms across it
        ext = 0
        for side in ACROSS[arm]:
            if side in arms:
                ext = max(ext, c.gap + c.light / 2 if arms[side] == "DOUBLE" else c.thick(arms[side]) / 2)
        return ext

    for arm, weight in arms.items():
        edge = c.reach(arm)
        if weight != "DOUBLE":
            t = c.thick(weight)
            band(g, c, arm, -reach_in(arm), edge, -t / 2, t / 2)
            continue
        for sign, side in ((1, ACROSS[arm][0]), (-1, ACROSS[arm][1])):
            other = OPPOSITE[side]
            if side in arms:
                u0 = c.gap - c.light / 2 if arms[side] == "DOUBLE" else -c.thick(arms[side]) / 2
            elif other in arms:
                u0 = -(c.gap + c.light / 2) if arms[other] == "DOUBLE" else -c.thick(arms[other]) / 2
            else:
                u0 = 0
            v = sign * c.gap
            band(g, c, arm, u0, edge, v - c.light / 2, v + c.light / 2)


def dashes(g, c, weight, n, vertical):
    t = c.thick(weight)
    if vertical:
        size = c.top - c.bottom
        for i in range(n):
            y0 = c.bottom + size * i / n + size / n * 0.2
            band(g, c, "up", y0 - c.cy, y0 - c.cy + size / n * 0.6, -t / 2, t / 2)
    else:
        for i in range(n):
            x0 = c.w * i / n + c.w / n * 0.2
            band(g, c, "right", x0 - c.cx, x0 - c.cx + c.w / n * 0.6, -t / 2, t / 2)


def arc(g, c, a, b):
    """a rounded corner joining arm a to arm b (light), as ╭ ╮ ╯ ╰"""
    t = c.light
    r = c.w * 0.36
    k = 0.5523
    ua, ub = UNIT[a], UNIT[b]
    ox, oy = c.cx + (ua[0] + ub[0]) * r, c.cy + (ua[1] + ub[1]) * r  # the curve's centre

    pts_out, pts_in = [], []
    for rr, pts in ((r + t / 2, pts_out), (r - t / 2, pts_in)):
        # from the arm a side to the arm b side, round the centre
        s = (ox - ub[0] * rr, oy - ub[1] * rr)
        e = (ox - ua[0] * rr, oy - ua[1] * rr)
        # handles: leaving s towards the middle of the turn, arriving at e likewise
        h1 = (s[0] - ua[0] * rr * k, s[1] - ua[1] * rr * k)
        h2 = (e[0] - ub[0] * rr * k, e[1] - ub[1] * rr * k)
        pts.append((s, h1, h2, e))
    so, h1o, h2o, eo = pts_out[0]
    si, h1i, h2i, ei = pts_in[0]
    ea, eb = c.reach(a), c.reach(b)
    # outer side: from arm a's edge in to the curve, round it, out to arm b's edge
    a_out = (so[0] + ua[0] * (ea - r), so[1] + ua[1] * (ea - r))
    b_out = (eo[0] + ub[0] * (eb - r), eo[1] + ub[1] * (eb - r))
    a_in = (si[0] + ua[0] * (ea - r), si[1] + ua[1] * (ea - r))
    b_in = (ei[0] + ub[0] * (eb - r), ei[1] + ub[1] * (eb - r))
    contour = [("L", a_out, so), ("C", so, h1o, h2o, eo), ("L", eo, b_out), ("L", b_out, b_in),
               ("L", b_in, ei), ("C", ei, h2i, h1i, si), ("L", si, a_in), ("L", a_in, a_out)]
    g.shape(orient(contour, True))


def diagonal(g, c, rising):
    """a light line from corner to corner"""
    t = c.light
    h = c.top - c.bottom
    length = (h * h + c.w * c.w) ** 0.5
    dx = t / 2 * length / h  # half its width, measured level
    if rising:
        pts = [(-dx, c.bottom), (dx, c.bottom), (c.w + dx, c.top), (c.w - dx, c.top)]
    else:
        pts = [(-dx, c.top), (dx, c.top), (c.w + dx, c.bottom), (c.w - dx, c.bottom)]
    g.shape(polygon(pts))


def rect(g, x0, y0, x1, y1):
    g.shape(polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))


def fill(g, c, x0, y0, x1, y1):
    """a block, its sides on the cell's edges reaching a little past them"""
    x0 = x0 - OVER_X if x0 <= 0 else x0
    x1 = x1 + OVER_X if x1 >= c.w else x1
    y0 = y0 - OVER_Y if y0 <= c.bottom else y0
    y1 = y1 + OVER_Y if y1 >= c.top else y1
    rect(g, x0, y0, x1, y1)


def box(code):
    name = unicodedata.name(chr(code)).replace("BOX DRAWINGS ", "")

    def f(g):
        c = start(g, name)
        words = name.split()
        if "DASH" in words:
            n = {"DOUBLE": 2, "TRIPLE": 3, "QUADRUPLE": 4}[words[1]]
            dashes(g, c, words[0], n, "VERTICAL" in words)
        elif "ARC" in words:
            a, b = [d for w in words if w in DIRECTIONS for d in DIRECTIONS[w]]
            arc(g, c, a, b)
        elif "DIAGONAL" in words:
            if "CROSS" in words or "UPPER RIGHT TO LOWER LEFT" in name:
                diagonal(g, c, True)
            if "CROSS" in words or "UPPER LEFT TO LOWER RIGHT" in name:
                diagonal(g, c, False)
        else:
            lines(g, c, arms_of(name))
    return f


def block(code):
    name = unicodedata.name(chr(code))

    def f(g):
        c = start(g, name)
        w, b, t = c.w, c.bottom, c.top
        h = t - b
        if name == "FULL BLOCK":
            fill(g, c, 0, b, w, t)
        elif name.endswith("SHADE"):
            # a grid of squares: a quarter of them, half (a chequer), or three quarters
            cols, rows = 4, max(4, round(h / (w / 4)))
            sx, sy = w / cols, h / rows
            for i in range(cols):
                for j in range(rows):
                    on = {"LIGHT SHADE": i % 2 == 0 and j % 2 == 0, "MEDIUM SHADE": (i + j) % 2 == 0,
                          "DARK SHADE": not (i % 2 == 1 and j % 2 == 1)}[name]
                    if on:
                        rect(g, i * sx, b + j * sy, (i + 1) * sx, b + (j + 1) * sy)
        elif name.startswith("QUADRANT"):
            for q in name.replace("QUADRANT ", "").split(" AND "):
                x0, x1 = (0, w / 2) if q.endswith("LEFT") else (w / 2, w)
                y0, y1 = (b + h / 2, t) if q.startswith("UPPER") else (b, b + h / 2)
                fill(g, c, x0, y0, x1, y1)
        else:
            side = name.split()[0]
            part = next(v for k, v in EIGHTHS.items() if k in name) / 8
            if side == "UPPER":
                fill(g, c, 0, t - h * part, w, t)
            elif side == "LOWER":
                fill(g, c, 0, b, w, b + h * part)
            elif side == "LEFT":
                fill(g, c, 0, b, w * part, t)
            elif side == "RIGHT":
                fill(g, c, w * (1 - part), b, w, t)
    return f


if G.STYLE is not None and G.STYLE.mono:
    for code in range(0x2500, 0x2580):
        glyph(f"uni{code:04X}", code)(box(code))
    for code in range(0x2580, 0x25A0):
        glyph(f"uni{code:04X}", code)(block(code))
