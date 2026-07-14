# NEXT — GLG-Mono

Boot sector for the next session. Durable product direction: `AGENTS.md`. v2 contract:
`docs/V2_CMAP_CONTRACT.md`. Web baseline and verifier: `docs/WEBFONT_SUBSET.md`.

# NOW — make the font's cmap an owned, published contract

## North star

> GLG-Mono is a font for 힣's own working environment. It publishes its supported range as an exact
> Unicode cmap, traces every codepoint to an owner, and lets no undeclared character into the build.

No standard, no canonical repertoire, no "complete CJK font". Chasing that is what makes the code
explode. Three questions only: what does it support, where did each glyph come from, and does
anything unexpected sneak in.

## Fixed decisions

- **Exact cmap is the SSOT.** Range lists and the Emacs fontset are generated outputs. Blocks are
  mixed (`U+3300` holds both `㌀` and `㎏`), so **codepoint allowlists only — never block rules**.
- **Layer ownership**, higher wins: custom > Plex Mono (Latin/coding) > Plex Sans KR (Hangul and
  every Korean character it carries) > Plex Sans JP (**seed Hanja only**) > Hack > Nerd Fonts (NF
  variants only). JP has no path in for anything but seed Hanja, so nothing arrives to be excluded.
- **Take back the 163.** Plex Sans KR's whole cmap is the Korean layer, so `￦` and `㈜` come back —
  not because they are standard, but because the layer carries them.
- **Hanja seed** = 8,567 BMP ideographs of Source Han Sans KR 2.005, pinned for reproducibility.
  A seed, not a standard. JP draws 7,686 + 250 aliases, so the font claims **7,936**; 631 fall back
  and unsupported Hanja is simply Hanja 힣 does not type.
- **Seed and donor are separate files.** Seed is a codepoint list; donor coverage is a per-donor
  report. Swapping donors changes the report, never the seed.
- **Allowlist-first assembly**: fontTools subsets each donor and computes closure, then FontForge
  does geometry. The verifier fails closed on unknown rules and unexpected output. No blocklist of
  `jp78`/`hkna`/`ruby` — a donor bump extends it silently.
- **The gate decides the architecture.** Whichever assembly makes `missing == 0 && unexpected == 0`
  hold without fragile exceptions wins. JP-base vs KR-first is no longer a philosophical question.
- **Web is independent**: four faces, no Han, no Kana, browser fallback owns Han.

## Measured starting point (Regular)

```text
base layers (Mono 983 ∪ KR 12,183 ∪ Hack 1,548) = 13,563, zero Han
expected cmap under the contract                21,499  (base + 7,936 claimed Hanja)
current build                                    27,846

missing                                             413
  base-layer codepoints missing                     163   ← ￦ U+FFE6, ㈜ U+321C, enclosed Hangul,
                                                             unit symbols (㎧ ㎩ ㏊ …)
  compatibility aliases absent                      250   ← declared for v2, not yet created
unexpected                                        6,760
  undeclared non-Han                              1,424   ← Kana, radicals, JP enclosed/squared
  Han outside the claimed set                     5,336
```

Cause of the 163: `merge_kr_glyphs()` (`fontforge_script.py:361`) copies Plex Sans KR from four
ranges only (`AC00-D7A3`, `3131-318E`, `A960-A97F`, `D7B0-D7FF`) and discards the rest.

Also measured, and it shrinks the job: GPOS is already clean (only `mark`, four type-4 lookups) and
**no cmap 14 / UVS table exists** in donor or build. The surviving Japanese coupling is **GSUB only**
— 44 features, 73 lookups, 7 chained-contextual — plus 7,841 unencoded glyphs.

# Next concrete move

1. **Inventory extractor** — `work_scripts/font_inventory.py`, read-only, no repo mutation.
   Emits per font: cmap by block, glyph counts, unencoded count, GSUB/GPOS features and lookup-type
   histogram. Run it over Plex Mono / Plex Sans KR / Plex Sans JP / Hack / current GLG Regular+Bold.
   This is what turns the numbers above from a session memory into a regenerable artifact.
