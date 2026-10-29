"""Glyphs: what a letter's drawing gives, and the masters' numbers.

A glyph function gets a Draw for one master and draws with its numbers:
strokes (engine.Stroke), filled shapes, components and anchors. Draw then
outlines the strokes and spaces the glyph: its sides' sidebearings come
from what they are (a straight stem, a round, a diagonal), as multiples of
the master's own, so spacing follows the weight.
"""

from engine import Nib, Stroke, bounds, ellipse, transform

GLYPHS = {}  # name: (unicodes, upper, function), in drawing order


def glyph(name, *unicodes, upper=False):
    """register a glyph's drawing; upper ones use the capitals' pen and
    sidebearings"""

    def register(f):
        GLYPHS[name] = (list(unicodes), upper, f)
        return f

    return register


# ---------------------------------------------------------------- families


class Family:
    """One of PatroneOS's font families: what sets it apart, the same in
    every weight. Heights are in design units (1000 to the em); the font is
    written at upm. widths: the advance widths it matches, by style and
    code point (metrics/KEY.json), so text lays out the same. weight: its
    stems against the base weights; width, spacing, contrast: counters,
    sidebearings, level strokes' weight; k_bias: rounder (below 0) or
    squarer curves; ends: how curved strokes end (tilt, level or square);
    aperture: how far round c, e and s close; g, y, a: single- or
    double-storey g, straight or curved y tail, a with or without a spur;
    dots: round or square; t_top: t's top cut; one_foot: a foot on 1;
    G_spur: a spur on G; mono: one width for everything; serif: serifs;
    figures: the figures' counters against the letters' (narrower figures,
    more room between them); kern: the kerning's strength; match_widths:
    whether its widths match the family it stands in for (metrics/KEY.json);
    space: its word space, where it doesn't take the matched one."""

    def __init__(self, key, name, x, cap, asc, desc, masters, italics, slant, weight=1.0, width=1.0,
                 spacing=1.0, contrast=1.0, k_bias=0.0, ends="tilt", tilt=1.0, aperture=1.0, g="single",
                 y="straight", a="plain", dots="round", t_top=24, one_foot=False, G_spur=False,
                 mono=None, serif=False, figures=1.0, kern=1.0, match_widths=True, space=None,
                 upm=2048):
        self.key, self.family = key, name
        self.x, self.cap, self.asc, self.desc = x, cap, asc, desc
        self.masters, self.italics, self.slant = masters, italics, slant
        self.weight, self.width, self.spacing, self.contrast = weight, width, spacing, contrast
        self.k_bias, self.ends, self.tilt, self.aperture = k_bias, ends, tilt, aperture
        self.g, self.y, self.a, self.dots, self.t_top = g, y, a, dots, t_top
        self.one_foot, self.G_spur, self.mono, self.serif, self.upm = one_foot, G_spur, mono, serif, upm
        self.figures, self.kern, self.match_widths, self.space = figures, kern, match_widths, space
        self.metrics, self.widths = {}, {}

    def load(self):
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parent / "metrics" / f"{self.key}.json"
        if path.exists():
            data = json.load(open(path))
            self.metrics = data["metrics"]
            self.widths = {style: {int(k): v for k, v in d["widths"].items()}
                           for style, d in data["styles"].items()}
        return self


STYLE = None  # the family being drawn


def ends(tilt):
    """how a curved stroke's end is cut in this family (arguments for
    Stroke and its end): tilt is how far towards upright, where the family
    turns cuts that way"""
    if STYLE.ends == "square":
        return {}
    if STYLE.ends == "level":
        return {"tilt": -90}
    return {"tilt": tilt * STYLE.tilt}


# ---------------------------------------------------------------- masters

# the base numbers, at weights 300, 400 and 900: between and beyond them
# they're drawn straight through
BASE = {
    "stem": (56, 84, 180), "hair": (50, 72, 138), "ustem": (60, 90, 190), "uhair": (52, 76, 146),
    "sb": (70, 66, 50), "usb": (84, 80, 62), "counter": (1.05, 1.0, 0.80), "join": (0.68, 0.62, 0.52),
    "ov": (11, 12, 14),
}


