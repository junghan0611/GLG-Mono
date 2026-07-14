# GLG-Mono v2 — the cmap contract

Status: **contract fixed; implementation pending** (2026-07-14). Supersedes the "Korean standard
profile" framing, which was dropped: GLG-Mono represents no standard.

## What this font is

> GLG-Mono is a font for 힣's own working environment. It publishes its supported range as an exact
> Unicode cmap, traces every codepoint to an owner, and lets no undeclared character into the build.

The product is not "a complete East Asian font". Aiming there is what makes the code explode — fonts
arrive dirtier than expected, and every standard to satisfy adds another exception. The product is a
Unicode assembly 힣 can **see, own and extend**. Everything below serves three questions:

1. which codepoints does the font support right now,
2. which source does each glyph come from,
3. does anything unexpected arrive when a layer is added or removed.

Unsupported Hanja is not a defect. It is Hanja 힣 does not type — and if that changes, the seed is a
text file with one codepoint per line.

## Exact cmap is the SSOT

Emacs selects fonts by Unicode range, so the supported range *is* the product interface. But block
ranges must never be the source of truth, because **blocks are mixed**:

| Block | Contains |
|---|---|
| `U+3200-32FF` | Korean parenthesized/circled Hangul (`㈜`, `㉠`), Japanese enclosed forms, circled numbers |
| `U+3300-33FF` | Japanese squared Kana (`㌀`), **and the unit symbols Korean technical text lives on** (`㎏` `㎡` `㎞` `㎝` `㎥` `㏄`) |

Deleting `U+3300` as "Japanese enclosed forms" would destroy `㎏` and `㎡`. Therefore: **codepoint
allowlists only, never block rules.** Three artifacts, one truth:

```text
source of truth   exact codepoint list   U+0020, U+0021, …, U+321C, U+33A1, U+4E00, …
human report      compressed ranges      U+0020-U+007E, U+3131-U+318E, U+AC00-U+D7A3, …
Emacs output      fontset ranges         '((#x0020 . #x007e) (#x3131 . #x318e) …)
```

The range report and the Emacs fontset are **generated from** the exact list. They are outputs, not
inputs.

## Layers and ownership

The repertoire is the union of its layers. Ownership resolves a contested codepoint; higher wins:

```text
custom adjustments (source/AdjustedGlyphs)
> IBM Plex Mono        — Latin, coding symbols
> IBM Plex Sans KR     — Hangul and every Korean support character it carries
> IBM Plex Sans JP     — the Hanja seed, and nothing else
> Hack                 — supplementary glyphs
> Nerd Fonts           — NF variants only
```

This is not a claim that Plex Sans KR is authoritative. It is a decision: **힣 adopts Plex Sans KR's
character inventory as the Korean layer.** That is the whole justification, and it is enough. The
163 codepoints the current build drops are simply taken back — not because they are standard, but
because the Korean layer carries them.

The JP layer is admitted for **seed Hanja codepoints only**. This one rule dissolves the
classification problem: we never have to argue which character is "Japanese-only", because Kana,
Bopomofo, radicals, enclosed forms and Japanese GSUB have no path in. Nothing arrives to be excluded.

Measured baseline (Regular):

```text
IBM Plex Mono          983
IBM Plex Sans KR    12,183
Hack                 1,548
base union          13,563     (contains zero Han)
+ claimed Hanja      7,936
expected cmap       21,499
```

## The Hanja seed

The 8,567 BMP ideographs of **Source Han Sans KR 2.005** are the *GLG-Mono Hanja seed*. Not a
standard, not a canonical repertoire, not 국가표준 — a starting list, pinned so it is reproducible.

```text
seed                        8,567
drawn directly by JP        7,686
compatibility aliases         250
claimed by the font         7,936
fall back to another font     631
```

The font claims **7,936**, and the cmap says so exactly. The 84 supplementary-plane ideographs of
the Korean subset are outside the seed (BMP only).

The seed is generated from a pinned artifact, recorded with upstream URL, version, input SHA-256 and
output SHA-256. Normal builds are offline and never regenerate it. It is never derived from education
policy, hand curation or the garden corpus.

