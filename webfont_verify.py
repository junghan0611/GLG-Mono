#!/usr/bin/env python3
"""Prove the eight web files still are the font, not merely something that renders.

Subsetting is silent when it goes wrong. It drops the licence name records by default,
it drops `BASE` because fontTools does not recognise it, and a tier boundary drawn
through a ligature or a mark/base pair breaks shaping in a way no size check would ever
show. Every gate here exists because the failure it guards is invisible otherwise.

The gates and what each one is really for are written up in docs/WEBFONT_SUBSET.md.

Usage:  python3 webfont_verify.py [--web build/web]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

from webfont_subset import (FACES, PUA_RANGES, SOURCE, in_ranges, partition,
                            shaping_clusters)

# Change under subsetting by definition; comparing them would fail a correct build.
DERIVED_FIELDS = {
    ("hhea", "numberOfHMetrics"),
    ("maxp", "numGlyphs"),
    ("maxp", "maxComponentElements"),
    ("maxp", "maxCompositeContours"),
    ("maxp", "maxCompositePoints"),
    ("maxp", "maxContours"),
    ("maxp", "maxPoints"),
    ("maxp", "maxSizeOfInstructions"),
    ("head", "checkSumAdjustment"),
    ("head", "indexToLocFormat"),
}

# head.flags bit 11 says "lossless data produced by an optimizing transform". The WOFF2
# encoder is required to set it, so it differs from the source by design; every other bit
# must survive.
HEAD_FLAGS_WOFF2_BIT = 1 << 11

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

failures = []


def fail(gate, detail):
    failures.append(f"[{gate}] {detail}")
    print(f"  FAIL  {gate}: {detail}")


def ok(gate, detail):
    print(f"  ok    {gate}: {detail}")


def outlines(font):
    glyph_set = font.getGlyphSet()
    drawn = {}
    for name in font.getGlyphOrder():
        pen = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(pen)
        drawn[name] = pen.value
    return drawn


def gate_coverage(face, source, tiers):
    web = {c for c in source.getBestCmap() if not in_ranges(c, PUA_RANGES)}
    core = set(tiers["core"].getBestCmap())
    jp = set(tiers["jp"].getBestCmap())

    if core | jp != web:
        missing = web - (core | jp)
        extra = (core | jp) - web
        fail("coverage", f"{face}: {len(missing)} lost, {len(extra)} unexpected")
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
                continue                              # .notdef and friends may be synthesised
            if tier_outlines[name] != source_outlines[name]:
                shape.append(name)
            if tier_hmtx[name] != source_hmtx[name]:
                metric.append(name)
            source_program = getattr(source_glyf[name], "program", None)
            tier_program = getattr(font["glyf"][name], "program", None)
            source_code = source_program.bytecode if source_program else b""
            tier_code = tier_program.bytecode if tier_program else b""
            if source_code != tier_code:
                program.append(name)

        checked = len(font.getGlyphOrder())
        if shape:
            fail("geometry", f"{face}/{tier}: {len(shape)} outlines changed, e.g. {shape[:5]}")
        elif metric:
            fail("geometry", f"{face}/{tier}: {len(metric)} advance/LSB changed, e.g. {metric[:5]}")
        else:
            ok("geometry", f"{face}/{tier}: {checked} glyphs keep outline, advance and LSB")

        if program:
            fail("hinting", f"{face}/{tier}: {len(program)} glyph programs changed, e.g. {program[:5]}")
        else:
            ok("hinting", f"{face}/{tier}: glyph bytecode preserved")


def gate_metrics(face, source, tiers):
    for tier, font in tiers.items():
        wrong = []
        for table, field in EXACT_FIELDS:
            if getattr(source[table], field) != getattr(font[table], field):
                wrong.append(f"{table}.{field}")

        source_flags = source["head"].flags & ~HEAD_FLAGS_WOFF2_BIT
        tier_flags = font["head"].flags & ~HEAD_FLAGS_WOFF2_BIT
        if source_flags != tier_flags:
            wrong.append(f"head.flags ({source_flags:#b} -> {tier_flags:#b})")

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
        wrong = []
        for name_id in LEGAL_NAME_IDS:
            want = source["name"].getDebugName(name_id)
            got = font["name"].getDebugName(name_id)
            if want != got:
                wrong.append(f"nameID {name_id}")
        if wrong:
            fail("licensing", f"{face}/{tier}: {', '.join(wrong)} lost or altered")
        else:
            ok("licensing", f"{face}/{tier}: nameID {LEGAL_NAME_IDS} preserved")

    for required in ("OFL.txt", "THIRD_PARTY_NOTICES.txt"):
        if not os.path.exists(os.path.join(web_dir, required)):
            fail("licensing", f"{required} missing from the distribution")


def gate_shaping(face, source, tiers):
    reverse = {}
    for codepoint, name in source.getBestCmap().items():
        reverse.setdefault(name, codepoint)

    core = set(tiers["core"].getBestCmap())
    jp = set(tiers["jp"].getBestCmap())

    split = 0
    for group in shaping_clusters(source, reverse).groups():
        group &= core | jp
        if group & core and group & jp:
            split += 1
    if split:
        fail("shaping", f"{face}: {split} shaping clusters straddle the tier boundary")
    else:
        ok("shaping", f"{face}: no ligature or mark/base cluster crosses the boundary")

    # Marks must travel with a base that can position them; GPOS cannot reach across files.
    for tier, font in tiers.items():
        if "GPOS" not in font:
            fail("shaping", f"{face}/{tier}: GPOS dropped")
            continue
        lookups = font["GPOS"].table.LookupList.Lookup if font["GPOS"].table.LookupList else []
        marks = sum(1 for lk in lookups if lk.LookupType == 4)
        if tier == "core" and not marks:
            fail("shaping", f"{face}/core: mark-to-base lookups gone")


def gate_determinism(web_dir, manifest):
    """Rebuild into a scratch directory and demand the same eight content hashes.

    The garden serves WOFF2 with a one-year immutable cache, so a filename must pin one
    byte sequence forever. A build that is not reproducible cannot make that promise.
    """
    scratch = web_dir + ".determinism"
    result = subprocess.run(
        [sys.executable, "webfont_subset.py", "--out", scratch],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail("determinism", f"second build failed: {result.stderr.strip()[:200]}")
        return

    try:
        again = json.load(open(os.path.join(scratch, "manifest.json"), encoding="utf-8"))
        drifted = []
        for face, entry in manifest["faces"].items():
            for tier, info in entry["tiers"].items():
                repeat = again["faces"][face]["tiers"][tier]
                if repeat["file"] != info["file"]:
                    drifted.append(f"{face}/{tier}: {info['file']} -> {repeat['file']}")
        if drifted:
            fail("determinism", f"{len(drifted)} files changed on rebuild: {drifted[:3]}")
        else:
            ok("determinism", "a second build reproduces all 8 content hashes")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web", default="build/web")
    args = parser.parse_args()

    manifest = json.load(open(os.path.join(args.web, "manifest.json"), encoding="utf-8"))

    for face in FACES:
        print(f"\n{face}")
        source = TTFont(SOURCE.format(face=face))
        tiers = {
            tier: TTFont(os.path.join(args.web, info["file"]))
            for tier, info in manifest["faces"][face]["tiers"].items()
        }

        gate_coverage(face, source, tiers)
        gate_geometry_and_hinting(face, source, tiers)
        gate_metrics(face, source, tiers)
        gate_binary_tables(face, source, tiers)
        gate_shaping(face, source, tiers)
        gate_licensing(face, source, tiers, args.web)

        source.close()
        for font in tiers.values():
            font.close()

    print()
    gate_determinism(args.web, manifest)

    print()
    if failures:
        print(f"{len(failures)} FAILURES")
        return 1
    print("all gates green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