def between(values, w):
    if isinstance(values[1], tuple):
        return tuple(between(v, w) for v in zip(*values))
    a, b, c = values
    if w <= 400:
        return a + (b - a) * (w - 300) / 100
    return b + (c - b) * (w - 400) / 500


class Master:
    """One master's numbers. Lowercase: stem (an upright stroke's weight),
    hair (a horizontal stroke's), sb (a straight side's sidebearing);
    capitals the same with u. counter scales counters (narrower in heavy
    weights, where the strokes take the room), join how thin a stroke gets
    where it leaves a stem."""

    X, C, A, D = 530, 710, 760, -230  # set for each family
    UPM = 1000

    def __init__(self, name, wght, italic=False):
        F = STYLE
        self.name, self.wght, self.italic = name, wght, italic
        v = {k: between(vals, wght) for k, vals in BASE.items()}
        # (a family's weight can differ by master: {master name: weight})
        weight = F.weight.get(name, 1.0) if isinstance(F.weight, dict) else F.weight
        self.stem, self.ustem = v["stem"] * weight, v["ustem"] * weight
        self.hair, self.uhair = v["hair"] * weight * F.contrast, v["uhair"] * weight * F.contrast
        self.sb, self.usb = v["sb"] * F.spacing, v["usb"] * F.spacing
        self.counter = v["counter"] * F.width
        self.join, self.ov = v["join"], v["ov"]
        self.uov = self.ov + 2
        self.a, self.b = self.stem / 2, self.hair / 2
        self.ua, self.ub = self.ustem / 2, self.uhair / 2
        self.nib = Nib(self.a, self.b)
        self.unib = Nib(self.ua, self.ub)
        # how much heavier a round's sides are than a stem
        self.rnd = 1.04
        # the fullness of round curves (0.552 is a circle's)
        self.k = 0.58
        style = name if not italic else ("Italic" if name == "Regular" else name + " Italic")
        self.widths = F.widths.get(style) or F.widths.get(name) or {}

    def target(self, unicodes):
        """the advance width this glyph matches, in design units, if any"""
        if STYLE.mono:
            return STYLE.mono
        if not STYLE.match_widths:
            return None
        for u in unicodes:
            if u in self.widths:
                return self.widths[u] * 1000 / STYLE.upm
        return None

    def cw(self, regular):
        """a counter's width: its regular width, for this weight"""
        return regular * self.counter

    def t(self, light, regular, black):
        """a number that depends on the weight, given at 300, 400 and 900"""
        return between((light, regular, black), self.wght)


MASTERS = []


def use_family(fam, italic=False):
    """draw this family from now on (its upright or its italic masters)"""
    global STYLE
    import engine
    STYLE = fam.load()
    Master.X, Master.C, Master.A, Master.D = fam.x, fam.cap, fam.asc, fam.desc
    engine.K_BIAS = fam.k_bias
    engine.DOT_K = 0.78 if fam.dots == "square" else 0.5523
    MASTERS[:] = [Master(name, wght, italic) for name, wght in fam.masters]


# ---------------------------------------------------------------- drawing


