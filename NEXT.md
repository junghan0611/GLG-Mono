# NEXT — GLG-Mono

Boot sector for the next session. Durable product direction: `AGENTS.md`. v2 design:
`docs/V2_KOREAN_PROFILE.md`. Web baseline and verifier: `docs/WEBFONT_SUBSET.md`.

# NOW — v2-A Regular proof of the Korean-first product contract

## North star

GLG-Mono is a **Korean programming and knowledge-work font**:

```text
Hangul (Plex Sans KR)
+ Latin (Plex Mono)
+ BMP Korean-profile Hanja (explicit donor)
+ coding/Korean symbols (Plex Mono, Hack, custom, optional Nerd Fonts)
```

PlemolJP is heritage, not product identity. Japanese syllabaries, Bopomofo, Japanese-only forms and
regional GSUB features are outside the v2 repertoire. Repertoire and outline donor are independent.

## Fixed decisions

- **Hanja repertoire**: Source Han Sans KR 2.005 BMP cmap, exactly **8,567 mappings**. The 84
  supplementary Korean-subset mappings are deliberately delegated to fallback in v2-A.
- **v2-A donor**: the vendored IBM Plex Sans JP. It directly draws 7,686 profile mappings; 250
  compatibility aliases raise renderable coverage to 7,936/8,567. The remaining 631 fall back.
- **Regional forms**: JP forms are accepted for the v2-A proof, not declared Korean-canonical. A
  donor change later requires provenance, geometry golden updates and visual proof.
- **Web**: independent four-face delivery; GLG WOFF2 claims neither Han nor Japanese syllabaries.
  Browser fallback renders Han. No frequency chunks or corpus maps.
- **Architecture gate**: v2-A may use the inherited JP-base assembly to prove the output contract.
  If Japanese cmap/layout/metric coupling cannot be removed cleanly, stop and move to v2-B
  neutral/KR-first assembly. Do not normalize fragile exceptions into the final architecture.

# Next concrete move

1. **Profile maintenance surface**
   - Add `work_scripts/gen_hanja_profile.py` and generated `source/korean-hanja-profile.txt`.
   - Record upstream URL/version/input SHA-256/output SHA-256 and the explicit BMP-only scope.
   - Normal builds are offline; a maintenance command regenerates only after verifying the pinned
     upstream artifact. No education list, hand curation or garden frequency.
2. **Regular-only `/tmp` proof before repo productization**
   - Keep only JP donor Han in the 8,567-profile intersection.
   - Alias supported CJK Compatibility Ideographs to canonical base glyphs without new outlines.
   - Remove Kana/Bopomofo/Japanese-only encoded and unencoded glyphs.
   - Replace all U+3042 width sentinels with explicit product/Korean metrics.
   - Remove or rewrite dangling GSUB/UVS references; audit `jp78`, `jp83`, `jp90`, `hkna`, `vkna`,
     `ruby`, `hojo`, `nlck`, `trad`, `vert` and `locl` after deletion.
3. **Decision report before all weights**
   - Report cmap/glyph counts, TTF size, retained scripts/features, missing profile mappings,
     compatibility aliases, width failures and screenshot canaries.
   - Compare Latin/Hangul/symbol geometry against v1 and run `task verify:widths`.
   - If the output is clean, productize all weights/styles. If not, activate v2-B KR-first assembly.
4. **Keep web moving separately**
   - Implement the four-face Han/Kana-free WOFF2 contract against the current desktop artifact.
   - Re-sync the uncommitted notes checkpoint and verify `脈`/`如` render through fallback with no
     GLG `jp` request before committing notes.

## Acceptance

- The profile is reproducible from pinned provenance and explicitly named **BMP Korean profile**.
- `一日一生`, `道`, `無學論道`, `脈`, `如` render without tofu; donor misses fall back deliberately.
- No undeclared Kana, Bopomofo, Japanese-only forms or Japanese regional GSUB features survive.
- Compatibility aliases, cmap 12/14, UVS and retained GSUB have no dangling references.
- Latin/Hangul/coding symbols retain v1 geometry and shaping; retained Hanja are fullwidth.
- `task verify:widths` guards all four FontForge round-trips.
- Four legal provenance records remain in nameID 0; no source or copyright is silently erased.
- Web pages request only GLG core faces and no Han payload; system/remote fallback owns Han.

## Stop conditions

- Do not call excluded Han “Japanese-only”; say **outside the selected Korean profile**.
- Do not claim TC or JP is Korean-canonical. Regional-form quality needs separate proof.
- Do not claim a donor swap leaves verification untouched; geometry goldens and provenance change.
- Do not machine-claim that a file was not corpus-derived unless exact regeneration proves it.
- Do not revive education lists, garden-trained profiles, frequency tiers or the 192-file prototype.
- Do not push v2-A through all weights if the Regular proof leaves Japanese structural coupling.

# RECENT

- [2026-07-14] This handoff established the Korean-first north star and split repertoire, donor
  and web delivery into independent contracts.
- [2026-07-14] Local measurements: Plex Sans KR has zero Han; current GLG inherits 13,412 Han and
  about 1,048 non-Han codepoints uniquely from JP. The Source Han KR profile is 8,567 BMP mappings
  plus 84 supplementary mappings.
- [2026-07-14] `981199a` made web Han a fallback concern; the 8-file `{core,jp}` build remains a
  verified baseline, not the final delivery.
- [2026-07-13] `a6cf1a7` added chained-context semantics and fourteen mutation probes.
- [2026-07-13] `ef67095`, `3dbf108`, `af273a3` repaired FontForge advance widths at all four TTF
  round-trips; `task verify:widths` remains mandatory.
