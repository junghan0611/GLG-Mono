#!/usr/bin/env python3
"""Guard the advance width of glyphs the Latin side ships at zero.

Why this exists: hmtx stores advance widths only for the first `numberOfHMetrics`
glyphs; every later glyph inherits the last stored value. FontForge 20251009 treats a
monospaced face as compressible and writes `numberOfHMetrics=4`, so every glyph past
index 4 inherits a half-width advance. Zero-width glyphs — combining accents, soft
hyphen, ZWSP — are destroyed, and outlines and cmap stay identical, so nothing but an
advance-width check notices.

The build round-trips through TTF in three places (the final `generate()`, the Hack
temp font inside `merge_hack()`, the alt_uni reopen). Each one loses widths, and each
one calls `restore_advance_widths()`. This test is the guard for all three.

Mirroring the pipeline matters. The Latin side is IBM Plex Mono plus whatever Hack
adds on top for codepoints Plex Mono lacks, and `delete_duplicate_glyphs()` then lets
that Latin side win over IBM Plex Sans JP. So the zero-advance contract is:

    Plex Mono <style> zeros
      ∪  Hack <Bold|Regular> zeros, for codepoints Plex Mono does not have

Style matters too, and this is not academic: Hack-Regular has no U+0305/U+030D-U+0361,
while Hack-Bold ships them at advance 0. That single asymmetry is why the hmtx bug hit
Bold and BoldItalic while leaving Regular and Italic intact — and why a Regular-only
baseline missed it.

Marks that only IBM Plex Sans JP supplies (U+030F in the Regular weight, say) are
designed there as spacing glyphs and end up full-width. They have been that way since
v1.0.0, carry no GPOS mark lookup, and are reported rather than failed: fixing them is
a decision about the desktop font, not something to smuggle in through a build fix.

Usage:  python3 test_advance_widths.py [font.ttf ...]
"""
import glob
import os
import re
import sys
import unicodedata

from fontTools.ttLib import TTFont

ENG_SOURCE = "source/IBM-Plex-Mono/IBMPlexMono-{style}.ttf"
HACK_SOURCE = "source/hack/Hack-{style}.ttf"
ZERO_ADVANCE_CATEGORIES = {"Mn", "Cf"}

# Weights Hack does not ship; merge_hack() falls back to Hack-Regular for all of them
# and uses Hack-Bold only when the style name contains "Bold".
PLEX_WEIGHTS = ["ExtraLight", "Light", "SemiBold", "BoldItalic", "Bold", "Italic",
                "Medium", "Regular", "Text", "Thin"]


def style_of(path: str) -> str:
    """GLG-Mono-SemiBoldItalic.ttf -> SemiBoldItalic"""
    stem = os.path.basename(path).rsplit(".", 1)[0]
    match = re.match(r"GLG-Mono\d*(?:Console)?-(.+)$", stem)
    return match.group(1) if match else "Regular"


def zero_advance_codepoints(name: str, style: str) -> tuple[set[int], set[int]]:
    """(codepoints at advance 0, all codepoints) for one source face."""
    path = name.format(style=style)
    if not os.path.exists(path):
        return set(), set()
    font = TTFont(path)
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    zero = {cp for cp, glyph in cmap.items() if hmtx[glyph][0] == 0}
    every = set(cmap)
    font.close()
    return zero, every


def latin_zero_contract(style: str) -> set[int]:
    plex_style = style if os.path.exists(ENG_SOURCE.format(style=style)) else "Regular"
    hack_style = "Bold" if "Bold" in style else "Regular"

    plex_zero, plex_all = zero_advance_codepoints(ENG_SOURCE, plex_style)
    hack_zero, _ = zero_advance_codepoints(HACK_SOURCE, hack_style)

    # merge_hack() only contributes what Plex Mono is missing.
    return plex_zero | (hack_zero - plex_all)


def check_font(path: str) -> int:
    style = style_of(path)
    must_be_zero = latin_zero_contract(style)

    font = TTFont(path)
    cmap, hmtx = font.getBestCmap(), font["hmtx"]

    regressions, inherited = [], []
    for codepoint, glyph_name in cmap.items():
        if unicodedata.category(chr(codepoint)) not in ZERO_ADVANCE_CATEGORIES:
            continue
        advance = hmtx[glyph_name][0]
        if advance == 0:
            continue
        target = regressions if codepoint in must_be_zero else inherited
        target.append((codepoint, glyph_name, advance))

    name = os.path.basename(path)
    if regressions:
        print(f"FAIL  {name}: {len(regressions)} Latin-source zero-width glyphs carry advance")
        for codepoint, glyph_name, advance in sorted(regressions)[:10]:
            print(f"        U+{codepoint:04X} {glyph_name:14s} advance={advance:<5d} "
                  f"{unicodedata.name(chr(codepoint), '?')}")
        if len(regressions) > 10:
            print(f"        ... and {len(regressions) - 10} more")
    else:
        print(f"OK    {name}: {len(must_be_zero)} Latin-source zero-width codepoints "
              f"kept advance 0 (numberOfHMetrics={font['hhea'].numberOfHMetrics})")

    if inherited:
        first = min(cp for cp, _, _ in inherited)
        print(f"      note: {len(inherited)} IBM Plex Sans JP marks are spacing "
              f"(e.g. U+{first:04X}) — inherited from v1.0.0, not a regression")

    font.close()
    return len(regressions)


def main() -> int:
    paths = sys.argv[1:] or sorted(glob.glob("build/GLG-Mono*.ttf"))
    if not paths:
        print("no fonts found; build first (task quick) or pass paths explicitly")
        return 1
    return 1 if sum(check_font(p) for p in paths) else 0


if __name__ == "__main__":
    sys.exit(main())