**Seed and donor are separate files.** `source/hanja-seed.txt` is a codepoint list that knows nothing
about donors. Which of those codepoints a given donor can actually draw belongs in a per-donor
resolution report, so swapping the donor changes the report, never the seed. Compatibility aliases
are derived from `unicodedata.decomposition()`, never hand-written; a compat ideograph with no
canonical decomposition cannot be aliased and is honestly reported as missing. Donor resolution
records `unicodedata.unidata_version`, the alias count and an alias-map SHA-256 so that the same
mapping—not merely the same seed—can be reproduced.

## The gate

Every build emits four sets and an owner map. This is the whole quality system:

```text
missing    = expected − actual     must be 0
unexpected = actual − expected     must be 0
```

```text
U+0061  PlexMono
U+321C  PlexSansKR
U+33A1  PlexSansKR
U+4E00  PlexSansJP:hanja
U+E0B0  NerdFonts        (NF variants only)
```

Plus:

- JP contributes **zero non-seed codepoints**;
- no GSUB/GPOS feature outside the keep-allowlist survives — an allowlist, never a blocklist of
  `jp78`/`hkna`/`ruby`, because a donor bump can extend a blocklist behind our back;
- **zero unreachable unencoded glyphs.** Not "zero unencoded": mark and composite components
  legitimately live unencoded. The honest criterion is that every unencoded glyph is reachable from
  a retained lookup or is a component of a retained composite;
- zero width-contract violations (`task verify:widths`);
- Regular vs Bold cmap differences: only the declared ones. The hmtx incident hid in exactly this
  gap — Regular looked clean while Bold was corrupt — so **every proof checks Bold too**;
- no cmap format 14 / UVS table appears. Neither donor nor build has one today; assert it stays
  that way rather than designing for it;
- four legal records remain in nameID 0. Rebuilding the repertoire does not erase provenance.

Where the current build stands against this contract (Regular, measured):

```text
expected cmap                    21,499
current cmap                     27,846
missing                             413
  base-layer codepoints missing     163   ← ￦ U+FFE6, ㈜ U+321C, enclosed Hangul, unit symbols
  compatibility aliases absent      250   ← declared for v2, not created by the current build
unexpected                        6,760
  undeclared non-Han              1,424   ← Kana, radicals, enclosed/squared JP forms
  Han outside the claimed set     5,336
```

## Assembly

Allowlist-first, not delete-afterwards. Subtractive deletion must *prove a negative* across 7,841
unencoded glyphs and 73 GSUB lookups; an allowlist lets fontTools compute the closure. The verifier,
not the subsetter, fails closed on unknown rules and unexpected output.

```text
1. fontTools  — subset each donor to its owned codepoints + keep-allowlist features
2. FontForge  — merge, widths, italic, geometry   (what it is actually good at)
3. fontTools  — hinting, tables, post-processing
4. gate       — expected/actual/missing/unexpected + owner map
```

The base font choice stops being a philosophical question. **Whichever assembly makes the gate pass
without fragile exceptions is the right one.** If the inherited JP-base pipeline gets there, keep it;
if it needs exceptions to get there, rebuild the assembly KR-first. The gate decides, not the argument.

The surviving Japanese coupling is smaller than feared: GPOS is already clean (only `mark`, four
type-4 lookups — `remove_lookups(remove_gpos=True)` killed the rest) and there is no UVS table
anywhere. **The coupling is GSUB-only** — 44 features, 73 lookups, 7 chained-contextual — plus the
unencoded mass, which the allowlist orphans anyway.

For chained-contextual (type 6) verification, reuse `webfont_verify.py`'s projection: a chain is its
`SubstLookupRecord`s, not its coverage. Delete the records and the contexts still match, they simply
substitute nothing — and coverage compares equal, so a coverage-keyed check cannot see the loss. Do
not write a second, weaker gate for the desktop.

## Web

The web contract is independent and already decided: four physical faces, no Han, no Kana, browser
fallback owns Han. See `WEBFONT_SUBSET.md`. It publishes an exact cmap too; only the content differs.

## Language discipline

Say **seed**, **owner**, **allowlist**. Never standard, canonical, or 국가표준 — GLG-Mono justifies
its repertoire by ownership, not by authority. Excluded ideographs are **outside the seed**, not
"Japanese-only".
