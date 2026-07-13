# NEXT — GLG-Mono

Boot sector for the next session. Durable rules live in `AGENTS.md`; design detail lives in
`docs/WEBFONT_SUBSET.md`.

# NOW — the fonts are built and verified; nobody has looked at them

- **Stem**: the garden makes an ordinary Korean page download 5,280 KB of font. The two-tier web
  build brings that to **1,070 KB** (80% off) with eight WOFF2 files, no corpus and no chunking.
- **State**: `task web:all` builds and verifies. Every gate is green and every gate has been shown
  to bite — see below. `build/web/` is gitignored; nothing has been vendored into `notes`.
- **The gap**: **not one glyph has been rendered in a browser.** The gates prove the tiers are the
  font; they do not prove a page looks right. That is the whole of what remains.

## Next concrete move — browser integration in `notes`

1. Copy `build/web/*.woff2` into `~/repos/gh/notes/quartz/static/fonts/`, replacing the four full
   faces (11 MB) with the eight tiers.
2. Replace the four `@font-face` blocks in `quartz/styles/custom.scss` with the eight from
   `build/web/glg-mono.css`. **The generated `src:` URLs are bare filenames**; Quartz serves from
   the site root, so they need the `/static/fonts/` prefix. Decide whether the builder should emit
   that prefix (an option) or the copy step should rewrite it, and write the choice down.
3. Build the garden locally and look at it: Korean body text, a page with 漢字, italics, bold,
   NFD combining accents, Jamo, and a code block with ligatures.
4. Watch the network waterfall: a Korean home page must request **Regular-core and Bold-core, and
   nothing else**. Record the transfer size, LCP and CLS.
5. Only then ship.

## What the verifier actually checks

`webfont_verify.py` reads the **shipped WOFF2**, not the source it came from. An earlier version
checked the source and let a face with GSUB deleted pass green — the reason every gate below is now
stated in terms of the delivered file.

| Gate | What it would catch |
|---|---|
| coverage | a codepoint lost or duplicated across tiers |
| geometry | an outline, advance or LSB that moved |
| hinting | glyph bytecode or `cvt`/`fpgm`/`prep`/`gasp` altered |
| metrics | vertical metrics or `xAvgCharWidth` drifting (field-level; `numberOfHMetrics` must change) |
| tables | `BASE` dropped — `pyftsubset` discards unknown tables by default |
| layout | a substitution or mark-attachment rule missing from the shipped file |
| shaping | HarfBuzz shaping the tier differently from the full font, across 3,216 derived canaries |
| stylesheet | a bad URL, a range that does not cover the file, tiers both claiming a character, `font-synthesis` |
| manifest | a file whose bytes no longer match its content-hashed name |
| determinism | a rebuild that does not reproduce all 13 files byte for byte |

Eleven planted defects are all caught (`--faces Regular --gates <gate>` keeps a probe at ~1 s;
the full sweep walks every outline and shapes thousands of strings, so do not run it per mutation).

## Verified traps — carry forward

- `pyftsubset` drops nameID 0/13/14 unless given `--name-IDs='*' --name-legacy`.
- `--drop-tables=` does not preserve unknown `BASE`; `--passthrough-tables` does.
- **HarfBuzz cannot read WOFF2.** Decompress before shaping, or every glyph comes back `.notdef`.
- The font has **chained-contextual GSUB (type 6)**, not just types 1/3/4. An unknown lookup type
  must fail the build, not be skipped.
- Declaring the jp tier's exact cmap costs 4,664 `unicode-range` spans — 200 KB of render-blocking
  CSS. The blocks are declared whole instead; a missing ideograph costs a wasted request, never a
  wrong glyph.
- Content-hashed names are mandatory: notes serves WOFF2 immutable for a year.

## Stop conditions

- Do not restructure away from the inherited PlemolJP/IBM Plex Sans JP base. A KR-based rewrite is
  a v2 with golden parity, not a cleanup.
- Do not add corpus-trained data, frequency slices, or more than 8 WOFF2 outputs.
- Do not "fix" the 27 IBM Plex Sans JP combining marks that are full-width. They have been wrong
  since v1.0.0, they have no GPOS mark lookup, and setting their advance to 0 without anchors would
  trade one rendering defect for another. Separate decision, separate canaries.
- Do not vendor into `notes` until the browser waterfall, LCP, CLS and shaping canaries pass.

# RECENT

- [2026-07-13] `fa770da` — verifier rewritten to check the shipped files: layout rules read back
  from the WOFF2, HarfBuzz canaries derived from the font's own rules, stylesheet/manifest/notices
  gates, byte-for-byte determinism. Eleven mutations all caught.
- [2026-07-13] `d289e4e` — eight-file two-tier web build. 5,280 KB → 1,070 KB.
- [2026-07-13] `ef67095`, `3dbf108`, `af273a3` — FontForge 20251009 over-compresses `hmtx` and
  destroys zero-width glyphs at every TTF round-trip. Four round-trips, all guarded by
  `font_widths.py`; `task verify:widths` is the gate. The 26.05 build reproduces the shipped
  v1.0.0 fonts exactly across all 35,402 glyphs.
- [2026-07-13] `2ea3262` — `shell.nix` replaced by `flake.nix` on nixos-26.05.
- A cleanup pass (dead code, duplicate build paths, stale docs) is wanted but was deliberately kept
  out of this work. It is its own session.
- v1.0.0 has no public GitHub release. Unrelated and not scheduled.
