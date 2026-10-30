#!/usr/bin/env python3
"""Draw one of PatroneOS's font families and write its masters as UFO
sources, with the designspace fontmake builds its fonts from.

    make_ufos.py OUT_DIR --family KEY [--italic]

KEY is one of families.FAMILIES. Each glyph's counters are fitted so its
advance comes out at the family's width for it, where the family has
one; the font is written at the family's units per em, with its vertical
metrics; italics are the uprights slanted.
"""

import copy
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ufoLib2  # noqa: E402

import engine  # noqa: E402
import glyph as G  # noqa: E402
from families import FAMILIES, INSTANCES  # noqa: E402

MARKS = set()  # the combining marks, for GDEF
UPRIGHT = set()  # glyphs the italics don't slant (box drawing)


def load_glyphs():
    """the drawings register themselves when imported (after the family is
    chosen: some read it as they're registered)"""
    import lower  # noqa: F401
    import upper  # noqa: F401
    import figures  # noqa: F401
    import punct  # noqa: F401
    import boxes  # noqa: F401
    import marks  # noqa: F401
    if G.STYLE.humanist:
        import humanist
        humanist.install()
    import composites
    composites.add_composites()


# ---------------------------------------------------------------- drawing


def with_counter(master, fit):
    if fit == 1.0:
        return master
    m = copy.copy(master)
    m.counter = master.counter * fit
    return m


def draw_one(master, name, upper, f, out, fit=1.0):
    g = G.Draw(with_counter(master, fit * (master.upper_width if upper else 1.0)), name, upper=upper)
    g.glyphs = out
    f(g)
    return g


def lighter(master, k):
    """the master with strokes k times as heavy"""
    m = copy.copy(master)
    m.stem, m.hair, m.ustem, m.uhair = master.stem * k, master.hair * k, master.ustem * k, master.uhair * k
    m.a, m.b, m.ua, m.ub = m.stem / 2, m.hair / 2, m.ustem / 2, m.uhair / 2
    m.nib, m.unib = engine.Nib(m.a, m.b), engine.Nib(m.ua, m.ub)
    return m


def box_width(g):
    box = engine.bounds(list(g.contours) + [c for st in g.strokes for c in st.outline()])
    return box[2] - box[0] if box else 0


def fitted(master, name, unicodes, upper, f, out):
    """the glyph fitted to its target advance (fit_counters); in one-width
    fonts, a letter still wider than its cell with its counters at their
    narrowest (m and w in the heavier weights) is drawn with lighter
    strokes until it fits"""
    g, target = fit_counters(master, name, unicodes, upper, f, out)
    from figures import FIGURES  # (imported after the family is chosen, with the drawings)
    if not G.STYLE.mono and g.advance and not g.components and name in FIGURES:
        g = figure_in_column(master, name, upper, f, out, g)
    if target is not None and G.STYLE.mono:
        for k in (0.94, 0.88, 0.82, 0.76):
            n = g.natural()
            if n is None or n <= target + 1 or box_width(g) <= target - 16:
                break
            g, target = fit_counters(lighter(master, k), name, unicodes, upper, f, out)
    return g, target


FIGURE_MARGIN = 12  # (design units)


def figure_in_column(master, name, upper, f, out, g):
    """a tabular figure wider than its column (in the heavy weights) redrawn
    with narrower counters, its strokes as they are, until it sits inside
    with a margin each side, so neighbouring figures never touch"""
    if box_width(g) <= g.advance:
        return g
    room = g.advance - 2 * FIGURE_MARGIN
    fit = 1.0
    while box_width(g) > room and fit > 0.6:
        fit -= 0.02
        g = draw_one(master, name, upper, f, out, fit)
    return g


