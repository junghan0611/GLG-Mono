#!/usr/bin/env python3
"""Prove the eight web files still are the font, not merely something that renders.

Subsetting fails quietly. It drops the licence name records by default, it drops `BASE`
because fontTools does not recognise it, and a tier boundary drawn through a ligature or
a mark/base pair breaks shaping in a way no size check would ever show. Every gate here
exists because the failure it guards is invisible otherwise.

An earlier version of this file checked the *source* for tier violations and never looked
at what was shipped: deleting GSUB outright from a delivered WOFF2 passed all eight gates.
So the rules are now read back out of the delivered files and compared against the
source's projection onto that tier, and — the part no model can fake — every ligature and
every mark/base pair the font actually declares is shaped through HarfBuzz twice, once
with the source and once with the tier, and the two must agree glyph for glyph.

Gates: coverage, geometry, hinting, metrics, global tables, layout, shaping, stylesheet,
licensing, determinism. The durable rationale and delivery contract live in AGENTS.md.

Usage:  python3 webfont_verify.py [--web build/web]
"""
import argparse
import hashlib
import io
import itertools
import json
import os
import re
import shutil
import subprocess
import sys

import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

from webfont_subset import (EXCLUDED_PUA, FACES, SOURCE, core_range, jp_range,
                            partition, shaping_clusters)

HEAD_FLAGS_WOFF2_BIT = 1 << 11      # the WOFF2 encoder is required to set it

EXACT_FIELDS = [
    ("head", "unitsPerEm"), ("head", "macStyle"),
    ("hhea", "ascent"), ("hhea", "descent"), ("hhea", "lineGap"),
    ("OS/2", "sTypoAscender"), ("OS/2", "sTypoDescender"), ("OS/2", "sTypoLineGap"),
    ("OS/2", "usWinAscent"), ("OS/2", "usWinDescent"),
    ("OS/2", "xAvgCharWidth"), ("OS/2", "usWeightClass"), ("OS/2", "fsSelection"),
    ("post", "isFixedPitch"), ("post", "italicAngle"),
    ("post", "underlinePosition"), ("post", "underlineThickness"),
]

BINARY_TABLES = ["cvt ", "fpgm", "prep", "gasp", "BASE"]
LEGAL_NAME_IDS = [0, 13, 14]

# The notices must name every party whose work is in the binary. An empty file passed the
# old gate; these markers are what make that impossible.
NOTICE_MARKERS = ["IBM Plex", "Hack", "Bitstream Vera", "PlemolJP",
                  "SIL Open Font License", "MIT License"]

# Text that must shape identically through a tier and through the whole font.
FIXED_CANARIES = {
    "core": ["힣", "한글 코딩", "가나다라마바사", "ㄱㄴㄷㅏㅑ", "AVWA Typography",
             "é à ö", "i̇́", "→ ± © § ¶", "0O1lI",
             "ｆｕｌｌｗｉｄｔｈ", "== != >= <= -> =>"],
    "jp": ["日本語", "漢字とかな", "ひらがな", "カタカナ", "が ぱ", "ｱｲｳｴｵ"],
}

failures = []


def fail(gate, detail):
    failures.append(f"[{gate}] {detail}")
    print(f"  FAIL  {gate}: {detail}")


def ok(gate, detail):
    print(f"  ok    {gate}: {detail}")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# --------------------------------------------------------------------------- layout


CONTEXT_COVERAGES = ("BacktrackCoverage", "InputCoverage", "LookAheadCoverage")
MAX_CHAIN_DEPTH = 4


def chain_context(sub, keep):
    """The three coverage groups of a chained rule, or None if it cannot fire here.

    A coverage emptied by the tier boundary means the rule can never match in this file,
    so it is not something the tier lost.
    """
    groups = tuple(
        tuple(tuple(sorted(g for g in coverage.glyphs if keep(g)))
              for coverage in getattr(sub, attr, []) or [])
        for attr in CONTEXT_COVERAGES
    )
    if any(not coverage for group in groups for coverage in group):
        return None
    return groups


