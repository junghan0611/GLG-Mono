# Web Font Delivery — Two-Tier Design

Status: **implemented; all gates green** (2026-07-13). Build with `task web:all`.

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

1. **Coverage** — per-face cmap union and disjointness as defined above. Catches a bad seed, a
   missing PUA exclusion, or the small per-face cmap differences.
2. **Geometry** — every retained glyph keeps its decomposed outline (`DecomposingRecordingPen`),
   advance and LSB. Check **glyphs, not just encoded codepoints**: layout closure drags in
   unencoded dependencies, and composite glyphs are re-pointed at new GIDs.
3. **Hinting** — retained glyph bytecode matches the source, and `cvt `/`fpgm`/`prep`/`gasp` are
   binary-identical. Do not demand binary equality of composite glyph records; their component
   GIDs are renumbered by design.
4. **Metrics** — compare **fields, not tables**. Equal: UPM, `hhea` ascent/descent/lineGap, OS/2
   vertical metrics, `xAvgCharWidth`, `post.isFixedPitch` and `post.italicAngle`. Necessarily
   different: `hhea.numberOfHMetrics`, `maxp.numGlyphs`, `head.checkSumAdjustment`. A whole-table
   equality check here is simply wrong and will fail on a correct subset.
5. **Shaping** — the highest-risk gate. Close the dependency graph *before* partitioning, then
   verify lookup coverage after subsetting, then run shaping canaries. GPOS in the current source
   is four type-4 mark-to-base lookups whose marks and bases are all Latin/Cyrillic, so they land
   in `core` and never straddle the boundary — but the builder must derive that, not assume it:
   bind each `MarkBasePos` subtable's encoded `MarkCoverage ∪ BaseCoverage` into one component.
   GSUB is type 1/3/4 only; a type-4 ligature's input sequence must not cross tiers. If a
   contextual type 5/6 or an extension lookup ever appears, **fail closed** rather than ignore it.
6. **Global tables** — preserve `BASE`. `pyftsubset` drops unknown tables by default, so
   `--passthrough-tables` is required and the result must be verified binary-identical.
7. **Licensing** — `pyftsubset` keeps only nameIDs 0–6 by default, dropping 13/14. Pass
   `--name-IDs='*' --name-legacy --name-languages='*'` and verify nameID 0/13/14 content against
   the source. Ship `OFL.txt` and `THIRD_PARTY_NOTICES.txt` (IBM Plex, PlemolJP/PlemolKR, Hack,
   Bitstream Vera).
8. **Determinism** — two builds from a clean staging directory produce identical hashes for all
   eight WOFF2 files, the CSS and the manifest. Required because notes serves WOFF2 immutable for
   a year.

### Verifying without depending on glyph names

Dropping `post` glyph names (version 3.0) is a legitimate size optimisation, but correctness must
not hang on names being present. Build in two steps:

1. Subset **with** `--glyph-names`, and verify everything above against the source by glyph name.
2. Rewrite only `post` to 3.0 for the shipped WOFF2, then diff every sfnt table except `post`
   against the verified intermediate, and separately confirm `post`'s header fields.

Measured on the full Regular face, post 3.0 saves 79,768 bytes (2,672,456 → 2,592,688, about 3%).
That is not enough to justify weakening verification, so names stay until the pipeline is green.
Prefer emitting a source-name → output-GID map into the manifest over `--retain-gids`.

Note that `test_advance_widths.py` guards the *desktop* build and must not be pointed at a `jp`
tier: that tier has neither the Console discriminator characters nor most of the Latin contract
glyphs. The web verifier compares each tier against its source face instead, which subsumes the
zero-advance check.

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

## How the stylesheet declares its ranges

`core` is declared exactly — 229 spans, about 2 KB per face.

`jp` is declared as the **blocks it stands for**, not as its exact cmap. Stating the jp cmap
precisely takes 4,664 spans, because the font fills the CJK blocks unevenly: 50 KB per face,
200 KB across the four. The garden bundles its stylesheet into one render-blocking `index.css`
(39 KB today), so that would move the weight we came to remove out of the font and into the CSS.

The cost of declaring the blocks whole is that the font does not contain every ideograph in them.
For a missing one the browser fetches the jp tier and then falls back to a system font — a wasted
request, never a wrong glyph, and a page whose only CJK is an ideograph this font lacks would have
had to fall back anyway. Codepoints that shaping pulls into `core` are punched out of the jp range,
so the tiers never claim the same character; the verifier checks that.

Measured: 210.5 KB of CSS becomes 11.3 KB (1.1 KB brotli).

## Performance gate

Earlier 65 KiB Hangul and 175 KB homepage figures belonged to the discarded many-chunk prototype
and are invalid here. The numbers below are **measured**, by subsetting the built Regular/Bold TTFs
to the two tiers and encoding real WOFF2:

```text
Regular     core   569.3 KB   jp  1900.3 KB     full face today: 2582 KB
Bold        core   500.6 KB   jp  1958.9 KB     full face today: 2573 KB
Italic      core   622.8 KB   jp  2048.1 KB
BoldItalic  core   548.3 KB   jp  2129.4 KB
```

Korean home page = Regular-core + Bold-core = **1,070 KB**, against **5,280 KB** today, an 80% cut.
(The earlier 973 KB estimate omitted the `post` glyph names, which the pipeline keeps so that
verification can address glyphs by name.) That is the
honest ceiling of a corpus-free design: Hangul cannot be split further without frequency data,
because Korean text scatters across the syllable block and would fetch every codepoint-ordered
slice anyway. A page containing even one Han character still pulls the 1.87 MB `jp` tier.

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