class Draw:
    def __init__(self, master, name, upper=False):
        self.P = master
        self.name = name
        self.upper = upper
        self.strokes = []
        self.contours = []
        self.components = []  # (glyph name, dx, dy)
        self.anchors = {}
        self.sides = (1.0, 1.0)
        self.advance = None  # a fixed advance (figures, spaces)
        self.centre = 0  # where an outline sits in a fixed advance, from its middle
        self.shift = 0  # where the outline lands, when spaced

    @property
    def nib(self):
        return self.P.unib if self.upper else self.P.nib

    def stroke(self, p, s=1.0, nib=None, cap=None, tilt=None):
        st = Stroke(p, nib or self.nib, s, cap, tilt)
        st.key = (self.name, len(self.strokes))
        self.strokes.append(st)
        return st

    def dot(self, cx, cy, r):
        self.contours.append(ellipse(cx, cy, r, r))

    def shape(self, contour):
        self.contours.append(contour)

    def component(self, name, dx=0, dy=0):
        self.components.append((name, dx, dy))

    def anchor(self, name, x, y):
        self.anchors[name] = (x, y)

    def space(self, left, right):
        """sidebearings, as multiples of the master's straight one"""
        self.sides = (left, right)

    def fixed(self, advance, centre=0):
        """a fixed advance (tabular figures), the outline in its middle"""
        self.advance = advance
        self.centre = centre

    def draw(self, name, master=None, dx=0, dy=0, upper=None):
        """draw another glyph's drawing in this one, moved by dx, dy (its
        own spacing ignored: it lands where its function draws it)"""
        unicodes, up, f = GLYPHS[name]
        sub = Draw(master or self.P, f"{self.name}/{name}", up if upper is None else upper)
        f(sub)
        k0 = len(self.strokes)
        for st in sub.strokes:
            st.key = (self.name, len(self.strokes))
            self.strokes.append(st)
        self.contours.extend(sub.contours)
        moved = lambda p: (p[0] + dx, p[1] + dy)  # noqa: E731
        self.transform_all(moved, start=k0, contours_from=len(self.contours) - len(sub.contours))
        return sub

    def transform_all(self, f, start=0, contours_from=0):
        """move or turn what's drawn (from stroke number start on)"""
        for st in self.strokes[start:]:
            st.points = [f(p) for p in st.points]
            st.segs = [(seg[0], *(f(p) for p in seg[1:])) for seg in st.segs]
        self.contours[contours_from:] = [transform(c, f) for c in self.contours[contours_from:]]

    def copy_of(self, name, dx=0, dy=0):
        """a glyph that is another one (a component), with its width"""
        self.component(name, dx, dy)
        self.advance = self.glyphs[name][3]

    # ---- the finished glyph

    def spacing_box(self, contours):
        """the outline's extent, as spacing sees it: serifs count half their
        reach, so they come nearer their neighbours than the stems do"""
        box = bounds(contours)
        parts = getattr(self, "serif_parts", None)
        if not parts or box is None:
            return box
        core = bounds([c for i, c in enumerate(self.contours) if i not in parts]
                      + [c for st in self.strokes for c in st.outline()])
        if core is None:
            return box
        return ((box[0] + core[0]) / 2, box[1], (box[2] + core[2]) / 2, box[3])

    def natural(self):
        """the glyph's own advance, from its spacing (None if it has a fixed
        one or no outline)"""
        if self.advance is not None or getattr(self, "keep_place", False):
            return None
        contours = list(self.contours) + [c for st in self.strokes for c in st.outline()]
        box = self.spacing_box(contours)
        if box is None:
            return None
        base = self.P.usb if self.upper else self.P.sb
        return base * (self.sides[0] + self.sides[1]) + box[2] - box[0]

    def finish(self, target=None):
        """outline, space and return (contours, advance, anchors); with a
        target, the advance is that, the sidebearings sharing what differs"""
        contours = list(self.contours)
        for st in self.strokes:
            contours.extend(st.outline())
        box = self.spacing_box(contours)
        base = self.P.usb if self.upper else self.P.sb
        if box is None:
            if target is not None and self.advance is not None and self.advance > 0:
                return [], target, dict(self.anchors), 0
            return [], self.advance or 0, dict(self.anchors), 0
        x0, _, x1, _ = box
        if getattr(self, "keep_place", False):
            dx, width = 0, self.advance
        elif self.advance is not None:
            adv = target if target is not None and self.advance > 0 else self.advance
            dx = (adv - (x1 - x0)) / 2 - x0 + self.centre
            width = adv
        else:
            left, right = base * self.sides[0], base * self.sides[1]
            width = left + (x1 - x0) + right
            if target is not None:
                extra = target - width
                share = left / (left + right) if left + right > 1 else 0.5
                left += extra * min(1, max(0, share))
                width = target
            dx = left - x0
        self.shift = dx
        contours = [transform(c, lambda p: (p[0] + dx, p[1])) for c in contours]
        anchors = {k: (x + dx, y) for k, (x, y) in self.anchors.items()}
        return contours, width, anchors, dx