def fit_counters(master, name, unicodes, upper, f, out):
    """the glyph drawn with its counters widened or narrowed until its own
    spacing gives the target advance (as near as counters can)"""
    target = master.target(unicodes)
    g = draw_one(master, name, upper, f, out)
    if target is None:
        return g, None
    n0 = g.natural()
    if n0 is None:
        return g, target
    # (a glyph may widen less: in one-width fonts, narrow letters stay
    # narrow, their spare room going to their sides; or narrow more, as
    # W must to fit its cell)
    most, least = getattr(g, "max_fit", 1.9), getattr(g, "min_fit", 0.45)
    f0, f1 = 1.0, 1.0 + (target - n0) / max(n0 * 0.6, 1)
    f1 = min(most, max(least, f1))
    best = (abs(target - n0), 1.0, g)
    for _ in range(4):
        try:
            g1 = draw_one(master, name, upper, f, out, f1)
            n1 = g1.natural()
        except ValueError:
            break  # squeezed this far, the shape no longer draws: keep the last that did
        if n1 is None:
            break
        if abs(target - n1) < best[0]:
            best = (abs(target - n1), f1, g1)
        if abs(target - n1) < 1 or abs(n1 - n0) < 0.5:
            break
        f0, n0, f1 = f1, n1, f1 + (target - n1) * (f1 - f0) / (n1 - n0)
        f1 = min(most, max(least, f1))
    return best[2], target


def plan_pieces():
    """draw every master until every outline follows its centre line
    closely enough, splitting the curves that don't (engine.PIECES)"""
    if getattr(plan_pieces, "done", False):
        return
    for _ in range(4):
        engine.ERRORS.clear()
        for master in G.MASTERS:
            _draw(master)
        more = {k for k, e in engine.ERRORS.items() if e > engine.TOLERANCE}
        if not more:
            break
        for key in more:
            engine.PIECES[key] = engine.PIECES.get(key, 1) + 1
    plan_pieces.done = True


def drawn(master):
    plan_pieces()
    return _draw(master)


def _draw(master):
    """every glyph drawn for one master: name -> (unicodes, contours,
    components, advance, anchors)"""
    out = {}
    for name, (unicodes, upper, f) in G.GLYPHS.items():
        g, target = fitted(master, name, unicodes, upper, f, out)
        if getattr(g, "mark", False):
            MARKS.add(name)
        if getattr(g, "upright", False):
            UPRIGHT.add(name)
        contours, advance, anchors, _ = g.finish(target if not g.components else None)
        if G.STYLE.mono and not g.components and not getattr(g, "upright", False):
            contours, anchors = in_cell(contours, anchors, advance)
        out[name] = (unicodes, contours, g.components, advance, anchors)
    return out


MONO_MARGIN = 12  # (design units)


def in_cell(contours, anchors, advance):
    """in a one-width font, a glyph still wider than its cell (a symbol
    drawn wide: an arrow, ©, the em dash) narrowed about its middle to fit,
    a small margin each side; zero-width accents are left as they are"""
    box = engine.bounds(contours)
    room = advance - 2 * MONO_MARGIN
    if advance <= 0 or box is None or box[2] - box[0] <= room:
        return contours, anchors
    k = room / (box[2] - box[0])
    mid = (box[0] + box[2]) / 2

    def squeeze(p):
        return (advance / 2 + (p[0] - mid) * k, p[1])
    return ([engine.transform(c, squeeze) for c in contours],
            {key: squeeze(p) for key, p in anchors.items()})


# ---------------------------------------------------------------- writing


def write_glyph(font, name, unicodes, contours, components, advance, anchors, scale, slant):
    """the glyph at the font's units per em, slanted about the middle of
    the x-height for italics"""
    gl = font.newGlyph(name)
    gl.width = round(advance * scale)
    gl.unicodes = unicodes
    tan = math.tan(math.radians(slant))
    mid = G.Master.X / 2

    def t(p):
        return (round((p[0] + (p[1] - mid) * tan) * scale), round(p[1] * scale))

    pen = gl.getPen()
    for contour in contours:
        start = t(contour[0][1])
        pen.moveTo(start)
        for i, seg in enumerate(contour):
            end = start if i == len(contour) - 1 else t(seg[-1])
            if seg[0] == "L":
                pen.lineTo(end)
            else:
                pen.curveTo(t(seg[2]), t(seg[3]), end)
        pen.closePath()
    for base, dx, dy in components:
        pen.addComponent(base, (1, 0, 0, 1, round((dx + dy * tan) * scale), round(dy * scale)))
    for key, (x, y) in anchors.items():
        ax, ay = t((x, y))
        gl.appendAnchor({"name": key, "x": ax, "y": ay})
    return gl