def lookup_rules(tag, lookups, lookup, keep, depth=0):
    """Every rule one lookup declares, spelled out in glyph names."""
    rules = set()
    for sub in lookup.SubTable:
        kind = (tag, lookup.LookupType)
        if kind == ("GSUB", 1):
            for src, dst in sub.mapping.items():
                if keep(src) and keep(dst):
                    rules.add(("gsub1", src, dst))
        elif kind == ("GSUB", 2):
            for src, dst in sub.mapping.items():
                if keep(src) and all(map(keep, dst)):
                    rules.add(("gsub2", src, tuple(dst)))
        elif kind == ("GSUB", 3):
            for src, alts in sub.alternates.items():
                surviving = tuple(a for a in alts if keep(a))
                if keep(src) and surviving:
                    rules.add(("gsub3", src, surviving))
        elif kind == ("GSUB", 4):
            for first, entries in sub.ligatures.items():
                for entry in entries:
                    glyphs = [first] + list(entry.Component) + [entry.LigGlyph]
                    if all(map(keep, glyphs)):
                        rules.add(("gsub4", first, tuple(entry.Component), entry.LigGlyph))
        elif kind == ("GSUB", 6):
            if getattr(sub, "Format", None) != 3:
                fail("layout", f"GSUB 6 subtable is format {getattr(sub, 'Format', '?')}, "
                               f"which this projection does not model — fail closed")
                continue
            context = chain_context(sub, keep)
            if context is None:
                continue
            if depth >= MAX_CHAIN_DEPTH:
                fail("layout", f"GSUB chains nest deeper than {MAX_CHAIN_DEPTH} lookups")
                continue
            # The record is the whole point of a chained lookup: it says which lookup runs
            # at which position. Its LookupListIndex is renumbered by subsetting, so what
            # is compared is the *rules of the lookup it names*, projected the same way.
            # Record order is semantic and is preserved.
            records = tuple(
                (record.SequenceIndex,
                 frozenset(lookup_rules(tag, lookups, lookups[record.LookupListIndex],
                                        keep, depth + 1)))
                for record in (getattr(sub, "SubstLookupRecord", None) or [])
            )
            rules.add(("gsub6", context, records))
        elif kind == ("GPOS", 4):
            marks = [g for g in sub.MarkCoverage.glyphs if keep(g)]
            bases = [g for g in sub.BaseCoverage.glyphs if keep(g)]
            if marks and bases:
                rules.add(("gpos4", tuple(sorted(marks)), tuple(sorted(bases))))
        elif kind in (("GPOS", 1), ("GPOS", 2)):
            continue
        else:
            fail("layout", f"unknown lookup {tag} type {lookup.LookupType}")
    return rules


def layout_rules(font, retained=None):
    """Every substitution and mark-attachment the font declares, as comparable rules.

    Keyed by glyph name, never by glyph or lookup index — subsetting renumbers both, and
    a rule set keyed on indices would report differences that are not differences.
    """
    rules = set()
    keep = (lambda g: True) if retained is None else (lambda g: g in retained)

    for tag in ("GSUB", "GPOS"):
        if tag not in font or font[tag].table.LookupList is None:
            continue
        lookups = font[tag].table.LookupList.Lookup
        for lookup in lookups:
            rules |= lookup_rules(tag, lookups, lookup, keep)
    return rules


def gate_layout(face, source, tiers):
    for tier, font in tiers.items():
        retained = set(font.getGlyphOrder())
        expected = layout_rules(source, retained)
        actual = layout_rules(font)

        lost = expected - actual
        if lost:
            sample = sorted(str(r)[:60] for r in lost)[:3]
            fail("layout", f"{face}/{tier}: {len(lost)} of {len(expected)} rules missing "
                           f"from the shipped file, e.g. {sample}")
        elif not expected:
            fail("layout", f"{face}/{tier}: source declares no rules for these glyphs — "
                           f"the projection is wrong")
        else:
            ok("layout", f"{face}/{tier}: all {len(expected)} substitution and "
                         f"mark-attachment rules survive")


# --------------------------------------------------------------------------- shaping


class Shaper:
    """HarfBuzz over a face, whatever container it arrived in.

    HarfBuzz does not read WOFF2 — hand it the compressed bytes and every lookup silently
    misses, every glyph comes back as .notdef, and a comparison against the source
    "fails" for reasons that have nothing to do with the font. Decompress first.
    """

    def __init__(self, path):
        font = TTFont(path)
        self.names = font.getGlyphOrder()
        font.flavor = None
        sfnt = io.BytesIO()
        font.save(sfnt)
        font.close()

        self.face = hb.Face(sfnt.getvalue())
        self.font = hb.Font(self.face)
        if self.face.glyph_count == 0:
            raise SystemExit(f"HarfBuzz cannot read {path}")

    def shape(self, text, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, features or {})
        return [
            (self.names[info.codepoint], position.x_advance, position.x_offset,
             position.y_offset)
            for info, position in zip(buf.glyph_infos, buf.glyph_positions)
        ]


