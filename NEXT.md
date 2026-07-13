# NEXT — GLG-Mono

Boot sector for the next session. Durable rules live in `AGENTS.md`; design detail lives in
`docs/WEBFONT_SUBSET.md`.

# NOW — eight-file, two-tier web fonts

- **Stem**: the garden currently stores four full WOFF2 faces (~11 MB); a normal home page requests
  full Regular + Bold (~5.28 MB). Preserve font quality while making ordinary Korean pages request
  only the Korean/core portions.
- **Decision reset (2026-07-13)**: the 192-file frequency prototype was discarded before commit.
  The output contract is now **8 WOFF2 files total**: `core` + `jp` for each of
  Regular/Bold/Italic/BoldItalic. A normal Korean home page should request exactly two:
  Regular-core and Bold-core.
- **Read first**: `docs/WEBFONT_SUBSET.md` is the SSOT. Do not reuse the discarded 8-Hangul/32-Han
  maps or their size projections.

## Next concrete move

1. ~~Dev environment~~ **done (2026-07-13)**: `shell.nix` is gone. `flake.nix` pins nixos-26.05
   (the host system's own nixpkgs rev) with generic `python3` + fontTools + **brotli**. Enter with
   `nix develop`. Two 26.05 toolchain breaks were found and fixed — see `AGENTS.md`.
2. Implement one static two-tier builder. No corpus input and no frequency map.
3. Emit 8 content-hashed WOFF2 files plus CSS, manifest, `OFL.txt` and
   `THIRD_PARTY_NOTICES.txt` under `build/web/`.
4. Implement the exhaustive verifier, then run two deterministic builds.
5. Report actual sizes. Integrate into a Quartz preview only after local quality gates pass.

## Measured, not projected (2026-07-13)

The first real WOFF2 measurement of the two-tier split, on the built Regular/Bold faces:

```text
Regular  core 520.6 KB   jp 1868.0 KB   (full face today: 2582 KB)
Bold     core 452.6 KB   jp 1928.1 KB   (full face today: 2573 KB)
```

A Korean home page requests Regular-core + Bold-core ≈ **973 KB**, against **5,280 KB** today —
an 82% cut. Splitting Hangul further without frequency data buys nothing: Korean text scatters
across the syllable block, so codepoint-ordered slices all get fetched anyway. One Han character on
a page still pulls the 1.87 MB `jp` tier; that is the known sharp edge of this design.

## Output contract

```text
4 source faces × {core,jp} = 8 WOFF2 files
home page expected requests = Regular-core + Bold-core = 2
```

- `core`: Latin, all Hangul/Jamo, common punctuation/symbols and complete GPOS mark/base clusters.
- `jp`: Han, Kana, CJK radicals/Japanese forms and related GSUB multi-input clusters.
- Per face, union equals source cmap minus the declared 14 PUA codepoints; tiers are disjoint.
- Physical Italic/BoldItalic outlines stay. Do not replace them with browser synthesis.

## Verified traps — carry forward

- `pyftsubset` drops legal name records unless nameID 0/13/14 are explicitly retained.
- `--drop-tables=` does not preserve unknown `BASE`; passthrough and verification are required.
- GPOS mark glyphs **and every covered base** must share a tier. Checking only GDEF class-3 marks
  misses Cyrillic bases.
- GSUB ligature input sequences must share a tier. CJK radicals `U+2E80–2FDF` are not punctuation.
- Source face cmaps differ slightly; preserve each face independently.
- Content-hashed names are mandatory because notes serves WOFF2 with a one-year immutable cache.
- Generated font CSS must not set a global `font-synthesis` policy.

## Stop conditions

- Do not touch `fontforge_script.py`, `fonttools_script.py` or `build.ini`.
- Do not restructure away from the inherited PlemolJP/IBM Plex Sans JP base.
- Do not add corpus-trained data, 8/32 frequency slices, or more than 8 WOFF2 outputs.
- Do not promise a target byte count before measuring the actual two-tier build.
- Do not vendor artifacts into `notes` until browser waterfall, LCP, CLS and shaping canaries pass.

# RECENT

- [2026-07-13] Repo protocol baseline committed as `8fe39d2` (`AGENTS.md`, `NEXT.md`, design SSOT).
- [2026-07-13] A 192-file prototype was built but not committed. It demonstrated selective loading
  and exhaustive glyph checks, but exposed compression-context costs and cross-file shaping traps.
  The prototype was removed; only its durable lessons remain in the design.
- v1.0.0 has no public GitHub release yet. Unrelated to this work and not scheduled.