YEAR = 2026
COPYRIGHT = f"Copyright {YEAR} William Daugherty (https://github.com/billsecond/patroneos)"
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
VERSION = (1, 100)  # (fonts count thousandths: 1.100 is release 1.1.0)


def description(fam):
    return (f"{fam.family} is one of PatroneOS's font families, drawn from scratch with AI help: "
            "every letter is a pen stroke along a skeleton, outlined by PatroneOS's own code.")


def style_name(master_name, italic):
    if not italic:
        return master_name
    return "Italic" if master_name == "Regular" else f"{master_name} Italic"


def master_font(master, fam, italic, win):
    font = ufoLib2.Font()
    info = font.info
    m = fam.metrics
    scale = fam.upm / 1000
    info.familyName = fam.family
    info.styleName = style_name(master.name, italic)
    info.versionMajor, info.versionMinor = VERSION
    info.copyright = COPYRIGHT
    info.unitsPerEm = fam.upm
    info.xHeight = round(G.Master.X * scale)
    info.capHeight = round(G.Master.C * scale)
    info.ascender = round(G.Master.A * scale)
    info.descender = round(G.Master.D * scale)
    info.openTypeHheaAscender = m["hheaAscender"]
    info.openTypeHheaDescender = m["hheaDescender"]
    info.openTypeHheaLineGap = m["hheaLineGap"]
    # the typo metrics are the hhea ones, so every system spaces lines alike
    info.openTypeOS2TypoAscender = m["hheaAscender"]
    info.openTypeOS2TypoDescender = m["hheaDescender"]
    info.openTypeOS2TypoLineGap = m["hheaLineGap"]
    info.openTypeOS2WinAscent = max(m["winAscent"], win[0])
    info.openTypeOS2WinDescent = max(m["winDescent"], win[1])
    info.openTypeOS2Selection = [7] if m["useTypoMetrics"] else []
    info.openTypeOS2Type = []  # installable
    info.openTypeOS2VendorID = "PTRN"
    info.openTypeOS2WeightClass = master.wght
    info.openTypeOS2StrikeoutPosition = m["strikeoutPosition"]
    info.openTypeOS2StrikeoutSize = m["strikeoutSize"]
    info.postscriptUnderlinePosition = m["underlinePosition"]
    info.postscriptUnderlineThickness = m["underlineThickness"]
    if italic:
        info.italicAngle = -fam.slant
    if fam.mono:
        info.postscriptIsFixedPitch = True
        info.openTypeOS2Panose = [2, 11, 5, 9, 2, 2, 4, 2, 2, 4]
    info.openTypeNameDesigner = "William Daugherty"
    info.openTypeNameManufacturer = "PatroneOS"
    info.openTypeNameManufacturerURL = "https://github.com/billsecond/patroneos"
    info.openTypeNameDescription = description(fam)
    info.openTypeNameLicense = LICENSE
    info.openTypeNameLicenseURL = "https://openfontlicense.org"
    slant = fam.slant if italic else 0
    for name, (unicodes, contours, components, advance, anchors) in drawn(master).items():
        write_glyph(font, name, unicodes, contours, components, advance, anchors, scale,
                    0 if name in UPRIGHT else slant)
    font.glyphOrder = list(G.GLYPHS)
    font.lib["public.openTypeCategories"] = {
        name: ("mark" if name in MARKS else "base") for name in G.GLYPHS
    }
    font.features.text = features()
    import kerning
    if not fam.mono:  # (kerning would knock a one-width font out of its columns)
        kerning.apply(font, master)
    for pair in list(font.kerning):
        font.kerning[pair] = round(font.kerning[pair] * scale * fam.kern)
    return font


