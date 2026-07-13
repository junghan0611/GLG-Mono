# Web Font Delivery — Two-Tier Design

Status: **direction reset; implementation not started** (2026-07-13)

This design changes only the web deliverable. The inherited PlemolJP desktop build remains intact:
IBM Plex Sans JP stays the base, and desktop TTF/NF releases retain their complete coverage.

## Contract

The build emits exactly **8 WOFF2 files**: two tiers for each existing face.

```text
GLG-Mono-Regular-core.<hash>.woff2
GLG-Mono-Regular-jp.<hash>.woff2
GLG-Mono-Bold-core.<hash>.woff2
GLG-Mono-Bold-jp.<hash>.woff2
GLG-Mono-Italic-core.<hash>.woff2
GLG-Mono-Italic-jp.<hash>.woff2
GLG-Mono-BoldItalic-core.<hash>.woff2
GLG-Mono-BoldItalic-jp.<hash>.woff2
```

CSS, a manifest and licence notices accompany them but are not font binaries.

A normal Korean home page should request only two fonts:

```text
Regular-core + Bold-core
```

Italic files are requested only where italic text occurs. The JP tail is requested only when its
codepoints occur. Do not introduce frequency tiers, corpus-trained maps, or dozens of files.

## Why eight, not two

Two physical files total would mean Regular and Bold only. That either keeps the current full
27,000-codepoint payload, yielding little reduction, or drops the real Italic/BoldItalic designs
and relies on synthesis, which is a quality regression. Four physical faces are therefore the
minimum quality-preserving set. Splitting each face once gives eight files while keeping ordinary
page requests at two.

## Tier boundary

### `core`

- Latin and all encoded non-Japanese scripts
- all 11,172 modern Hangul syllables
- Hangul Jamo and compatibility Jamo
- common punctuation, symbols, box drawing and fullwidth forms needed by Korean text
- complete GPOS mark/base input clusters required for decomposed text

### `jp`

- CJK Unified and Compatibility Ideographs
- Hiragana, Katakana and halfwidth Kana
- CJK/Kangxi radicals and Japanese-specific forms
- related GSUB multi-codepoint input clusters

The seed classification is only a starting point. Shaping closure decides boundary cases:

- every encoded input participating in one GPOS mark lookup must remain in one tier;
- every encoded multi-codepoint GSUB ligature input must remain in one tier;
- CJK radicals must not be mistaken for punctuation merely because their Unicode blocks are near
  `U+3000`;
- single-substitution output glyphs may remain unencoded dependencies included by fontTools.

If a shaping cluster crosses the initial boundary, move the whole cluster to the appropriate tier.
Never solve the problem by duplicating an overlapping `unicode-range`.

## Coverage and style policy

Per face:

```text
cmap(core) ∪ cmap(jp) == cmap(source) − declared PUA exclusion
cmap(core) ∩ cmap(jp) == ∅
```

The inherited source faces differ slightly: Regular/Italic and Bold/BoldItalic do not encode
exactly the same small Latin/combining set. Preserve each face independently; do not force a common
intersection or union.

Italic and BoldItalic keep their physical outlines. Latin is IBM Plex Mono's true italic; CJK is
the inherited 9° transformed outline. The generated stylesheet must not impose a global
`font-synthesis` policy.

The existing 14 PUA codepoints remain the only deliberate web-profile exclusion. Record them in
the manifest. Do not silently remove any other encoded character.

## Quality gates

Every generated face/tier must pass:

1. **Coverage** — per-face cmap union and disjointness as defined above.
2. **Geometry** — every retained encoded codepoint keeps decomposed outline, advance and LSB.
3. **Hinting** — glyph programs and global `cvt `/`fpgm`/`prep`/`gasp` data remain equivalent.
4. **Metrics** — UPM, hhea, OS/2 vertical metrics, `xAvgCharWidth` and `isFixedPitch` remain equal.
5. **Shaping** — GPOS mark/base and GSUB multi-input clusters do not cross tiers; fixed canaries
   compare source and web shaping.
6. **Global tables** — preserve `BASE`. `pyftsubset --drop-tables=` alone is insufficient because
   unknown tables are still dropped; use and verify the appropriate passthrough behavior.
7. **Licensing** — preserve nameID 0/13/14 content and ship `OFL.txt` plus
   `THIRD_PARTY_NOTICES.txt` for IBM Plex, PlemolJP/PlemolKR, Hack and Bitstream Vera provenance.
8. **Determinism** — two builds from the same source produce identical hashes.

Dropping non-rendering `post` glyph names may be evaluated as a size optimization, but only after
all rendering and licence gates remain green.

## Build shape

The release build:

- runs inside `nix develop` (`flake.nix`, nixos-26.05);
- uses the nixpkgs default `python3` package set plus fontTools and Brotli;
- reads only the four source TTFs and static two-tier rules;
- never reads the garden or an external corpus;
- writes to a staging directory and replaces `build/web/` without mixing stale outputs;
- emits content-hashed filenames, CSS, manifest and licence notices.

Planned tasks:

```sh
task web:build
task web:verify
task web:all       # build + verify, no corpus dependency
```

## Performance gate

Earlier 65 KiB Hangul and 175 KB homepage figures belonged to the discarded many-chunk prototype
and are invalid here. The numbers below are **measured**, by subsetting the built Regular/Bold TTFs
to the two tiers and encoding real WOFF2:

```text
Regular   core   520.6 KB   jp  1868.0 KB     full face today: 2582 KB
Bold      core   452.6 KB   jp  1928.1 KB     full face today: 2573 KB
```

Korean home page = Regular-core + Bold-core ≈ **973 KB**, against **5,280 KB** today. That is the
honest ceiling of a corpus-free design: Hangul cannot be split further without frequency data,
because Korean text scatters across the syllable block and would fetch every codepoint-ordered
slice anyway. A page containing even one Han character still pulls the 1.87 MB `jp` tier.

These are pipeline measurements, not a shipped result. Treat them as the size budget the real build
must reproduce, and re-measure the Italic faces when they are cut.

After building:

1. report all eight file sizes and total distribution size;
2. verify in a real browser that the home page requests only Regular-core and Bold-core;
3. record homepage font bytes, request count, LCP and CLS on a Quartz deploy preview;
4. test Korean, Han/Kana, italic, bold-italic, NFD combining, Jamo and GSUB ligature canaries;
5. ship only after GLG accepts the measured size/quality tradeoff.

## Discarded prototype

A garden-frequency prototype generated 192 WOFF2 files using 8 Hangul and 32 Han slices per face.
It proved that roughly 200–500 KiB page transfers are possible, and it exposed important licence,
`BASE`, GPOS and GSUB traps. It was discarded because its operational complexity contradicted this
repository's cleanup goal and still missed provisional p95 targets.

Do not revive its corpus maps or 8/32 slicing without a new explicit decision. The useful lessons
have been promoted into the quality gates above.
