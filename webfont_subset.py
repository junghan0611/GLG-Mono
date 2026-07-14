#!/usr/bin/env python3
"""Cut the four web faces into two tiers each: eight WOFF2 files, nothing more.

The garden ships four full faces at ~2.6 MB apiece, so an ordinary Korean page waits on
5.3 MB of font before it can reflow. Almost all of that weight is Han: the desktop font
inherits 13,022 Han mappings from IBM Plex Sans JP, and a Korean page needs none of them.

So each face is cut once — `core` (Latin, Hangul, punctuation, symbols) and `jp` (Han,
Kana, radicals) — and `unicode-range` lets the browser fetch only what the page uses. A
Korean home page then asks for exactly two files: Regular-core and Bold-core.

Deliberately not done here: no corpus, no frequency map, no dozens of chunks. A
discarded 192-file prototype did transfer less, but its operational complexity is the
thing this repository is trying to shed. The durable web contract lives in AGENTS.md.

Usage:  python3 webfont_subset.py [--out build/web]
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

SOURCE = "build/GLG-Mono-{face}.ttf"
FACES = {
    "Regular": {"weight": 400, "style": "normal"},
    "Bold": {"weight": 700, "style": "normal"},
    "Italic": {"weight": 400, "style": "italic"},
    "BoldItalic": {"weight": 700, "style": "italic"},
}
FAMILY = "GLG Mono"

# Seed for the `jp` tier. Everything the source encodes and this does not name is `core`,
# so a codepoint can never be silently lost by being forgotten here.
JP_RANGES = [
    (0x2E80, 0x2FDF),    # CJK and Kangxi radicals — not punctuation, despite sitting near U+3000
    (0x3040, 0x30FF),    # Hiragana, Katakana
    (0x31F0, 0x31FF),    # Katakana phonetic extensions
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0xFF66, 0xFF9F),    # Halfwidth Katakana
    (0x20000, 0x3FFFF),  # SIP: ideographic extensions
]

# The one deliberate exclusion from the web profile: the Powerline separators and the
# private-use glyphs a web page has no way to ask for. Named one by one, not by range: a
# range would silently swallow any PUA codepoint a future build adds, and the contract
# says these fourteen and nothing else.
EXCLUDED_PUA = frozenset({
    0xE0A0, 0xE0A1, 0xE0A2, 0xE0B0, 0xE0B1, 0xE0B2, 0xE0B3,
    0xF6D7, 0xF6D8, 0xF860, 0xF861, 0xF862, 0xF87A, 0xF87F,
})
PUA_RANGES = [(0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD)]

LICENCE_FILES = {"OFL.txt": "LICENSE", "HACK-LICENSE.txt": "source/hack/LICENSE"}


def in_ranges(codepoint, ranges):
    return any(lo <= codepoint <= hi for lo, hi in ranges)


def excluded_pua(font):
    """The fourteen, verified — a new PUA codepoint must be a decision, not a surprise."""
    present = {c for c in font.getBestCmap() if in_ranges(c, PUA_RANGES)}
    if present != EXCLUDED_PUA:
        added = sorted(f"U+{c:04X}" for c in present - EXCLUDED_PUA)
        gone = sorted(f"U+{c:04X}" for c in EXCLUDED_PUA - present)
        raise SystemExit(
            "the font's private-use codepoints no longer match the web profile's "
            f"declared exclusion (added: {added or 'none'}, missing: {gone or 'none'}). "
            "Decide what the web build should do with them and update EXCLUDED_PUA."
        )
    return present


class Clusters:
    """Codepoints that shaping binds together and a tier boundary must not separate."""

    def __init__(self):
        self.parent = {}

    def find(self, item):
        self.parent.setdefault(item, item)
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def bind(self, items):
        items = sorted(set(items))
        for other in items[1:]:
            a, b = self.find(items[0]), self.find(other)
            if a != b:
                self.parent[b] = a

    def groups(self):
        found = {}
        for item in self.parent:
            found.setdefault(self.find(item), set()).add(item)
        return list(found.values())


def shaping_clusters(font, reverse_cmap):
    """Bind every multi-input GSUB rule and every GPOS mark/base pair.

    A ligature's inputs must resolve in one face, and a mark cannot be positioned against
    a base that lives in a different file — GPOS lookups do not reach across faces. Rules
    are read one at a time: two unrelated ligatures in the same lookup constrain nothing.

    Any lookup type this does not understand raises. Silently ignoring an unknown lookup
    is how a font ships with broken shaping that no size check would ever reveal.
    """
    clusters = Clusters()

    def encoded(glyphs):
        return [reverse_cmap[g] for g in glyphs if g in reverse_cmap]

    for lookup in font["GSUB"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 4:                       # ligature
                for first, entries in sub.ligatures.items():
                    for entry in entries:
                        clusters.bind(encoded([first] + list(entry.Component)))
            elif lookup.LookupType in (1, 2, 3):             # single input; outputs follow
                continue
            elif lookup.LookupType == 6 and getattr(sub, "Format", None) == 3:
                context = []
                for attr in ("BacktrackCoverage", "InputCoverage", "LookAheadCoverage"):
                    for coverage in getattr(sub, attr, []) or []:
                        context += encoded(coverage.glyphs)
                clusters.bind(context)
            else:
                raise SystemExit(
                    f"unhandled GSUB lookup type {lookup.LookupType} "
                    f"format {getattr(sub, 'Format', '?')} — fail closed, "
                    f"teach webfont_subset.py what it binds before shipping"
                )

    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 4:                       # mark-to-base
                clusters.bind(encoded(sub.MarkCoverage.glyphs) +
                              encoded(sub.BaseCoverage.glyphs))
            elif lookup.LookupType in (1, 2):                # single / pair positioning
                continue
            else:
                raise SystemExit(
                    f"unhandled GPOS lookup type {lookup.LookupType} — fail closed"
                )

    return clusters


def partition(font):
    """Split this face's cmap into (core, jp, excluded PUA)."""
    cmap = set(font.getBestCmap())
    pua = excluded_pua(font)
    web = cmap - pua

    core = {c for c in web if not in_ranges(c, JP_RANGES)}
    jp = web - core

    reverse = {}
    for codepoint, name in font.getBestCmap().items():
        reverse.setdefault(name, codepoint)

    # A cluster that straddles the seed boundary is pulled whole into `core`. Dragging a
    # few ideographs into core costs bytes; the reverse would strand a Latin codepoint in
    # the jp tier and break a page that never uses Japanese at all.
    moved = set()
    for group in shaping_clusters(font, reverse).groups():
        group &= web
        if group & core and group & jp:
            moved |= group & jp
    core |= moved
    jp -= moved

    assert core | jp == web, "tiers must cover the whole web profile"
    assert not (core & jp), "tiers must be disjoint"
    return core, jp, pua, moved


