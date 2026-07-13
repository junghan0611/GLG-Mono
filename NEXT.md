# NEXT — GLG-Mono

Boot sector for the next session. Durable rules live in `AGENTS.md`; design detail lives in
`docs/WEBFONT_SUBSET.md`.

# NOW — webfont delivery complete; measured feedback pending

- **Result**: the garden's ordinary Korean page font payload fell from 5,280 KB to **1,070 KB**
  (80% off): eight WOFF2 files, no corpus and no chunking; Regular-core + Bold-core are the normal
  two requests.
- **Proof**: `task web:all` is green across all four faces; `task web:test-gates` plants fourteen
  defects and catches all fourteen. The full verifier compares shipped layout rules, thousands of
  HarfBuzz strings and all thirteen distribution files deterministically.
- **Delivery**: `~/repos/gh/notes` now owns a deterministic `scripts/sync-webfonts.sh` that copies
  the verified distribution and generates `/static/fonts/` URLs. GLG has visually confirmed the
  local garden. The notes-side performance evaluation is still running and may return requirements.

## Next concrete move — wait for measured notes feedback

1. Do not change the desktop font or invent another subset. Receive the notes-side waterfall,
   transferred bytes, LCP and CLS results first.
2. If a font requirement returns, reproduce it against `build/web/`, make the smallest web-layer
   change, then run `task web:test-gates` and `task web:all` before re-syncing notes.
3. If no font requirement returns, this lane is complete. Cleanup and the KR-first rewrite remain
   separate work; roadmap: <https://github.com/junghan0611/GLG-Mono/issues/2>.

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
| layout | a substitution, mark-attachment or **chained-context record** missing or rewired |
| shaping | HarfBuzz shaping the tier differently from the full font, across 3,233 derived canaries |
| stylesheet | a bad URL, a range that does not cover the file, tiers both claiming a character, `font-synthesis` |
| manifest | a file whose bytes no longer match its content-hashed name, or a wrong `total_bytes` |
| determinism | a rebuild that does not reproduce all 13 files byte for byte |

`task web:test-gates` (`test_webfont_gates.py`, ~24 s) plants **fourteen** defects and demands a
FAIL for each. Add a gate only with the mutation that proves it bites. The full sweep walks every
outline and shapes thousands of strings, so never run it per mutation — `--faces Regular
--gates <gate>` keeps a probe at ~1 s.

## Verified traps — carry forward

- `pyftsubset` drops nameID 0/13/14 unless given `--name-IDs='*' --name-legacy`.
- `--drop-tables=` does not preserve unknown `BASE`; `--passthrough-tables` does.
- **HarfBuzz cannot read WOFF2.** Decompress before shaping, or every glyph comes back `.notdef`.
- The font has **chained-contextual GSUB (type 6)**, not just types 1/3/4. An unknown lookup type
  must fail the build, not be skipped.
- **A type-6 rule is its `SubstLookupRecord`, not its coverage.** Delete the record and the context
  still matches, substituting nothing; coverage compares equal and the loss is invisible. Lookup 25
  (`ccmp`, invokes lookup 26) has coverage *identical* to lookup 29, which has no records at all —
  so a coverage-keyed rule set cannot even tell them apart. The layout gate spells each record out
  as `(SequenceIndex, rules of the lookup it names)`.
- **HarfBuzz composes before it lays out**, so shaping cannot stand in for that. `d` + U+030C
  becomes precomposed `dcaron` and the caron chain never fires; `g` + U+0326 and `j` + U+0300 have
  no precomposed form, fire, and are caught. A rule no text can reach still must not be dropped.
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
- Do not interpret notes-side PageSpeed work as permission to reopen the desktop font pipeline;
  measured font regressions return through the web-layer gates above.

# RECENT

- [2026-07-13] Notes integration — the generated eight-file distribution is synced through a
  deterministic notes-owned script; font hashes, sizes, CSS references and manifest totals agree,
  and GLG visually confirmed the local garden. Performance measurement remains notes-owned.
- [2026-07-13] Type-6 hardening — chained-context records are projected by their invoked lookup
  semantics, reachable chains add derived HarfBuzz canaries, and `task web:test-gates` permanently
  plants fourteen defects. All four faces pass the full release verifier.
- [2026-07-13] `fa770da` — verifier rewritten to check the shipped files: layout rules read back
  from the WOFF2, HarfBuzz canaries derived from the font's own rules, stylesheet/manifest/notices
  gates and byte-for-byte determinism.
- [2026-07-13] `d289e4e` — eight-file two-tier web build. 5,280 KB → 1,070 KB.
- [2026-07-13] `ef67095`, `3dbf108`, `af273a3` — FontForge 20251009 over-compresses `hmtx` and
  destroys zero-width glyphs at every TTF round-trip. Four round-trips, all guarded by
  `font_widths.py`; `task verify:widths` is the gate. The 26.05 build reproduces the shipped
  v1.0.0 fonts exactly across all 35,402 glyphs.
- [2026-07-13] `2ea3262` — `shell.nix` replaced by `flake.nix` on nixos-26.05.
- A cleanup pass (dead code, duplicate build paths, stale docs) is wanted but was deliberately kept
  out of this work. It is its own session.
- v1.0.0 has no public GitHub release. Unrelated and not scheduled.
