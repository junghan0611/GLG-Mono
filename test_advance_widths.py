#!/usr/bin/env python3
"""Guard the advance width of every glyph the Latin sources ship at zero.

Why this exists: hmtx stores advance widths only for the first `numberOfHMetrics`
glyphs, and every later glyph inherits the last stored value. FontForge 20251009 judges
a monospaced face compressible and writes `numberOfHMetrics=4`, so everything past index
4 inherits a half-width advance. Zero-width glyphs are destroyed — combining accents,
soft hyphen, ZWSP, line/paragraph separators, unencoded mark components. Outlines, glyph
names and cmap all survive unchanged, so only an advance-width check notices.
`font_widths.restore_advance_widths()` repairs each FontForge → TTF round-trip; this is
the guard for that repair.

The contract is stated over **glyph names, not codepoints**, and this matters. Roughly
half the casualties are unreachable from cmap: `breveacute` and friends are GSUB-only
mark components, and a codepoint-keyed test walks straight past them. A category filter
would lose more still — U+2028 is Zl, U+2029 is Zp, `.null` has no codepoint at all —
so nothing here filters on Unicode category. (The inherited-JP report below does, but it
is a report, not a gate.)

The contract mirrors what the build actually does. The Latin side is IBM Plex Mono plus
whatever Hack adds on top, and `delete_duplicate_glyphs()` then lets the Latin side win
over IBM Plex Sans JP — so any glyph the Latin side ships at advance 0 must still be 0
in the output. What Hack contributes depends on the mode, because `merge_hack()` clears
Hack glyphs that already exist elsewhere:

    Console      Hack fills whatever Plex Mono lacks (and outranks JP).
    non-Console  Hack fills only what neither Plex Mono nor JP has.

Style matters too, and not academically: Hack-Regular has no U+0305 or U+030D-U+0361,
while Hack-Bold ships all of them at advance 0. That one asymmetry is why the hmtx bug
mangled Bold and BoldItalic while leaving Regular and Italic clean — and why an earlier
Regular-only baseline waved the Bold regression through.

Marks that only IBM Plex Sans JP supplies (U+030F in the Regular weight, say) are drawn
there as spacing glyphs and come out full-width. They have been that way since v1.0.0,
they carry no GPOS mark lookup, and they are reported rather than failed: correcting
them is a decision about the desktop font's design, not something to slip in through a
build fix.

Usage:  python3 test_advance_widths.py [font.ttf ...]
"""
import glob
import os
import re
import sys
import unicodedata

from fontTools.ttLib import TTFont

BUILD_SCRIPT = "fontforge_script.py"
PLEX_MONO = "source/IBM-Plex-Mono/IBMPlexMono-{style}.ttf"
PLEX_SANS_JP = "source/IBM-Plex-Sans-JP/unhinted/IBMPlexSansJP-{style}.ttf"
PLEX_SANS_KR = "source/IBM-Plex-Sans-KR/unhinted/IBMPlexSansKR-{style}.ttf"
HACK = "source/hack/Hack-{style}.ttf"

WEIGHTS = ["Thin", "ExtraLight", "Light", "Regular", "Text", "Medium", "SemiBold", "Bold"]
STYLES = WEIGHTS + [w + "Italic" for w in WEIGHTS] + ["Italic"]

SECTION_SIGN = 0x00A7   # East Asian Ambiguous; half-width only in Console builds
DIGIT_ZERO = 0x0030     # the half-width reference


def style_of(path):
    """GLG-Mono35ConsoleNF-SemiBoldItalic.ttf -> SemiBoldItalic

    Every family prefix (Console, 35, NF) is glued to 'GLG-Mono' without a hyphen and no
    style name contains one, so the style is always the final hyphen-separated field.
    """
    stem = os.path.basename(path).rsplit(".", 1)[0]
    style = stem.rsplit("-", 1)[-1]
    return style if style in STYLES else "Regular"


def open_source(template, style, fallback="Regular"):
    path = template.format(style=style)
    if not os.path.exists(path):
        path = template.format(style=fallback)
    return TTFont(path) if os.path.exists(path) else None


def zero_width_names(font):
    """Glyph names this source ships at advance 0 — encoded or not."""
    hmtx = font["hmtx"].metrics
    return {name for name, (advance, _) in hmtx.items() if advance == 0}


def is_console(font):
    """Console builds fold East Asian Ambiguous characters down to half-width."""
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    if SECTION_SIGN not in cmap or DIGIT_ZERO not in cmap:
        return True
    return hmtx[cmap[SECTION_SIGN]][0] <= hmtx[cmap[DIGIT_ZERO]][0] * 1.5


SELECT_CALL = re.compile(
    r'select\(\(\s*"(?P<mode>more|less)"\s*,\s*"unicode"'
    r'(?P<ranged>\s*,\s*"ranges")?\s*\)\s*,\s*'
    r'(?P<first>0x[0-9A-Fa-f]+)(?:\s*,\s*(?P<last>0x[0-9A-Fa-f]+))?\s*\)'
)


