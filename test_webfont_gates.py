#!/usr/bin/env python3
"""A gate that cannot fail is not a gate. Plant each defect in the shipped files; demand a FAIL.

`webfont_verify.py` is the only thing standing between a silent subsetting failure and a
garden page that renders the wrong glyph. It has already been wrong once: an earlier
version read the *source* and let a delivered face with GSUB deleted pass every gate. So
the gates are not trusted because they are written; they are trusted because each of them
has been shown to bite a real defect planted in a real distribution.

Each mutation copies `build/web`, breaks one thing, and runs only the gates that defect
attacks, on one face. Re-verifying four faces per mutation was ten minutes of proving
nothing; the full sweep is a separate, single run (`task web:verify`).

Usage:  python3 test_webfont_gates.py [--web build/web]
        task web:test-gates
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

from fontTools.ttLib import TTFont

FACE = "Regular"


def manifest(web):
    with open(os.path.join(web, "manifest.json"), encoding="utf-8") as handle:
        return json.load(handle)


def core_file(web):
    return os.path.join(web, manifest(web)["faces"][FACE]["tiers"]["core"]["file"])


def resave(font, path):
    font.flavor = "woff2"
    font.save(path)
    font.close()


def chain_subtables(font):
    """Every chained-contextual subtable that actually substitutes something."""
    for lookup in font["GSUB"].table.LookupList.Lookup:
        if lookup.LookupType != 6:
            continue
        for sub in lookup.SubTable:
            if getattr(sub, "SubstLookupRecord", None):
                yield sub


# --------------------------------------------------------------- the planted defects


def drop_gsub(web):
    path = core_file(web)
    font = TTFont(path)
    del font["GSUB"]
    resave(font, path)


def drop_gpos(web):
    path = core_file(web)
    font = TTFont(path)
    del font["GPOS"]
    resave(font, path)


def break_one_ligature(web):
    path = core_file(web)
    font = TTFont(path)
    for lookup in font["GSUB"].table.LookupList.Lookup:
        if lookup.LookupType == 4:
            for sub in lookup.SubTable:
                if sub.ligatures:
                    sub.ligatures.pop(next(iter(sub.ligatures)))
                    resave(font, path)
                    return
    raise SystemExit("no ligature to break")


def strip_one_chain_record(web):
    """The defect coverage alone cannot see.

    A chained context whose SubstLookupRecord is gone still matches the same text — it
    simply substitutes nothing. Its coverage tables are untouched, so a rule set keyed on
    coverage compares equal and the loss is invisible. Half of this font's chains are also
    unreachable through HarfBuzz (it composes d + caron into the precomposed glyph before
    layout ever runs), so shaping cannot see them either. Only a layout gate that models
    what the record *invokes* catches this.
    """
    path = core_file(web)
    font = TTFont(path)
    sub = next(chain_subtables(font))
    sub.SubstLookupRecord = []
    sub.SubstCount = 0
    resave(font, path)


def retarget_one_chain_record(web):
    """The same context, quietly wired to a different lookup."""
    path = core_file(web)
    font = TTFont(path)
    lookups = font["GSUB"].table.LookupList.Lookup
    sub = next(chain_subtables(font))
    record = sub.SubstLookupRecord[0]
    elsewhere = next(i for i, lookup in enumerate(lookups)
                     if lookup.LookupType == 1 and i != record.LookupListIndex
                     and any(s.mapping for s in lookup.SubTable))
    record.LookupListIndex = elsewhere
    resave(font, path)


def drop_base(web):
    path = core_file(web)
    font = TTFont(path)
    del font["BASE"]
    resave(font, path)


def strip_licence_names(web):
    path = core_file(web)
    font = TTFont(path)
    font["name"].removeNames(nameID=13)
    resave(font, path)


def empty_notices(web):
    with open(os.path.join(web, "THIRD_PARTY_NOTICES.txt"), "w") as handle:
        handle.write("")


def tamper_font_bytes(web):
    path = core_file(web)
    with open(path, "rb") as handle:
        raw = bytearray(handle.read())
    raw[-1] ^= 0xFF
    with open(path, "wb") as handle:
        handle.write(raw)


def wrong_total_bytes(web):
    path = os.path.join(web, "manifest.json")
    recorded = manifest(web)
    recorded["total_bytes"] += 4096
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(recorded, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def rewrite_css(web, old, new):
    path = os.path.join(web, "glg-mono.css")
    with open(path, encoding="utf-8") as handle:
        css = handle.read()
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(css.replace(old, new))


def css_typo(web):
    rewrite_css(web, manifest(web)["faces"][FACE]["tiers"]["core"]["file"],
                "GLG-Mono-Regular-core.deadbeef.woff2")


def css_drops_hangul(web):
    rewrite_css(web, "U+AC00-D7A3", "U+AC00-AC01")


def css_font_synthesis(web):
    path = os.path.join(web, "glg-mono.css")
    with open(path, encoding="utf-8") as handle:
        css = handle.read()
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("* { font-synthesis: style; }\n" + css)


def css_tiers_overlap(web):
    rewrite_css(web, "unicode-range: U+2E80-2FDF",
                "unicode-range: U+AC00-D7A3, U+2E80-2FDF")


# (label, mutation, the gates it must trip)
MUTATIONS = [
    ("GSUB deleted from a shipped face",          drop_gsub,               "layout,shaping"),
    ("GPOS deleted from a shipped face",          drop_gpos,               "layout,shaping"),
    ("one ligature rule removed",                 break_one_ligature,      "layout,shaping"),
    ("a chain's SubstLookupRecord removed",       strip_one_chain_record,  "layout,shaping"),
    ("a chain rewired to another lookup",         retarget_one_chain_record, "layout,shaping"),
    ("BASE table dropped",                        drop_base,               "tables"),
    ("licence nameID 13 stripped",                strip_licence_names,     "licensing"),
    ("THIRD_PARTY_NOTICES.txt emptied",           empty_notices,           "notices"),
    ("one byte of a shipped font flipped",        tamper_font_bytes,       "manifest"),
    ("manifest total_bytes disagrees",            wrong_total_bytes,       "manifest"),
    ("CSS points at a file that is not there",    css_typo,                "stylesheet"),
    ("CSS range no longer covers Hangul",         css_drops_hangul,        "stylesheet"),
    ("CSS forces font-synthesis",                 css_font_synthesis,      "stylesheet"),
    ("CSS lets both tiers claim Hangul",          css_tiers_overlap,       "stylesheet"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web", default="build/web")
    args = parser.parse_args()

    if not os.path.exists(os.path.join(args.web, "manifest.json")):
        raise SystemExit(f"{args.web} holds no distribution — run `task web:build` first")

    scratch = tempfile.mkdtemp(prefix="glg-web-gates-")
    escaped = []
    try:
        print(f"{'planted defect':44s} {'gate':16s} {'verdict':8s} {'s':>5}")
        print("-" * 78)
        for label, mutate, gates in MUTATIONS:
            web = os.path.join(scratch, "web")
            shutil.rmtree(web, ignore_errors=True)
            shutil.copytree(args.web, web)
            mutate(web)

            started = time.time()
            result = subprocess.run(
                [sys.executable, "webfont_verify.py", "--web", web,
                 "--faces", FACE, "--gates", gates],
                capture_output=True, text=True,
            )
            caught = result.returncode != 0
            if not caught:
                escaped.append(label)
            print(f"{label:44s} {gates:16s} {'CAUGHT' if caught else 'ESCAPED':8s} "
                  f"{time.time() - started:5.1f}", flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print("-" * 78)
    if escaped:
        print(f"{len(escaped)} defect(s) went unnoticed: {escaped}")
        return 1
    print(f"every one of the {len(MUTATIONS)} planted defects was caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
