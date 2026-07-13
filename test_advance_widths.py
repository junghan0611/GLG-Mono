#!/usr/bin/env python3
"""Guard the advance width of nonspacing and format characters.

Why this exists: hmtx stores advance widths only for the first `numberOfHMetrics`
glyphs; every later glyph inherits the last stored value. FontForge 20251009 treats
the merged Latin face as monospaced and compresses that count to 4, which silently
gave 54 zero-width glyphs a half-width advance — combining accents, soft hyphen,
ZWSP. No cmap or outline comparison catches it, yet NFD text then renders the accent
in its own cell. `restore_advance_widths()` in fontforge_script.py writes the real
widths back after FontForge generates each face; this test is the guard for that fix.

Two populations, deliberately kept apart:

  REGRESSION  IBM Plex Mono ships these marks at advance 0. The build must preserve
              that. A nonzero advance here means the hmtx fix broke or regressed,
              and the test fails.

  INHERITED   Marks that only IBM Plex Sans JP provides (U+030F, U+0318…). That face
              designs them as spacing glyphs, so width normalisation makes them
              full-width. They have been wrong since v1.0.0, independently of the
              FontForge upgrade, and they carry no GPOS mark lookup to position them.
              Reported, not failed — fixing them is a separate decision about the
              desktop font, not something to smuggle in through a build migration.

Usage:  python3 test_advance_widths.py [font.ttf ...]
"""
import glob
import sys
import unicodedata

from fontTools.ttLib import TTFont

ENG_SOURCE = "source/IBM-Plex-Mono/IBMPlexMono-Regular.ttf"
ZERO_ADVANCE_CATEGORIES = {"Mn", "Cf"}


def eng_zero_advance_codepoints() -> set[int]:
    """Codepoints the Latin source ships at advance 0 — the contract we must keep."""
    font = TTFont(ENG_SOURCE)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    zero = {cp for cp, name in cmap.items() if hmtx[name][0] == 0}
    font.close()
    return zero


def check_font(path: str, must_be_zero: set[int]) -> int:
    font = TTFont(path)
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    regressions, inherited = [], []
    for codepoint, glyph_name in cmap.items():
        if unicodedata.category(chr(codepoint)) not in ZERO_ADVANCE_CATEGORIES:
            continue
        advance = hmtx[glyph_name][0]
        if advance == 0:
            continue
        target = regressions if codepoint in must_be_zero else inherited
        target.append((codepoint, glyph_name, advance))

    name = path.split("/")[-1]
    if regressions:
        print(f"FAIL  {name}: {len(regressions)} Latin-source zero-width glyphs carry advance")
        for codepoint, glyph_name, advance in regressions[:10]:
            print(f"        U+{codepoint:04X} {glyph_name:12s} advance={advance:<5d} "
                  f"{unicodedata.name(chr(codepoint), '?')}")
    else:
        print(f"OK    {name}: every Latin-source zero-width glyph kept advance 0 "
              f"(numberOfHMetrics={font['hhea'].numberOfHMetrics})")

    if inherited:
        print(f"      note: {len(inherited)} IBM Plex Sans JP marks are spacing "
              f"(e.g. U+{inherited[0][0]:04X}) — inherited from v1.0.0, not a regression")

    font.close()
    return len(regressions)


def main() -> int:
    paths = sys.argv[1:] or sorted(glob.glob("build/GLG-Mono*.ttf"))
    if not paths:
        print("no fonts found; build first (task quick) or pass paths explicitly")
        return 1
    must_be_zero = eng_zero_advance_codepoints()
    return 1 if sum(check_font(p, must_be_zero) for p in paths) else 0


if __name__ == "__main__":
    sys.exit(main())