def spans_of(codepoints):
    spans, run_start, previous = [], None, None
    for codepoint in sorted(codepoints):
        if run_start is None:
            run_start = previous = codepoint
        elif codepoint == previous + 1:
            previous = codepoint
        else:
            spans.append((run_start, previous))
            run_start = previous = codepoint
    if run_start is not None:
        spans.append((run_start, previous))
    return spans


def format_ranges(spans):
    return ", ".join(f"U+{lo:X}" if lo == hi else f"U+{lo:X}-{hi:X}" for lo, hi in spans)


def core_range(core):
    """`core` is declared exactly: 229 spans, about 2 KB. Cheap and precise."""
    return format_ranges(spans_of(core))


def jp_range(core):
    """`jp` is declared as the tier's blocks, not as its exact cmap.

    Stating the jp cmap exactly costs 4,664 spans — 50 KB per face, 200 KB across the
    four, on top of a stylesheet the garden bundles into one render-blocking file. That
    is the size of the problem we came here to solve, moved from the font to the CSS.

    So the blocks are declared whole. The font does not have every ideograph in them, and
    for a missing one the browser will fetch the jp tier and then fall back to a system
    font. That is a wasted request, never a wrong glyph — a page whose only CJK is an
    ideograph this font lacks would have to fall back anyway. Any codepoint that shaping
    pulled into `core` is punched back out, so the two tiers never claim the same
    character.
    """
    claimed = set()
    for lo, hi in JP_RANGES:
        claimed.update(range(lo, hi + 1))
    return format_ranges(spans_of(claimed - core))


def subset_face(source_path, codepoints, out_path):
    font = TTFont(source_path)
    options = subset.Options()
    options.layout_features = ["*"]        # keep every feature; the desktop font's are all wanted
    options.name_IDs = ["*"]               # default keeps 0-6 only and drops the licence records
    options.name_legacy = True
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.hinting = True
    options.glyph_names = True             # verification is by name; post 3.0 is a later step
    options.passthrough_tables = True      # BASE is 'unknown' to fontTools and would be dropped
    options.drop_tables = []
    options.recalc_bounds = False
    options.recalc_timestamp = False       # determinism: keep the source's head.modified

    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)

    font.flavor = "woff2"                  # needs brotli; see flake.nix
    font.save(out_path)
    font.close()
    return os.path.getsize(out_path)


