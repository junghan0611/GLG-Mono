#!/usr/bin/env python3
"""Repair the advance widths FontForge drops when it writes a TTF.

hmtx stores advance widths only for the first `numberOfHMetrics` glyphs; every glyph
after that inherits the last stored value. FontForge 20251009 judges a face monospaced
whenever the trailing advances agree and compresses that count as far as 4, so every
glyph past index 4 silently inherits a half-width advance. Zero-width glyphs —
combining accents, soft hyphen, ZWSP, unencoded mark components — are destroyed. There
is no generate() flag to turn this off, and outlines, glyph names and cmap all survive
intact, so nothing but an advance-width check notices.

FontForge's in-memory model is the source of truth. Snapshot it before `generate()` and
write it back afterwards. fontTools recomputes `numberOfHMetrics` from the real
advances when it saves, so the repaired file also stops lying about how many metrics it
carries.

Every FontForge → TTF round-trip in this repo must go through here:

  fontforge_script.py    final eng/jp generate, merge_hack()'s Hack temp font,
                         the alt_uni reopen
  fix_nf_korean_bearing.py   the Nerd Fonts bearing pass
"""
import sys

from fontTools.ttLib import TTFont


def snapshot_widths(font):
    """Advance width per glyph name, straight from FontForge's in-memory model."""
    return {glyph.glyphname: glyph.width for glyph in font.glyphs()}


def restore_advance_widths(font_path, widths, quiet=False):
    """Write `widths` back into a TTF FontForge just generated. Returns glyphs repaired."""
    font = TTFont(font_path)
    hmtx = font["hmtx"]
    restored = 0
    for glyph_name, width in widths.items():
        if glyph_name not in hmtx.metrics:
            continue
        advance, lsb = hmtx.metrics[glyph_name]
        if advance != width:
            hmtx.metrics[glyph_name] = (int(width), lsb)
            restored += 1
    if restored:
        font.save(font_path)
        if not quiet:
            print(f"restore advance width: {restored} glyphs in {font_path}",
                  file=sys.stderr)
    font.close()
    return restored
