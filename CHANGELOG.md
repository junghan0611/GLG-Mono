# Changelog

Closed work moves here from `NEXT.md` through the `tag-release` loop. The current section remains
unreleased until GLG explicitly cuts a CalVer snapshot.

## Unreleased

## v2026.7.14 — GLG-Mono 재건축 기준선

### Repository rebuild

- Reframed GLG-Mono as 힣's owned, observable Unicode assembly: exact cmap, one owner per
  codepoint, allowlist-first inputs, and zero undeclared output.
- Replaced the inherited document tree with the root document set: `README.md`, `AGENTS.md`,
  `NEXT.md`, `ROADMAP.md`, and `CHANGELOG.md`; recovered durable findings before deleting the old
  research files.
- Promoted the Korean bearing formula and verification history into `AGENTS.md`/this changelog,
  moved math and Unicode-height ideas into measured later phases of `ROADMAP.md`, retained the web
  quality gates in `AGENTS.md`, and moved the terminal screenshot to `assets/`.
- Separated the shipped v1 facts from the pending v2 cmap contract and corrected stale build,
  release, coverage, and provenance claims.

### Build and verification

- Moved the build environment to a Nix flake pinned to nixos-26.05 and kept Python, fontTools,
  FontForge, Brotli, ttfautohint, Task, and fontconfig coherent.
- Repaired FontForge's compressed-`hmtx` corruption at all four TTF round-trips by snapshotting and
  restoring advance widths; added a glyph-name-based zero-advance regression gate.
- Adapted `ttfautohint-py` to the newer CLI wrapper by removing the unsupported `epoch` option from
  the parsed option dictionary.

### Web baseline

- Built a deterministic eight-file `{core,jp}` WOFF2 baseline for Regular, Bold, Italic, and
  BoldItalic, preserving physical italic faces and reducing an ordinary Korean page to the two core
  files. Measured per face: Regular `core` 569.3 KB / `jp` 1,900.3 KB, Bold 500.6 / 1,958.9, Italic
  622.8 / 2,048.1, BoldItalic 548.3 / 2,129.4. A Korean home page fell from 5,280 KB to 1,070 KB
  (Regular-core + Bold-core), an 80% cut — but a single Han character still pulled the 1.87 MB `jp`
  tier, which is why the four-face fallback contract supersedes this baseline.
- Cut the generated stylesheet from 210.5 KB to 11.3 KB by declaring the `jp` tier as whole Unicode
  blocks instead of its exact 4,664-span cmap.
- Added delivered-file verification for coverage, geometry, hinting, metrics, layout, shaping,
  `BASE`, legal names/notices, stylesheet truth, and deterministic hashes.
- Added fourteen mutation probes, including deleted GSUB/GPOS, stripped legal records, stylesheet
  lies, missing `BASE`, broken hashes, and chained-context records removed or rewired.
- Corrected chained-context verification to compare each `SubstLookupRecord` and the rules it
  invokes, rather than treating matching coverage as matching semantics.
- Superseded the two-tier delivery contract: final web output will be four Han/Kana-free faces, with
  browser fallback owning Han.

### Cmap contract

- Measured the current Regular face at 27,846 mapped codepoints against an expected 21,499:
  413 missing (163 Plex Sans KR characters plus 250 not-yet-created aliases) and 6,760 unexpected
  (1,424 non-Han plus 5,336 Han outside the claimed set).
- Fixed the Hanja seed direction at 8,567 BMP codepoints; the vendored JP donor resolves 7,686
  directly and 250 by compatibility alias, leaving 631 to fallback.

## v1.0.0 — 2026-03-17

- Published the initial GLG-Mono desktop, Nerd Fonts, and four-face WOFF2 assets inherited from the
  PlemolJP/PlemolKR build line.
- Shipped 11,172 modern Hangul syllables and the first bbox-centred Korean bearing repair.
- Centred IBM Plex Sans KR outlines from their 892-unit advance into the GLG fullwidth cell with
  `offset = (target_width - bbox_width) / 2 - bbox.xMin`; measured representative residual
  asymmetry at 0–2 units after TrueType rounding instead of the original 28–45 units.
- Added Nerd Fonts post-processing because FontForge/FontPatcher merging can disturb Korean
  bearings; `fix_nf_korean_bearing.py` reapplies centring and `task verify:bearing` compares NF with
  non-NF output.
- Established the Taskfile-based Console and 3:5 build paths, eight weights, physical italic faces,
  optional Nerd Fonts, and Linux/Emacs visual verification.
