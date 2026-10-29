#!/usr/bin/env python3
"""Finish PatroneOS's static fonts after fontmake and ttfautohint.

- Adds a STAT table (weight, and italic for the italics), so the family's
  styles are named alike everywhere.
- Gives the family's styles the same clipping metrics, covering every glyph.
- Drops the Macintosh names (every current system reads the other set),
  and checks that every name left is PatroneOS's own: its family, its
  copyright, its designer, its licence.

    finish_static.py FONT.ttf...
"""

import re
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont

NAMES = {300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}
STYLES = set(NAMES.values()) | {"Italic"} | {f"{n} Italic" for n in NAMES.values()}
DESIGNER = "William Daugherty"
LICENSE_URL = "https://openfontlicense.org"


def own_name(record):
    """whether a name record says only what a PatroneOS font should"""
    text = record.toUnicode()
    if record.nameID in (2, 17):
        return text in STYLES
    if record.nameID == 5:
        return re.fullmatch(r"Version \d+\.\d+.*", text) is not None
    if record.nameID == 9:
        return text == DESIGNER
    if record.nameID == 13:
        return text.startswith("This Font Software is licensed under the SIL Open Font License, Version 1.1.")
    if record.nameID == 14:
        return text == LICENSE_URL
    return "patroneos" in text.lower()


def main():
    status = 0
    # systems clip what reaches past the win metrics: they cover every glyph
    # of the family (accented capitals included), alike in each style
    top = bottom = 0
    for path in sys.argv[1:]:
        head = TTFont(path)["head"]
        top, bottom = max(top, head.yMax), max(bottom, -head.yMin)
    for path in sys.argv[1:]:
        font = TTFont(path)
        weight = font["OS/2"].usWeightClass
        italic = bool(font["OS/2"].fsSelection & 1)
        axes = [
            {"tag": "wght", "name": "Weight",
             "values": [{"value": weight, "name": NAMES.get(weight, str(weight)),
                         "flags": 0x2 if weight == 400 else 0,
                         **({"linkedValue": 700} if weight == 400 else {})}]},
            {"tag": "ital", "name": "Italic",
             "values": [{"value": 1, "name": "Italic"} if italic else
                        {"value": 0, "name": "Roman", "flags": 0x2, "linkedValue": 1}]},
        ]
        buildStatTable(font, axes, elidedFallbackName="Regular")
        font["head"].flags |= 1 << 3  # hinted: whole pixels per em
        os2 = font["OS/2"]
        os2.usWinAscent = max(os2.usWinAscent, top)
        os2.usWinDescent = max(os2.usWinDescent, bottom)
        font["name"].names = [r for r in font["name"].names if r.platformID != 1]
        for record in font["name"].names:
            # (the STAT table's own names are style and axis names)
            if record.nameID >= 256:
                continue
            if not own_name(record):
                print(f"{path}: name {record.nameID} says {record.toUnicode()!r}")
                status = 1
        font.save(path)
    print(f"finished {len(sys.argv) - 1} fonts")
    sys.exit(status)


if __name__ == "__main__":
    main()