2. **Seed + provenance** — `work_scripts/gen_hanja_seed.py` → `source/hanja-seed.txt`
   (one codepoint per line) plus `provenance.json` (upstream URL, version, input SHA-256, output
   SHA-256, BMP-only scope). Record `unicodedata.unidata_version`, alias count and alias-map SHA-256
   with donor resolution. Offline for normal builds. Call it a **seed**, never a profile or standard.
3. **Expected-cmap builder + gate** — compose expected cmap from the layer/ownership rules, then
   emit `missing`, `unexpected` and the owner map against a built font. The gate must be able to
   fail: prove it by planting the current build against the new expected set and watching it report
   413 missing (163 base + 250 aliases) / 6,760 unexpected (1,424 non-Han + 5,336 Han).
4. **`/tmp` Regular proof of the allowlist-first assembly**, plus **one Bold face** (the hmtx
   incident hid in Regular-looks-clean/Bold-is-broken). Report cmap counts, TTF size, retained
   features, orphaned unencoded glyphs, width check, canary render.
5. **Emacs fontset output** — generate compressed ranges and the `'((#x.... . #x....) …)` form from
   the exact cmap. This is the deliverable 힣 actually uses; it is cheap once the exact list exists.
6. **Keep web moving separately** — four-face Han/Kana-free WOFF2, then verify `脈`/`如` render via
   fallback with no GLG `jp` request.

## Acceptance

- `missing == 0` and `unexpected == 0` against the declared layers, with an owner for every
  codepoint.
- `￦`, `㈜`, `㎡`, `㎏` render; `一日一生`, `無學論道`, `脈`, `如` render or fall back deliberately.
- JP contributes zero non-seed codepoints; no GSUB/GPOS feature outside the keep-allowlist survives.
- Zero *unreachable* unencoded glyphs (not zero unencoded — marks and components are legitimate).
- Latin/Hangul/coding-symbol geometry unchanged from v1; `task verify:widths` passes; Bold checked.
- No cmap 14 / UVS appears. Four legal records remain in nameID 0.
- The exact cmap, the range report and the Emacs fontset are all generated from one list.

## Stop conditions

- Do not justify the repertoire by any standard (KS X 1001, Adobe-KR, 교육용 한자). Ownership is the
  justification. Say **seed**, **owner**, **allowlist**.
- Do not delete or keep by Unicode block. `U+3300` holds both `㌀` and `㎏`.
- Do not write a blocklist of Japanese GSUB features; write the keep-allowlist.
- Do not treat "zero unencoded glyphs" as the goal; the goal is zero *unreachable* ones.
- Do not prove on Regular alone.
- Do not revive education lists, garden-trained profiles, frequency tiers or the 192-file prototype.

# RECENT

- [2026-07-14] North star replaced: standards framing dropped for **owned, observable cmap**. The
  design doc was renamed `V2_KOREAN_PROFILE.md` → `docs/V2_CMAP_CONTRACT.md` to match.
- [2026-07-14] Measured the real defect: the JP-base merge **drops 163 Korean codepoints** Plex Sans
  KR provides (`￦`, `㈜`, KS-era enclosed Hangul, unit symbols). Exact set arithmetic then corrected
  the current gate baseline to 413 missing and 6,760 unexpected; count subtraction had hidden the 250
  not-yet-created aliases. Every previous stop condition pointed only at removal and missed this.
- [2026-07-14] Measured that GPOS is already clean and no UVS table exists anywhere; the Japanese
  coupling is GSUB-only. The job is smaller than the last handoff assumed.
- [2026-07-13] `a6cf1a7` added chained-context semantics and fourteen mutation probes to the web
  verifier. Reuse its type-6 projection for the desktop gate.
- [2026-07-13] `ef67095`, `3dbf108`, `af273a3` repaired FontForge advance widths at all four TTF
  round-trips; `task verify:widths` remains mandatory.