def features():
    """dotless i and j under accents, and the capitals' accents after
    capitals (mark and kern come from anchors and kerning)"""
    above = sorted(n for n in MARKS if n + ".case" in G.GLYPHS)
    upper = [n for n, (u, up, f) in G.GLYPHS.items() if up and u and chr(u[0]).isalpha()]
    return f"""languagesystem DFLT dflt;
languagesystem latn dflt;

@MarkAbove = [{" ".join(above)}];
@MarkAboveCase = [{" ".join(n + ".case" for n in above)}];
@Upper = [{" ".join(upper)}];

feature ccmp {{
    lookup dotless {{
        sub i' @MarkAbove by dotlessi;
        sub j' @MarkAbove by dotlessj;
    }} dotless;
    lookup case_marks {{
        sub @Upper @MarkAbove' by @MarkAboveCase;
    }} case_marks;
}} ccmp;
"""


def ps_family(fam):
    return fam.family.replace(" ", "")


def designspace(out, fam, italic):
    from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor
    doc = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.tag, axis.name = "wght", "Weight"
    weights = [w for _, w in fam.masters]
    axis.minimum, axis.default, axis.maximum = min(weights), 400, max(weights)
    doc.addAxis(axis)
    for master in G.MASTERS:
        src = SourceDescriptor()
        src.filename = f"{ps_family(fam)}-{style_name(master.name, italic).replace(' ', '')}.ufo"
        src.familyName, src.styleName = fam.family, style_name(master.name, italic)
        src.location = {"Weight": master.wght}
        doc.addSource(src)
    for name, wght in INSTANCES[fam.key]:
        inst = InstanceDescriptor()
        inst.familyName, inst.styleName = fam.family, style_name(name, italic)
        inst.location = {"Weight": wght}
        if name in ("Regular", "Bold"):
            inst.styleMapFamilyName = fam.family
            inst.styleMapStyleName = (name.lower() + (" italic" if italic else "")).replace("regular italic",
                                                                                           "italic")
        else:
            inst.styleMapFamilyName = f"{fam.family} {name}"
            inst.styleMapStyleName = "italic" if italic else "regular"
        inst.postScriptFontName = f"{ps_family(fam)}-{style_name(name, italic).replace(' ', '')}"
        inst.filename = f"instances/{inst.postScriptFontName}.ufo"
        doc.addInstance(inst)
    doc.write(out / f"{ps_family(fam)}{'-Italic' if italic else ''}.designspace")


def win_metrics(all_drawn, scale):
    top = bottom = 0
    for drawn_master in all_drawn:
        for unicodes, contours, components, advance, anchors in drawn_master.values():
            box = engine.bounds(contours)
            if box:
                bottom, top = min(bottom, box[1]), max(top, box[3])
    return round(top * scale) + 10, round(-bottom * scale) + 10


def main():
    out = Path(sys.argv[1])
    fam = FAMILIES[sys.argv[sys.argv.index("--family") + 1]]
    italic = "--italic" in sys.argv
    G.use_family(fam, italic)
    load_glyphs()
    out.mkdir(parents=True, exist_ok=True)
    plan_pieces()
    win = win_metrics([_draw(m) for m in G.MASTERS], fam.upm / 1000)
    for master in G.MASTERS:
        name = f"{ps_family(fam)}-{style_name(master.name, italic).replace(' ', '')}.ufo"
        master_font(master, fam, italic, win).save(out / name, overwrite=True)
    designspace(out, fam, italic)
    print(f"{out}: {fam.family}{' italic' if italic else ''}, {len(G.GLYPHS)} glyphs, "
          f"{len(G.MASTERS)} masters, glyphs reach {win}")


if __name__ == "__main__":
    main()
