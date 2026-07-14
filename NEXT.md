# NEXT — GLG-Mono

Boot sector for the next session. Durable rules live in `AGENTS.md`; the current implementation
baseline and verifier contract live in `docs/WEBFONT_SUBSET.md`.

# NOW — keep desktop Han; delegate web Han to fallback

- **Decision (2026-07-14)**: desktop TTF/NF remains complete, including all inherited Han. The
  size-driven exclusion applies **only to the web WOFF2 deliverable**. Never remove Han from the
  source build or restructure the PlemolJP/IBM Plex Sans JP base for this work.
- **Web contract**: GLG web faces no longer need to carry Han. A browser/system or remote CJK
  fallback may render Han; readable, non-tofu output is sufficient, and pixel parity with the
  desktop GLG Han outlines is not required on the web.
- **Why**: the verified 8-file `{core,jp}` experiment makes a no-Han page 5,280 KB → 1,072 KB, but
  one Han character opens an entire ~2 MB face. Homepage `脈` measured 3,031 KB and a sparse-Han
  `如` note measured 5,556 KB.
- **State**: GLG-Mono is clean and pushed. `~/repos/gh/notes` contains the 8-file integration as an
  intentionally uncommitted browser checkpoint; do not commit or discard it before the A/B proof.

## Next concrete move — prove Han fallback, then replace the web contract

1. In the notes checkpoint, temporarily stop declaring the `*-jp` faces and add an explicit CJK
   fallback after `"GLG Mono"`. Try installed system CJK fonts first; use a range-split remote font
   such as Noto Sans KR only if system rendering is inconsistent or produces tofu.
2. Browser-check the homepage `脈` and the sparse-Han `如` note. Record requested WOFF2 files,
   transfer bytes, screenshots, and whether normal/bold Han remains readable. Also check a Kana
   canary: the decision excludes Han, not Japanese syllabaries by accident.
3. If the proof passes, revise `docs/WEBFONT_SUBSET.md`, then change only the web builder/verifier:
   - emit four physical GLG faces with Han absent from their cmap/CSS claim;
   - retain Kana and required cross-codepoint shaping inputs in the supported web profile;
   - declare the intentional Han fallback set in the manifest;
   - verify excluded Han is not claimed, supported web glyphs preserve geometry/layout, and the
     desktop TTF cmap/artifacts are untouched.
4. Run `task web:test-gates`, then `task web:all` once as the release checkpoint. Re-sync notes,
   repeat the two browser measurements, and commit the notes integration only after GLG approves
   the rendering and payload.

## Acceptance

- Desktop TTF/NF keeps all inherited Han and existing build parity; no desktop pipeline edits.
- Homepage `脈` and note `如` request no GLG `jp` WOFF2 and display no tofu.
- A normal Korean page still requests only Regular and Bold GLG core faces; Italic/BoldItalic stay
  physical and load only when used.
- Kana, Hangul/Jamo, punctuation, symbols, hinting, metrics, legal names, `BASE`, GSUB/GPOS and
  deterministic content hashes remain guarded.
- The final web topology is stated before coding: artifact count, normal-page requests, intentional
  exclusions and fallback owner. Any later topology change requires GLG approval.

## Stop conditions

- Do not remove Han from source fonts, desktop TTF/NF, or the inherited JP base.
- Do not revive corpus-trained frequency maps, Han frequency tiers, or the discarded 192-file
  prototype. Han fallback replaces that complexity.
- Do not hand-edit generated notes SCSS as the final fix; the builder/sync path must own it.
- Do not commit the current notes 8-file checkpoint as the final delivery.
- Cleanup and the KR-first rewrite remain separate work:
  <https://github.com/junghan0611/GLG-Mono/issues/2>.

# RECENT

- [2026-07-14] GLG separated the product contracts: full Han remains in desktop TTF/NF; web WOFF2
  may omit Han and delegate it to a CJK fallback to avoid multi-megabyte single-character fetches.
- [2026-07-13] Notes integration rendered correctly. No-Han pages reached 1.07 MB, but sparse-Han
  pages exposed the coarse `jp` tier: homepage 3.03 MB; `如` note 5.56 MB.
- [2026-07-13] `a6cf1a7` hardened chained-context verification and added fourteen mutation probes;
  `d289e4e` implemented the verified 8-file baseline now being superseded.
- [2026-07-13] `ef67095`, `3dbf108`, `af273a3` repaired FontForge 20251009 advance-width damage at
  all four TTF round-trips. `task verify:widths` is the desktop guard.