CHAIN_CONTEXT_SAMPLES = 4    # per backtrack/lookahead position
CHAIN_INPUT_SAMPLES = 8      # per input position — the input is what gets substituted


def chain_canaries(sub, features, reverse, tier_codepoints):
    """Strings that make a chained rule actually fire.

    A coverage-only comparison cannot see a deleted SubstLookupRecord: the contexts still
    match, they simply substitute nothing. The only way to notice is to type text the
    chain is supposed to rewrite and watch what comes out, so each context position
    contributes its glyphs and the product becomes the canaries. Backtrack coverages are
    stored nearest-first, so they are reversed back into reading order.
    """
    positions = []
    for attr, limit in (("BacktrackCoverage", CHAIN_CONTEXT_SAMPLES),
                        ("InputCoverage", CHAIN_INPUT_SAMPLES),
                        ("LookAheadCoverage", CHAIN_CONTEXT_SAMPLES)):
        group = []
        for coverage in getattr(sub, attr, None) or []:
            usable = sorted(reverse[g] for g in coverage.glyphs
                            if g in reverse and reverse[g] in tier_codepoints)
            if not usable:
                return []            # this context cannot be typed from this tier
            group.append(usable[:limit])
        if attr == "BacktrackCoverage":
            group.reverse()
        positions += group

    return [("".join(map(chr, combination)), features)
            for combination in itertools.product(*positions)]


