#!/usr/bin/env bash
# Builds PatroneOS's five font families from their drawing code (source/):
# each family's upright and italic masters drawn and written as UFO sources,
# its named weights compiled as static TrueType fonts with overlaps removed,
# hinted by ttfautohint, finished (tools/finish_static.py), checked by
# fontbakery, and saved as WOFF2 for the web.
#
#   ./build.sh                 every family, checked
#   ./build.sh mono serif      only those families
#   ./build.sh --no-check      without fontbakery
#   ./build.sh --zip           and the release zip, in dist/
#
# The fonts land in fonts/ttf/PatroneOS-FAMILY/ and fonts/webfonts/.
#
# Needs python3 and curl, and the network the first time: the tools go into
# a venv in a cache folder ($PATRONEOS_FONTS_CACHE, by default
# ~/.cache/patroneos-fonts). No sudo. The fonts' dates are the drawing
# code's last commit's, so a rebuild of a commit gives the same fonts.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
cache=${PATRONEOS_FONTS_CACHE:-$HOME/.cache/patroneos-fonts}
version=$(cat "$here/VERSION")
check=1
zip=0
families=()
for arg; do
    case $arg in
        --no-check) check=0 ;;
        --zip) zip=1 ;;
        -*) echo "Unknown option: $arg" >&2; exit 1 ;;
        *) families+=("$arg") ;;
    esac
done
(( ${#families[@]} )) || families=(sans mono document serif classic)
declare -A names=([sans]=Sans [mono]=Mono [document]=Document [serif]=Serif [classic]=Classic)

mkdir -p "$cache"
venv=$cache/venv
if [[ ! -x $venv/bin/pip ]]; then
    # Without Ubuntu's python3-venv there's no ensurepip, so pip comes from
    # the Python Packaging Authority's installer instead (no sudo needed)
    python3 -m venv --without-pip "$venv"
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$cache/get-pip.py"
    "$venv/bin/python" "$cache/get-pip.py" --quiet
fi
"$venv/bin/pip" install --quiet -r "$here/requirements.txt"
python=$venv/bin/python

SOURCE_DATE_EPOCH=$(git -C "$here" log -1 --format=%ct -- source tools 2>/dev/null || true)
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-$(date +%s)}
export SOURCE_DATE_EPOCH

work=$cache/build
mkdir -p "$work" "$here/fonts/webfonts"

run() {
    local log=$1
    shift
    if ! "$@" > "$log" 2>&1; then
        tail -40 "$log" >&2
        echo "Failed: $* (the whole log is $log)" >&2
        exit 1
    fi
}

for family in "${families[@]}"; do
    name=${names[$family]:-}
    [[ -n $name ]] || { echo "Unknown family: $family (one of: ${!names[*]})" >&2; exit 1; }
    out=$here/fonts/ttf/PatroneOS-$name
    compiled=$work/ttf-$family
    rm -rf "$compiled" "$out" "$here/fonts/webfonts/PatroneOS$name-"*.woff2
    mkdir -p "$compiled" "$out"
    for slant in "" --italic; do
        ufo=$work/$family${slant:+-italic}
        rm -rf "$ufo"
        echo "PatroneOS $name${slant:+ italic}: drawing and compiling"
        run "$ufo.log" "$python" "$here/source/make_ufos.py" "$ufo" --family "$family" $slant
        run "$ufo.fontmake.log" "$venv/bin/fontmake" -m "$ufo"/*.designspace -i -o ttf \
            --output-dir "$compiled"
    done
    echo "PatroneOS $name: hinting and finishing"
    for font in "$compiled"/*.ttf; do
        run "$work/hint.log" "$python" -m ttfautohint --no-info "$font" "$out/$(basename "$font")"
    done
    run "$work/finish.log" "$python" "$here/tools/finish_static.py" "$out"/*.ttf
    for font in "$out"/*.ttf; do
        run "$work/woff2.log" "$python" -m fontTools.ttLib.woff2 compress \
            -o "$here/fonts/webfonts/$(basename "${font%.ttf}").woff2" "$font"
    done
    if (( check )); then
        # (less two checks that aren't about the fonts: an online name
        # lookup, and a list of the family's files)
        report=$work/fontbakery-$family.txt
        "$venv/bin/fontbakery" check-universal --succinct --no-colors --loglevel WARN \
            -x fontdata_namecheck -x superfamily/list "$out"/*.ttf 2> /dev/null > "$report" || true
        echo "PatroneOS $name, fontbakery:$(tail -1 "$report") (the report is $report)"
        if ! tail -1 "$report" | grep -q 'ERROR: 0 FATAL: 0 FAIL: 0'; then
            echo "fontbakery found errors or failures in PatroneOS $name" >&2
            exit 1
        fi
    fi
done

if (( zip )); then
    # The five families' fonts, their licence and their log
    top=PatroneOS-Fonts-$version
    stage=$work/zip/$top
    rm -rf "$work/zip"
    mkdir -p "$stage" "$here/dist"
    cp -r "$here"/fonts/ttf/PatroneOS-* "$stage/"
    cp "$here/OFL.txt" "$here/FONTLOG.txt" "$stage/"
    find "$stage" -exec touch -d "@$SOURCE_DATE_EPOCH" {} +
    rm -f "$here/dist/$top.zip"
    (cd "$work/zip" && find "$top" -type f | LC_ALL=C sort | zip -q -X -@ "$here/dist/$top.zip")
    echo "The release zip: dist/$top.zip"
fi
