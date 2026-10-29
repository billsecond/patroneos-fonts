"""Serifs, for the families that have them: bracketed slabs at the ends of
stems and diagonals, and upright ones at the ends of arms. Each function
draws nothing in a family without serifs, so letters call them freely."""

import glyph as G
from engine import polygon

# a serif's slab: its thickness against a level stroke's, how far it
# reaches past a stem (a little more for heavier stems, but far less than
# they grow: long bold serifs crowd the letters), and its bracket's size
# (large, so the serif flows out of the stem rather than meeting it square)
SLAB, REACH, BRACKET = 0.7, 0.3, 0.85


def on():
    return G.STYLE is not None and G.STYLE.serif


def serif_part(g, contour):
    """a serif's outline, marked as one (spacing counts serifs at half
    their reach: glyph.Draw.spacing_box)"""
    g.shape(contour)
    if not hasattr(g, "serif_parts"):
        g.serif_parts = set()
    g.serif_parts.add(len(g.contours) - 1)


def sizes(g, upper):
    P = g.P
    stem = P.ustem if upper else P.stem
    hair = P.uhair if upper else P.hair
    return stem / 2, hair * SLAB, stem * REACH + (62 if upper else 52), stem * BRACKET


def fillet(g, corner, dx, dy, r):
    """a bracket: the curved fill in the corner between a slab and a stem,
    reaching r along each; dx, dy (each 1 or -1) point from the corner
    along the slab and along the stem"""
    x, y = corner
    k = 0.5
    a = (x + dx * r, y)
    b = (x, y + dy * r)
    c = [("L", (x - dx * 2, y - dy * 2), (x + dx * r, y - dy * 2)), ("L", (x + dx * r, y - dy * 2), a),
         ("C", a, (x + dx * r * k, y), (x, y + dy * r * k), b), ("L", b, (x - dx * 2, y + dy * r)),
         ("L", (x - dx * 2, y + dy * r), (x - dx * 2, y - dy * 2))]
    from engine import orient
    serif_part(g, orient(c, True))


def foot(g, x, y=0, side="both", upper=False, reach=1.0):
    """a slab at the foot of the stem centred on x, standing on y"""
    if not on():
        return
    a, h, L, r = sizes(g, upper)
    L *= reach
    r = min(r, L * 0.72)  # (the bracket stops short of the slab's end)
    left = x - a - (L if side in ("both", "left") else 0)
    right = x + a + (L if side in ("both", "right") else 0)
    serif_part(g, polygon([(left, y), (right, y), (right, y + h), (left, y + h)]))
    if side in ("both", "left"):
        fillet(g, (x - a, y + h), -1, 1, r)
    if side in ("both", "right"):
        fillet(g, (x + a, y + h), 1, 1, r)


def head(g, x, y, side="left", upper=False, reach=1.0):
    """a slab at the top of the stem centred on x, its top at y"""
    if not on():
        return
    a, h, L, r = sizes(g, upper)
    L *= reach
    r = min(r, L * 0.72)  # (the bracket stops short of the slab's end)
    left = x - a - (L if side in ("both", "left") else 0)
    right = x + a + (L if side in ("both", "right") else 0)
    # a lowercase head serif slopes a little, higher at the stem
    drop = 0 if upper or side == "both" else h * 0.35
    serif_part(g, polygon([(left, y - h - drop), (right, y - h), (right, y), (left, y - drop)]))
    if side in ("both", "left"):
        fillet(g, (x - a, y - h - drop * 0.2), -1, -1, r)
    if side in ("both", "right"):
        fillet(g, (x + a, y - h), 1, -1, r)


def arm(g, x, y0, y1, upper=True):
    """an upright serif at an arm's end: its outer edge at x, from y0 to y1"""
    if not on():
        return
    P = g.P
    t = (P.ustem if upper else P.stem) * 0.66
    lo, hi = min(y0, y1), max(y0, y1)
    serif_part(g, polygon([(x - t, lo), (x, lo), (x, hi), (x - t, hi)]))


def arm_length(g, upper=True):
    P = g.P
    return (P.C if upper else P.X) * 0.13 + (P.uhair if upper else P.hair)


def ball(g, st, start=False):
    """a round end on a curved stroke (a, c, f, j and r): a dot hanging
    into the curve's inside, its outer edge running on from the stroke's"""
    if not on():
        return
    P = g.P
    # the end, the point before it, and a point further back (on the
    # curve's inside: the curve's far end, or the one before a straight end)
    segs = st.segs
    if start:
        seg = segs[0]
        p, q = seg[1], seg[2]
        far = seg[-1] if seg[0] == "C" else (segs[1][-1] if len(segs) > 1 else None)
    else:
        seg = segs[-1]
        p, q = seg[-1], seg[-2]
        far = seg[1] if seg[0] == "C" else (segs[-2][1] if len(segs) > 1 else None)
    if far is None:
        return
    dx, dy = p[0] - q[0], p[1] - q[1]
    length = (dx * dx + dy * dy) ** 0.5 or 1
    dx, dy = dx / length, dy / length  # out of the stroke, along it
    nx, ny = -dy, dx
    if nx * (far[0] - p[0]) + ny * (far[1] - p[1]) < 0:
        nx, ny = -nx, -ny
    # the stroke's half-width there (the pen's reach across its way)
    half = ((P.a * nx) ** 2 + (P.b * ny) ** 2) ** 0.5
    r = max(P.stem * P.t(0.58, 0.56, 0.5), half * 1.15)
    # its edge on the stroke's outer edge, which runs on into it unbroken
    hang = r - half
    g.dot(p[0] + nx * hang, p[1] + ny * hang, r)


def end(g, c, y, upper=False, reach=0.8):
    """a level slab across a diagonal's end: c the stroke's centre there,
    y the end's height (a foot if it's the bottom, else a head)"""
    if not on():
        return
    a, h, L, r = sizes(g, upper)
    w = a * 0.9 + L * reach * 0.75
    if y > 0:
        serif_part(g, polygon([(c[0] - w, y - h), (c[0] + w, y - h), (c[0] + w, y), (c[0] - w, y)]))
    else:
        serif_part(g, polygon([(c[0] - w, y), (c[0] + w, y), (c[0] + w, y + h), (c[0] - w, y + h)]))