def derived_canaries(source, tier_codepoints):
    """Turn the font's own rules into test strings.

    Every ligature it declares, every mark/base pair it can position and every chained
    context it can rewrite becomes a string, so the canaries cover what this font actually
    does rather than what a font usually does. Only rules whose codepoints all land in the
    tier are tested — the rest cannot be triggered from that file by construction.
    """
    reverse = {}
    for codepoint, name in source.getBestCmap().items():
        reverse.setdefault(name, codepoint)

    feature_of = {}
    for record in source["GSUB"].table.FeatureList.FeatureRecord:
        for index in record.Feature.LookupListIndex:
            feature_of.setdefault(index, set()).add(record.FeatureTag)

    cases = []
    for index, lookup in enumerate(source["GSUB"].table.LookupList.Lookup):
        features = {tag: True for tag in feature_of.get(index, ())}
        if lookup.LookupType == 4:
            for sub in lookup.SubTable:
                for first, entries in sub.ligatures.items():
                    for entry in entries:
                        glyphs = [first] + list(entry.Component)
                        if not all(g in reverse for g in glyphs):
                            continue
                        codepoints = [reverse[g] for g in glyphs]
                        if all(c in tier_codepoints for c in codepoints):
                            cases.append(("".join(map(chr, codepoints)), features))
        elif lookup.LookupType == 6:
            for sub in lookup.SubTable:
                if not (getattr(sub, "SubstLookupRecord", None) or []):
                    continue     # a chain that substitutes nothing has nothing to break
                cases += chain_canaries(sub, features, reverse, tier_codepoints)

    for lookup in source["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for sub in lookup.SubTable:
            marks = [reverse[g] for g in sub.MarkCoverage.glyphs if g in reverse]
            bases = [reverse[g] for g in sub.BaseCoverage.glyphs if g in reverse]
            for base in bases:
                for mark in marks:
                    if base in tier_codepoints and mark in tier_codepoints:
                        cases.append((chr(base) + chr(mark), {}))
    return cases


def gate_shaping(face, source_path, source, tiers, tier_paths):
    reference = Shaper(source_path)

    for tier, font in tiers.items():
        codepoints = set(font.getBestCmap())
        shaper = Shaper(tier_paths[tier])

        cases = [(text, {}) for text in FIXED_CANARIES[tier]
                 if all(ord(c) in codepoints or ord(c) < 0x20 for c in text)]
        cases += derived_canaries(source, codepoints)

        broken = []
        for text, features in cases:
            if reference.shape(text, features) != shaper.shape(text, features):
                broken.append(text)

        if broken:
            fail("shaping", f"{face}/{tier}: {len(broken)} of {len(cases)} strings shape "
                            f"differently than the full font, e.g. {broken[:3]!r}")
        elif not cases:
            fail("shaping", f"{face}/{tier}: no canaries ran")
        else:
            ok("shaping", f"{face}/{tier}: {len(cases)} strings shape identically "
                          f"through HarfBuzz (fixed + derived from the font's own rules)")

    # The partition itself: no cluster may straddle the boundary.
    reverse = {}
    for codepoint, name in source.getBestCmap().items():
        reverse.setdefault(name, codepoint)
    core = set(tiers["core"].getBestCmap())
    jp = set(tiers["jp"].getBestCmap())
    straddling = sum(
        1 for group in shaping_clusters(source, reverse).groups()
        if (group & core) and (group & jp)
    )
    if straddling:
        fail("shaping", f"{face}: {straddling} clusters straddle the tier boundary")
    else:
        ok("shaping", f"{face}: no ligature or mark/base cluster crosses the boundary")


# --------------------------------------------------------------------------- the rest


def outlines(font):
    glyph_set = font.getGlyphSet()
    result = {}
    for name in font.getGlyphOrder():
        pen = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(pen)
        result[name] = pen.value
    return result


def gate_coverage(face, source, tiers):
    web = set(source.getBestCmap()) - EXCLUDED_PUA
    core = set(tiers["core"].getBestCmap())
    jp = set(tiers["jp"].getBestCmap())

    if core | jp != web:
        fail("coverage", f"{face}: {len(web - (core | jp))} lost, "
                         f"{len((core | jp) - web)} unexpected")
    elif core & jp:
        fail("coverage", f"{face}: {len(core & jp)} codepoints in both tiers")
    else:
        ok("coverage", f"{face}: {len(core)} + {len(jp)} = {len(web)} codepoints, disjoint")


def gate_geometry_and_hinting(face, source, tiers):
    source_outlines = outlines(source)
    source_hmtx = source["hmtx"].metrics
    source_glyf = source["glyf"]

    for tier, font in tiers.items():
        tier_outlines = outlines(font)
        tier_hmtx = font["hmtx"].metrics
        shape, metric, program = [], [], []

        for name in font.getGlyphOrder():
            if name not in source_outlines:
                continue
            if tier_outlines[name] != source_outlines[name]:
                shape.append(name)
            if tier_hmtx[name] != source_hmtx[name]:
                metric.append(name)
            want = getattr(source_glyf[name], "program", None)
            got = getattr(font["glyf"][name], "program", None)
            if (want.bytecode if want else b"") != (got.bytecode if got else b""):
                program.append(name)

        if shape:
            fail("geometry", f"{face}/{tier}: {len(shape)} outlines changed, e.g. {shape[:5]}")
        elif metric:
            fail("geometry", f"{face}/{tier}: {len(metric)} advance/LSB changed, e.g. {metric[:5]}")
        else:
            ok("geometry", f"{face}/{tier}: {len(font.getGlyphOrder())} glyphs keep "
                           f"outline, advance and LSB")

        if program:
            fail("hinting", f"{face}/{tier}: {len(program)} glyph programs changed")
        else:
            ok("hinting", f"{face}/{tier}: glyph bytecode preserved")


def gate_metrics(face, source, tiers):
    for tier, font in tiers.items():
        wrong = [f"{table}.{field}" for table, field in EXACT_FIELDS
                 if getattr(source[table], field) != getattr(font[table], field)]
        if (source["head"].flags & ~HEAD_FLAGS_WOFF2_BIT) != \
           (font["head"].flags & ~HEAD_FLAGS_WOFF2_BIT):
            wrong.append("head.flags")
        if wrong:
            fail("metrics", f"{face}/{tier}: {', '.join(wrong)}")
        else:
            ok("metrics", f"{face}/{tier}: {len(EXACT_FIELDS) + 1} vertical/width fields exact")


def gate_binary_tables(face, source, tiers):
    for tier, font in tiers.items():
        wrong = []
        for tag in BINARY_TABLES:
            if tag not in source:
                continue
            if tag not in font:
                wrong.append(f"{tag} dropped")
            elif source.getTableData(tag) != font.getTableData(tag):
                wrong.append(f"{tag} altered")
        if wrong:
            fail("tables", f"{face}/{tier}: {', '.join(wrong)}")
        else:
            ok("tables", f"{face}/{tier}: {', '.join(BINARY_TABLES)} byte-identical")


def gate_licensing(face, source, tiers, web_dir):
    for tier, font in tiers.items():
        wrong = [f"nameID {i}" for i in LEGAL_NAME_IDS
                 if source["name"].getDebugName(i) != font["name"].getDebugName(i)]
        if wrong:
            fail("licensing", f"{face}/{tier}: {', '.join(wrong)} lost or altered")
        else:
            ok("licensing", f"{face}/{tier}: nameID {LEGAL_NAME_IDS} preserved")


def gate_notices(web_dir):
    for required in ("OFL.txt", "HACK-LICENSE.txt", "THIRD_PARTY_NOTICES.txt"):
        path = os.path.join(web_dir, required)
        if not os.path.exists(path):
            fail("licensing", f"{required} missing from the distribution")
            return

    notices = open(os.path.join(web_dir, "THIRD_PARTY_NOTICES.txt"), encoding="utf-8").read()
    absent = [marker for marker in NOTICE_MARKERS if marker.lower() not in notices.lower()]
    if absent:
        fail("licensing", f"THIRD_PARTY_NOTICES.txt never mentions {absent}")
    else:
        ok("licensing", f"notices name all {len(NOTICE_MARKERS)} parties and ship both licences")


def gate_stylesheet(web_dir, manifest):
    """The stylesheet is the only part of this a browser actually reads."""
    before = len(failures)
    css = open(os.path.join(web_dir, "glg-mono.css"), encoding="utf-8").read()

    blocks = re.findall(
        r"@font-face\s*\{(.*?)\}", css, re.S
    )
    if len(blocks) != 8:
        fail("stylesheet", f"{len(blocks)} @font-face rules, expected 8")
        return
    if "font-synthesis" in css:
        fail("stylesheet", "sets a font-synthesis policy; real italics must not be "
                           "second-guessed by the browser")

    def parse_ranges(text):
        found = set()
        for part in text.split(","):
            part = part.strip().removeprefix("U+")
            if "-" in part:
                lo, hi = part.split("-")
                found.update(range(int(lo, 16), int(hi, 16) + 1))
            elif part:
                found.add(int(part, 16))
        return found

    declared = {}
    for block in blocks:
        url = re.search(r'url\("([^"]+)"\)', block)
        weight = re.search(r"font-weight:\s*(\d+)", block)
        style = re.search(r"font-style:\s*(\w+)", block)
        ranges = re.search(r"unicode-range:\s*([^;]+);", block)
        if not (url and weight and style and ranges):
            fail("stylesheet", "an @font-face is missing src, weight, style or unicode-range")
            return
        declared[url.group(1)] = (int(weight.group(1)), style.group(1),
                                  parse_ranges(ranges.group(1)))

    for face, entry in manifest["faces"].items():
        for tier, info in entry["tiers"].items():
            filename = info["file"]
            if filename not in declared:
                fail("stylesheet", f"{filename} is in the manifest but not in the CSS")
                continue
            if not os.path.exists(os.path.join(web_dir, filename)):
                fail("stylesheet", f"the CSS points at {filename}, which is not on disk")
                continue
            weight, style, ranges = declared[filename]
            if (weight, style) != (entry["weight"], entry["style"]):
                fail("stylesheet", f"{filename}: declared {weight}/{style}, "
                                   f"manifest says {entry['weight']}/{entry['style']}")
            font = TTFont(os.path.join(web_dir, filename))
            missing = set(font.getBestCmap()) - ranges
            font.close()
            if missing:
                fail("stylesheet", f"{filename}: {len(missing)} codepoints in the file are "
                                   f"outside its unicode-range and can never be used")

    for face in manifest["faces"]:
        core_file = manifest["faces"][face]["tiers"]["core"]["file"]
        jp_file = manifest["faces"][face]["tiers"]["jp"]["file"]
        if core_file in declared and jp_file in declared:
            overlap = declared[core_file][2] & declared[jp_file][2]
            if overlap:
                fail("stylesheet", f"{face}: core and jp both claim {len(overlap)} codepoints; "
                                   f"the browser's choice would be arbitrary")

    if len(failures) == before:
        ok("stylesheet", "8 @font-face rules, ranges cover every codepoint shipped, "
                         "core and jp disjoint, no font-synthesis")


def distribution(web_dir):
    return {
        name: sha256(os.path.join(web_dir, name))
        for name in sorted(os.listdir(web_dir))
    }


def gate_manifest(web_dir, manifest):
    """The manifest must describe the files that are actually there."""
    wrong = []
    shipped = 0
    for face, entry in manifest["faces"].items():
        for tier, info in entry["tiers"].items():
            path = os.path.join(web_dir, info["file"])
            if not os.path.exists(path):
                wrong.append(f"{info['file']} absent")
                continue
            shipped += os.path.getsize(path)
            if os.path.getsize(path) != info["bytes"]:
                wrong.append(f"{info['file']} size {os.path.getsize(path)} != {info['bytes']}")
            digest = sha256(path)[:8]
            if digest != info["sha256_8"] or not info["file"].endswith(f".{digest}.woff2"):
                wrong.append(f"{info['file']} content hash is {digest}")
    if manifest.get("total_bytes") != shipped:
        wrong.append(f"total_bytes says {manifest.get('total_bytes')}, the eight files "
                     f"weigh {shipped}")
    if sorted(manifest["excluded_pua"]) != sorted(f"U+{c:04X}" for c in EXCLUDED_PUA):
        wrong.append("excluded_pua does not match the declared exclusion")
    if wrong:
        fail("manifest", "; ".join(wrong[:4]))
    else:
        ok("manifest", f"every file matches its recorded size, content hash and the "
                       f"{shipped/1024/1024:.2f} MB total")


def gate_determinism(web_dir):
    """Rebuild and demand the whole distribution back, byte for byte.

    The garden serves these immutable for a year, so a filename must pin one byte sequence
    forever. Comparing only the eight font names would miss a CSS or manifest that drifts.
    """
    scratch = web_dir + ".determinism"
    result = subprocess.run([sys.executable, "webfont_subset.py", "--out", scratch],
                            capture_output=True, text=True)
    if result.returncode != 0:
        fail("determinism", f"the second build failed: {result.stderr.strip()[:200]}")
        return
    try:
        first, second = distribution(web_dir), distribution(scratch)
        if first.keys() != second.keys():
            fail("determinism", f"the two builds emit different files: "
                                f"{set(first) ^ set(second)}")
        else:
            drifted = [name for name in first if first[name] != second[name]]
            if drifted:
                fail("determinism", f"{len(drifted)} files differ on rebuild: {drifted}")
            else:
                ok("determinism", f"a second build reproduces all {len(first)} files byte "
                                  f"for byte")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


PER_FACE_GATES = ["coverage", "geometry", "metrics", "tables", "layout", "shaping",
                  "licensing"]
DISTRIBUTION_GATES = ["notices", "stylesheet", "manifest", "determinism"]
ALL_GATES = PER_FACE_GATES + DISTRIBUTION_GATES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web", default="build/web")
    parser.add_argument("--faces", default=",".join(FACES),
                        help="comma-separated faces to check (default: all four)")
    parser.add_argument("--gates", default=",".join(ALL_GATES),
                        help=f"comma-separated gates to run. One of: {', '.join(ALL_GATES)}. "
                             f"Narrow this when probing a single gate; the full run walks "
                             f"every outline and shapes thousands of strings.")
    args = parser.parse_args()

    faces = [f.strip() for f in args.faces.split(",") if f.strip()]
    gates = {g.strip() for g in args.gates.split(",") if g.strip()}
    unknown = gates - set(ALL_GATES)
    if unknown:
        raise SystemExit(f"unknown gate(s): {sorted(unknown)}")

    manifest = json.load(open(os.path.join(args.web, "manifest.json"), encoding="utf-8"))

    if gates & set(PER_FACE_GATES):
        for face in faces:
            print(f"\n{face}")
            source_path = SOURCE.format(face=face)
            source = TTFont(source_path)
            tier_paths = {tier: os.path.join(args.web, info["file"])
                          for tier, info in manifest["faces"][face]["tiers"].items()}
            tiers = {tier: TTFont(path) for tier, path in tier_paths.items()}

            if "coverage" in gates:
                gate_coverage(face, source, tiers)
            if "geometry" in gates:
                gate_geometry_and_hinting(face, source, tiers)
            if "metrics" in gates:
                gate_metrics(face, source, tiers)
            if "tables" in gates:
                gate_binary_tables(face, source, tiers)
            if "layout" in gates:
                gate_layout(face, source, tiers)
            if "shaping" in gates:
                gate_shaping(face, source_path, source, tiers, tier_paths)
            if "licensing" in gates:
                gate_licensing(face, source, tiers, args.web)

            source.close()
            for font in tiers.values():
                font.close()

    if gates & set(DISTRIBUTION_GATES):
        print("\ndistribution")
        if "notices" in gates:
            gate_notices(args.web)
        if "stylesheet" in gates:
            gate_stylesheet(args.web, manifest)
        if "manifest" in gates:
            gate_manifest(args.web, manifest)
        if "determinism" in gates:
            gate_determinism(args.web)

    print()
    if failures:
        print(f"{len(failures)} FAILURES")
        return 1
    print("all gates green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
