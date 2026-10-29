#!/usr/bin/env python3
"""Draw specimen.png: each of the five families, from the fonts in
fonts/ttf, through Pango (as the desktop draws text).

    tools/specimen.py [OUT.png]

Needs PyGObject with Pango and cairo (Ubuntu: python3-gi, gir1.2-pango-1.0,
python3-gi-cairo).
"""

import os
import sys
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "specimen.png"

# fontconfig that sees these fonts, and the system's for everything else
conf = tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False)
conf.write('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig>'
           f'<dir>{here / "fonts" / "ttf"}</dir>'
           '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
           f'<cachedir>{tempfile.mkdtemp()}</cachedir></fontconfig>')
conf.close()
os.environ["FONTCONFIG_FILE"] = conf.name

import gi  # noqa: E402

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
import cairo  # noqa: E402
from gi.repository import Pango, PangoCairo  # noqa: E402

FAMILIES = [
    ("PatroneOS Sans", "the system font",
     "Settings, Files, Wi-Fi and Bluetooth: everything on the desktop.",
     "Light, Regular, SemiBold, Bold, ExtraBold, with italics"),
    ("PatroneOS Mono", "the console font",
     "$ ls -l ~/Projects  # Il1| 0O {} [] => 2026-10-29",
     "Light, Regular, Bold, with italics · box drawing ┌─┐ ▁▃▅▇"),
    ("PatroneOS Document", "for documents",
     "Annual Report 2026: revenue rose 14.6% to $3,481,200.",
     "Regular, Bold, with italics"),
    ("PatroneOS Serif", "for serif text",
     "The quick brown fox jumps over the lazy dog, again.",
     "Regular, Bold, with italics"),
    ("PatroneOS Classic", "a plain, classic sans",
     "Sphinx of black quartz, judge my vow. Handgloves 0123456789",
     "Regular, Bold, with italics"),
]
W, ROW = 1600, 210
INK, SOFT, LINE = (0.11, 0.12, 0.14), (0.42, 0.45, 0.5), (0.88, 0.89, 0.91)

opt = cairo.FontOptions()
opt.set_antialias(cairo.ANTIALIAS_GRAY)
opt.set_hint_style(cairo.HINT_STYLE_SLIGHT)
opt.set_hint_metrics(cairo.HINT_METRICS_OFF)


def show(cr, x, y, desc, markup, colour=INK):
    layout = PangoCairo.create_layout(cr)
    PangoCairo.context_set_font_options(layout.get_context(), opt)
    PangoCairo.context_set_resolution(layout.get_context(), 96)
    layout.set_font_description(Pango.FontDescription.from_string(desc))
    layout.set_markup(markup, -1)
    cr.set_source_rgb(*colour)
    cr.move_to(x, y)
    PangoCairo.show_layout(cr, layout)


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


surface = cairo.ImageSurface(cairo.FORMAT_RGB24, W, 40 + ROW * len(FAMILIES))
cr = cairo.Context(surface)
cr.set_source_rgb(1, 1, 1)
cr.paint()
for i, (family, role, sample, styles) in enumerate(FAMILIES):
    y = 30 + i * ROW
    if i:
        cr.set_source_rgb(*LINE)
        cr.rectangle(60, y - 14, W - 120, 1)
        cr.fill()
    show(cr, 60, y, f"{family} Bold 26", f"{esc(family)}")
    show(cr, 60, y + 46, f"{family} 13", f"{esc(role)} · {esc(styles)}", SOFT)
    show(cr, 60, y + 80, f"{family} 24", esc(sample))
    show(cr, 60, y + 128, f"{family} Italic 20", esc(sample))
surface.write_to_png(str(out))
print(out)