def content_hash(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()[:8]


def write_licences(out_dir):
    """Ship the licences, not a gesture at them.

    Four copyrights ride in nameID 0 and every one of them has terms attached. Hack is MIT
    and carries Bitstream Vera's reserved-font-name notice, which must travel with the
    binary — a subset is still a derived work of all of it.
    """
    for target, source in LICENCE_FILES.items():
        shutil.copyfile(source, os.path.join(out_dir, target))

    font = TTFont(SOURCE.format(face="Regular"))
    notice = font["name"].getDebugName(0)
    licence = font["name"].getDebugName(13)
    url = font["name"].getDebugName(14)
    font.close()

    hack_licence = open("source/hack/LICENSE", encoding="utf-8").read().strip()

    with open(os.path.join(out_dir, "THIRD_PARTY_NOTICES.txt"), "w", encoding="utf-8") as out:
        out.write("GLG-Mono web fonts — third party notices\n")
        out.write("=" * 39 + "\n\n")
        out.write("These WOFF2 files are subsets of GLG-Mono. Subsetting removes glyphs; it\n")
        out.write("removes no obligations. Every notice below applies to them in full.\n\n")
        out.write("Copyright notices carried in the font (nameID 0)\n")
        out.write("-" * 47 + "\n\n")
        out.write(notice + "\n\n")
        out.write("IBM Plex and PlemolJP — SIL Open Font License 1.1\n")
        out.write("-" * 49 + "\n\n")
        out.write(licence + "\n\n")
        out.write(f"Full text: OFL.txt in this directory, and {url}\n\n")
        out.write("Hack, DejaVu and Bitstream Vera\n")
        out.write("-" * 31 + "\n\n")
        out.write(hack_licence + "\n\n")
        out.write("Full text: HACK-LICENSE.txt in this directory.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build/web")
    args = parser.parse_args()

    for face in FACES:
        if not os.path.exists(SOURCE.format(face=face)):
            raise SystemExit(
                f"{SOURCE.format(face=face)} is missing — build the Console faces first"
            )

    staging = args.out + ".staging"
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)

    manifest = {
        "family": FAMILY,
        "generated_from": SOURCE,
        "tiers": ["core", "jp"],
        # No build timestamp: the manifest is part of the distribution and the
        # distribution must hash the same on every run.
        "excluded_pua": sorted(f"U+{c:04X}" for c in EXCLUDED_PUA),
        "faces": {},
    }
    css = [
        "/* GLG Mono — generated by webfont_subset.py. Do not edit.",
        " * Two tiers per face: `core` carries Latin and all Hangul, `jp` carries Han and",
        " * Kana. unicode-range means a Korean page fetches only the core files.",
        " */",
        "",
    ]
    total = 0

    for face, attrs in FACES.items():
        source_path = SOURCE.format(face=face)
        font = TTFont(source_path)
        core, jp, pua, moved = partition(font)
        font.close()

        manifest["faces"][face] = {"weight": attrs["weight"], "style": attrs["style"],
                                   "tiers": {}}

        for tier, codepoints in (("core", core), ("jp", jp)):
            temporary = os.path.join(staging, f"{face}-{tier}.woff2")
            size = subset_face(source_path, codepoints, temporary)
            digest = content_hash(temporary)
            filename = f"GLG-Mono-{face}-{tier}.{digest}.woff2"
            os.rename(temporary, os.path.join(staging, filename))
            total += size

            manifest["faces"][face]["tiers"][tier] = {
                "file": filename, "bytes": size, "codepoints": len(codepoints),
                "sha256_8": digest,
            }
            declared = core_range(core) if tier == "core" else jp_range(core)
            css += [
                "@font-face {",
                f'  font-family: "{FAMILY}";',
                f'  src: url("{filename}") format("woff2");',
                f"  font-weight: {attrs['weight']};",
                f"  font-style: {attrs['style']};",
                "  font-display: swap;",
                f"  unicode-range: {declared};",
                "}",
                "",
            ]
            print(f"  {face:11s} {tier:4s}  {size/1024:8.1f} KB  "
                  f"{len(codepoints):6d} codepoints"
                  f"{f'  (+{len(moved)} pulled from jp)' if tier == 'core' and moved else ''}")

    manifest["total_bytes"] = total
    with open(os.path.join(staging, "manifest.json"), "w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2, ensure_ascii=False)
        out.write("\n")
    with open(os.path.join(staging, "glg-mono.css"), "w", encoding="utf-8") as out:
        out.write("\n".join(css))

    write_licences(staging)

    shutil.rmtree(args.out, ignore_errors=True)
    os.rename(staging, args.out)

    home = sum(manifest["faces"][f]["tiers"]["core"]["bytes"] for f in ("Regular", "Bold"))
    print(f"\n  distribution: {total/1024/1024:.2f} MB across 8 files -> {args.out}/")
    print(f"  a Korean home page fetches Regular-core + Bold-core = {home/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