def dropped_in_non_console():
    """Codepoints `delete_not_console_glyphs()` strips from the Latin face.

    Read out of the build script rather than copied, so the two cannot drift. In
    non-Console builds those glyphs are handed to IBM Plex Sans JP, which draws several
    of them — U+00AD, say — as spacing glyphs, so Plex Mono's zero advance is no longer
    the contract for them.

    FontForge's selection is a running set, so the calls have to be replayed in order:
    `more` adds, `less` takes back. The build keeps six characters that way (U+00B7,
    U+2022, U+2024, U+2219, U+25D8, U+25E6 — the editors' whitespace-visualisation
    glyphs), and reading only the `more` calls would wrongly claim they are dropped.
    """
    source = open(BUILD_SCRIPT, encoding="utf-8").read()
    body = re.search(r"def delete_not_console_glyphs\(.*?\n(?=def |\Z)", source, re.S)
    if not body:
        raise SystemExit(f"delete_not_console_glyphs() not found in {BUILD_SCRIPT}")

    dropped = set()
    for call in SELECT_CALL.finditer(body.group()):
        first = int(call["first"], 16)
        last = int(call["last"], 16) if call["ranged"] and call["last"] else first
        codepoints = range(first, last + 1)
        if call["mode"] == "more":
            dropped.update(codepoints)
        else:
            dropped.difference_update(codepoints)
    return dropped


def latin_zero_contract(style, console):
    """Glyph names that must keep advance 0, given the pipeline's Latin precedence."""
    jp_style = style.replace("Italic", "") or "Regular"

    plex = open_source(PLEX_MONO, style)
    hack = open_source(HACK, "Bold" if "Bold" in style else "Regular")
    if plex is None or hack is None:
        raise SystemExit("source fonts missing; run from the repository root")

    plex_cmap = plex.getBestCmap()
    contract = zero_width_names(plex)
    if not console:
        surrendered = dropped_in_non_console()
        contract -= {name for cp, name in plex_cmap.items() if cp in surrendered}

    blocked = set(plex_cmap)                 # merge_hack() clears Hack glyphs Plex has
    if not console:
        # non-Console: JP also outranks Hack, so Hack only fills what JP lacks too.
        for template in (PLEX_SANS_JP, PLEX_SANS_KR):
            source = open_source(template, jp_style)
            if source is not None:
                blocked |= set(source.getBestCmap())
                source.close()

    hack_cmap = hack.getBestCmap()
    surviving = {name for cp, name in hack_cmap.items() if cp not in blocked}
    surviving |= set(hack.getGlyphOrder()) - set(hack_cmap.values())   # unencoded
    contract |= zero_width_names(hack) & surviving

    plex.close()
    hack.close()
    return contract


def check_font(path):
    font = TTFont(path)
    style = style_of(path)
    console = is_console(font)
    contract = latin_zero_contract(style, console)

    hmtx = font["hmtx"].metrics
    regressions = sorted(
        (name, hmtx[name][0]) for name in contract & set(hmtx) if hmtx[name][0] != 0
    )

    reverse_cmap = {glyph: cp for cp, glyph in font.getBestCmap().items()}
    inherited = [
        name for name, cp in reverse_cmap.items()
        if name not in contract
        and hmtx[name][0] != 0
        and unicodedata.category(chr(cp)) in {"Mn", "Cf"}
    ]

    name = os.path.basename(path)
    mode = "Console" if console else "non-Console"
    if regressions:
        print(f"FAIL  {name} [{mode}/{style}]: "
              f"{len(regressions)} zero-width Latin glyphs carry an advance")
        for glyph, advance in regressions[:10]:
            cp = reverse_cmap.get(glyph)
            where = f"U+{cp:04X}" if cp else "unencoded"
            print(f"        {glyph:16s} advance={advance:<5d} {where}")
        if len(regressions) > 10:
            print(f"        ... and {len(regressions) - 10} more")
    else:
        checked = len(contract & set(hmtx))
        print(f"OK    {name} [{mode}/{style}]: {checked} zero-width Latin glyphs "
              f"kept advance 0 (numberOfHMetrics={font['hhea'].numberOfHMetrics})")

    if inherited:
        print(f"      note: {len(inherited)} IBM Plex Sans JP marks are spacing — "
              f"inherited from v1.0.0, not a regression")

    font.close()
    return len(regressions)


def main():
    paths = sys.argv[1:] or sorted(glob.glob("build/**/GLG-Mono*.ttf", recursive=True))
    if not paths:
        print("no fonts found; build first (task quick) or pass paths explicitly")
        return 1
    return 1 if sum(check_font(p) for p in paths) else 0


if __name__ == "__main__":
    sys.exit(main())
