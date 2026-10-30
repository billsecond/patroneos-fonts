"""PatroneOS's five font families: their heights, weights and the letter
shapes that set each apart. Each draws with the same engine and the same
letters; the numbers here make them five different fonts."""

from glyph import Family

SANS_WEIGHTS = [("Light", 300), ("Regular", 400), ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800)]
TWO_WEIGHTS = [("Regular", 400), ("Bold", 700)]

FAMILIES = {f.key: f for f in [
    # the system font: open, narrow and calm, made for interface text at
    # small sizes, its strokes thinning where they join
    Family("sans", "PatroneOS Sans", x=500, cap=700, asc=740, desc=-230,
           masters=SANS_WEIGHTS, italics=True, slant=11,
           spacing={"Light": 1.16, "Regular": 1.21, "SemiBold": 1.24, "Bold": 1.13, "ExtraBold": 0.94},
           weight={"Light": 0.80, "Regular": 0.952, "SemiBold": 0.915, "Bold": 1.095, "ExtraBold": 1.294},
           width={"Light": 1.0, "Regular": 1.0, "SemiBold": 0.9, "Bold": 0.8, "ExtraBold": 0.76},
           contrast={"Light": 1.05, "Regular": 0.99, "SemiBold": 1.02, "Bold": 0.98, "ExtraBold": 0.94},
           upper_width={"Light": 0.91, "Regular": 0.91, "SemiBold": 0.93, "Bold": 0.96, "ExtraBold": 0.96},
           join=0.86, caps=0.965, ends="upright", t_top=26, space=275, figures=1.1, humanist=True),
    # the console font: one width, slabs where narrow letters need them
    Family("mono", "PatroneOS Mono", x=518, cap=693, asc=745, desc=-240,
           masters=[("Light", 300), ("Regular", 400), ("Bold", 700)], italics=True, slant=10,
           weight={"Light": 1.1, "Regular": 1.18, "Bold": 1.1}, one_foot=True, mono=1200 * 1000 / 2048),
    # the document font: narrow, warm, a small x-height and long ascenders
    Family("document", "PatroneOS Document", x=478, cap=642, asc=725, desc=-235,
           masters=TWO_WEIGHTS, italics=True, slant=7, weight=0.89, contrast=1.02, t_top=18,
           spacing=1.22, figures=0.82, kern=0.6),
    # both serif jobs
    Family("serif", "PatroneOS Serif", x=519, cap=729, asc=760, desc=-236,
           masters=TWO_WEIGHTS, italics=True, slant=11, weight={"Regular": 1.1, "Bold": 0.98},
           contrast=0.8, serif=True, ends="square", g="double", one_foot=True, width=1.0,
           spacing=1.32, match_widths=False, space=300),
    # the classic sans: even, closed apertures, level and square cuts
    Family("classic", "PatroneOS Classic", x=528, cap=688, asc=716, desc=-210,
           masters=TWO_WEIGHTS, italics=True, slant=12, weight=1.1, contrast=1.1, ends="square",
           aperture=1.3, a="spur", dots="square", t_top=34, G_spur=True, k_bias=0.02),
]}

# the named weights each family is built in
INSTANCES = {
    "sans": [("Light", 300), ("Regular", 400), ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800)],
    "mono": [("Light", 300), ("Regular", 400), ("Bold", 700)],
    "document": TWO_WEIGHTS,
    "serif": TWO_WEIGHTS,
    "classic": TWO_WEIGHTS,
}
