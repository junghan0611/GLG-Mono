# GLG-Mono v2 — Korean-first product architecture

Status: **north star approved; Regular proof pending** (2026-07-14).

## Product definition

GLG-Mono is a Korean programming and knowledge-work font. Its shipped repertoire is deliberate:

1. **Hangul** — IBM Plex Sans KR: all modern syllables and the supported Jamo repertoire.
2. **Latin** — IBM Plex Mono: the real roman/italic programming face.
3. **Hanja** — a pinned Korean standard profile, rendered by an explicitly named outline donor.
4. **Coding symbols** — IBM Plex Mono, Hack, custom adjusted glyphs, and optional Nerd Fonts.
5. **Korean punctuation and fullwidth forms** required by the product.

Japanese syllabaries, Bopomofo, Japanese-only enclosed forms and regional OpenType features are not
product goals. PlemolJP remains project heritage and legal provenance; it does not define the v2
repertoire.

## Repertoire and donor are separate

- **Repertoire** answers which Unicode codepoints GLG-Mono owns.
- **Donor** answers whose outlines draw those codepoints.

Changing a donor must not silently expand the repertoire. Changing the repertoire requires an
explicit contract decision regardless of what a donor font happens to contain.

### v2 Hanja profile

The first profile is the **BMP ideograph cmap of Source Han Sans KR 2.005**:

| Range | Codepoints |
|---|---:|
| CJK Unified Ideographs Extension A | 93 |
| CJK Unified Ideographs | 8,139 |
| CJK Compatibility Ideographs | 335 |
| **Total** | **8,567** |

The Korean subset also maps 84 supplementary-plane ideographs (69 Extension B–F and 15
Compatibility Supplement). v2-A deliberately delegates those 84 to fallback. This is therefore the
**BMP Korean profile**, not the complete Adobe-KR repertoire.

The profile is generated from a pinned upstream artifact, sorted deterministically, and committed
with upstream URL, version, input SHA-256 and output SHA-256. The normal build never downloads it.
A maintenance regeneration command verifies the pinned input before replacing the generated file.
The profile is never derived from education policy, garden frequency or a hand-curated list.

### v2-A outline donor

The first donor is the IBM Plex Sans JP already vendored in `source/`:

```text
BMP Korean profile                         8,567 mappings
JP direct coverage                         7,686
CJK compatibility aliases                    250
renderable by the v2-A donor               7,936 (92.6%)
outside donor coverage                       631 → fallback
```

JP regional forms on unified codepoints are an accepted **v2-A tradeoff**, not a claim that regional
forms are irrelevant. The proof must show the actual forms and record the decision. A future
TC-first or other donor may improve forms or coverage, but it requires new provenance, geometry
goldens and visual proof. IBM Plex Sans TC is a Taiwan-oriented amalgam, not a guaranteed Korean
font.

## Staged build architecture

### v2-A — prove the Korean output contract cheaply

Use the inherited JP-base assembly only as a low-risk implementation vehicle:

1. retain only donor Han that belongs to the BMP Korean profile;
2. create canonical compatibility aliases without duplicate outlines;
3. remove Kana, Bopomofo, Japanese-only repertoire and Japanese regional GSUB features;
4. replace Japanese width sentinels such as U+3042 with explicit Korean/product metrics;
5. preserve Latin, Hangul and coding-symbol geometry from v1.

The shipped output—not the name of an internal variable—must satisfy the Korean product contract.

### v2-B — neutral/KR-first assembly gate

If v2-A cannot remove JP-specific cmap, unencoded components, layout lookups or metric assumptions
without fragile exceptions, stop productization and rebuild the assembly as:

```text
IBM Plex Sans KR base
+ IBM Plex Mono Latin
+ generated-profile Hanja donor
+ Hack/custom symbols
+ optional Nerd Fonts
```

v2-A is a proof and migration step, not permission to preserve accidental Japanese coupling forever.

## Web contract is independent

Web delivery optimizes transfer rather than mirroring desktop coverage:

- four physical GLG faces: Regular, Bold, Italic and BoldItalic;
- Han is absent from GLG WOFF2 cmap and CSS claims and is rendered by a CJK fallback;
- Japanese syllabaries are not shipped;
- ordinary Korean pages request only Regular and Bold;
- no corpus-trained or frequency-ordered Han chunks.

The uncommitted notes integration remains the browser acceptance harness. It does not define the
font repertoire.

## Verification contract

A v2 build is acceptable only when:

- the generated profile exactly matches its pinned provenance and declared BMP scope;
- encoded and unencoded glyph inventories contain no undeclared Japanese repertoire;
- Japanese-only GSUB features (`jp78`, `jp83`, `jp90`, `hkna`, `vkna`, `ruby`, and related rules)
  are absent unless a surviving rule is explicitly justified;
- compatibility aliases, cmap formats 12/14 and variation data have no dangling references;
- all retained Hanja are fullwidth and survive every FontForge round-trip;
- Latin, Hangul and coding symbols retain v1 geometry and shaping goldens;
- physical Italic/BoldItalic, Console/35 variants, legal name records and deterministic outputs
  remain guarded;
- browser canaries `脈`, `如`, `一日一生`, `無學論道` display without tofu while GLG web faces do
  not fetch a Han payload.

## Language discipline

Use **outside the selected Korean profile**, not “Japanese-only Han,” for excluded ideographs. IBM
Plex Sans KR currently contains zero Han; IBM stated in 2020 that there were no plans to add Hanja
then, not that it would never do so. Donor coverage and regional-form correctness are separate
claims and must be measured separately.
