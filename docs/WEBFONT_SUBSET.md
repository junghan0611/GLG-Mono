# Web Font Subsetting — Design

Status: **design approved, not implemented** (2026-07-13)
Reviewers: garden steward (`notes`), GPT (codex/gpt-5.6-sol)

The web deliverable is the only thing this document changes. Desktop TTF/NF releases
keep their full coverage, including Han. Nothing in `fontforge_script.py` or
`fonttools_script.py` needs to change.

## Problem

`notes/quartz/static/fonts/` ships four full WOFF2 faces, 11 MB total. The home page pulls
Regular + Bold = 5,280 KB — 79% of total page weight. Because `quartz.config.ts` sets GLG Mono
for `header`/`title`/`body`/`code`, this is a **body font**: every glyph waits on it, then
reflows. Lighthouse: Performance 67, CLS 0.207, Speed Index 9.3 s.

## Why the font is this large

**The font is a PlemolJP fork, and PlemolJP is a Japanese font.** `fontforge_script.py:214` opens
`jp_font` (IBM Plex Sans JP) and merges Korean onto it (`merge_kr_glyphs`, `:355`). The Japanese
base is inherited build structure, not a mistake — upstream (<https://github.com/yuru7/PlemolJP>,
dormant since 2025-06) is built that way, and the desktop font legitimately carries Han.

Regular's cmap: 27,846 codepoints — Han 13,412 (48.1%), Hangul 11,172 (40.1%), Kana 189, rest ~3,000.

So roughly half the font is Japanese Han that a Korean garden almost never renders (739 distinct
Han glyphs across 263 of 2,245 documents). That is fine on disk. It is not fine over the wire.

**The actual fault: there is no web font pipeline.** No `woff2` task in `Taskfile.yml`; `README.md`
documents a manual `woff2_compress` (lossless Brotli). The desktop font — Han, Kana and all — was
compressed whole and uploaded. Nobody decided to serve 13,412 Han glyphs to the web; nobody decided
not to, either.

The fix therefore belongs entirely to the **web deliverable**. The source build stays as it is.

## Measurements

Corpus: 2,245 garden `.md` files, 3,665 distinct codepoints in use.

Cut from the shipped `GLG-Mono-Regular.woff2` (2,644 KB) with `pyftsubset`, hinting kept:

| Cut | Size |
|---|---|
| Latin core (+ punctuation, currency) | 28 KB |
| Symbols (arrows, math, shapes) | 32 KB |
| Box drawing | 8 KB |
| Fullwidth + CJK punctuation | 64 KB |
| Hangul, all 11,172 | 368 KB |
| Han, all 13,412 | 1,784 KB |
| Kana | 88 KB |
| Drop Han + Kana only, keep every Hangul | **480 KB (−82%)** |

Per-document simulation over the corpus — `unicode-range` loads a chunk if the page uses **any**
codepoint in it, so chunk count is a real tradeoff:

| Hangul chunks | Avg load / doc | | Han chunks | Avg load / Han doc | Avg / all docs |
|---|---|---|---|---|---|
| 1 | 368 KB | | 1 | 1,784 KB | 209 KB |
| 4 | 101 KB | | 8 | 234 KB | 27 KB |
| **8** | **65 KB** | | 16 | 123 KB | 14 KB |
| 16 | 72 KB | | **32** | **67 KB** | **7.9 KB** |
| 32 | 114 KB | | | | |

Hangul reverses at 16 — each chunk re-pays duplicated font tables and its own WOFF2 compression
context (~12 KB; this is **not** HTTP header overhead). Han is sparse (only 263 of 2,245 docs use
Han, 739 distinct glyphs), so it keeps improving as it splits.

## Why a corpus subset is rejected

The garden steward proposed subsetting to the 3,665 codepoints actually in use (267 KB). That
**breaks as the garden grows**. Sorting documents by commit time and subsetting on the oldest 80%
(1,796 docs), the newest 20% introduce **191 codepoints that subset lacks** — 49 of them Hangul.
Those would have rendered in a fallback font.

So: ship every Hangul and every Han, chunked. Nothing is dropped; unused chunks are never
requested. Loss is zero by construction, not by corpus luck.

## Italic — the largest single lever

`fontforge_script.py:131` builds Italic with `jp_style="Regular", eng_style="Italic"`. So:

- **Latin is a true italic** — IBM Plex Mono's own italic design. Verified: 'a' has 49 points in
  Regular, 48 in Italic. A different glyph.
- **CJK is oblique** — `transform_italic_glyphs` (`:699`) applies `skew(9°) + translate(-40, 0)`,
  advance preserved. Verified: '가' keeps all 22 points; only the slant differs.

Garden italic usage: 1,087 emphasis spans — Hangul in 523 (48%), Han in 2 (0.2%), Kana in 0.

**Decision: ship physical italic chunks for all CJK (option B).** Browser `font-synthesis` would
reproduce the slant but not the pixels — the font does exactly `9° + (-40)` with advance held,
while synthesis angle/origin/overhang is engine-defined. GLG's bar is pixel parity, so synthesis
is out. Applying synthesis only to rare codepoints (Han's 2 uses) was considered and rejected: it
smuggles back the mechanism we just declined, for a rounding error of traffic. Chunks cost network
nothing when unused; they cost only distribution size.

Policy, stated once: **web coverage == source coverage − the explicitly excluded PUA set.**

## PUA / Nerd — excluded, with evidence

The font carries 14 PUA glyphs (Powerline `E0A0`–`E0B3`, plus IBM Plex private `F6D7`/`F860`…).
The garden uses **none** of them. The PUA it does use — `U+E718` (24×), `U+F17A` (3×), `U+E135`
(1×) — is **absent from the font** and already falls back today. Excluding PUA changes zero pixels.

This is a deliberate web-profile exclusion recorded in the manifest, not a hidden exception to
"zero loss".

## Traps found (verified, not theoretical)

**1. `pyftsubset` drops the licence.** Source `name` table has IDs `[0,1,2,3,4,5,6,13,14,256–262]`;
after subsetting only `[1–6]` survive. Dropped: nameID 0 (copyright), 13 (licence text), 14
(licence URL).

And the copyright is **not just IBM** — nameID 0 carries four:

```
[IBM Plex]   Copyright (c) 2017 IBM Corp.
[Hack]       Copyright 2018 Source Foundry Authors
[Nerd Fonts] Copyright (c) 2014, Ryan L McIntyre
[PlemolJP]   Copyright (c) 2021, Yuko Otawara
```

`merge_hack()` (`:912`) runs in the **core build**, independent of `--skip-nerd`, so Hack glyphs
(MIT + Bitstream Vera terms) are in every face. Dropping Nerd PUA does not erase Hack provenance.

Required: `--name-IDs='*' --name-legacy --name-languages='*'`, plus shipped `OFL.txt` and
`THIRD_PARTY_NOTICES.txt`. Gate on the *content* (IBM copyright, OFL 1.1, URL present), not merely
on ID presence. OFL 1.1 §2 permits stand-alone text instead of binary metadata — but removing
metadata that was already there is not defensible either way.

**2. Immutable cache pins the font for a year.** `notes/netlify.toml` gives `*.woff2`
`max-age=31536000, immutable` while filenames are fixed (`GLG-Mono-Regular.woff2`). Replacing the
font would not reach existing visitors. That file's own comments already record one stale-cache
incident. **Content-hashed filenames are mandatory.**

**3. Subsetting does *not* break what this repo fixed.** Verified on the Hangul chunk: '가'
(U+AC00) keeps `advance=1056, lsb=116, bbox=(116,-101,940,767)` — identical to source. Vertical
metrics identical across all chunks (`upem=1000`, `hhea=950/-225/0`, `winAsc/Desc=950/225`,
`xAvgCharWidth=528`, `isFixedPitch=1`). `GSUB`/`GPOS`/`GDEF` retained. The v1.0.0 Korean bearing
work survives, because subsetting *selects* glyphs, it does not transform them.

**4. Split faces can split shaping runs.** Precomposed Hangul and Han are safe, but Jamo sequences,
combining marks, variation selectors, and Latin ligature/kern pairs must stay inside one logical
chunk. Binary glyph equality does not by itself prove composite-face render equality.

## Result

| | Now | After |
|---|---|---|
| Home page (R+B) | 5,280 KB | ~175 KB |
| Typical note | 5,280 KB | ~215 KB |
| Distribution total | 11 MB | ~10 MB, ~180 files |

Distribution size barely moves; **what the browser fetches** drops ~30×. Netlify serves 180 static
files without complaint, and file count is not request count — the CSS only matches what the page
needs.

## Acceptance gates

Not "average bytes". Style-aware simulation over the real corpus, per `font-style × font-weight`,
reporting p50/p75/p95/p99/max bytes **and request count**:

- home, cold: ≤ 220 KB, ≤ 8 font requests
- non-Han p95: ≤ 300 KB, ≤ 12 requests
- Han-doc p95: ≤ 500 KB, ≤ 16 requests
- Han-doc p99: ≤ 750 KB, ≤ 24 requests
- corpus max: ≤ 1.5 MB, ≤ 40 requests (glyph-catalog pages flagged separately)

**32 Han chunks stay a candidate, not a decision.** Adopt only if, against 16: Han-doc p95 bytes
improve ≥15%, p95 request growth ≤ +4, and mobile-throttled p95 LCP does not regress >50 ms on a
deploy preview. Otherwise fall back to 16. Do not wave "HTTP/2" at request growth — read the
waterfall.

Correctness gates:

- **cmap union**: source cmap == union of all chunk cmaps, per face, minus the declared PUA set.
  Cover Kana, Jamo, compat Jamo, compatibility ideographs, fullwidth forms, variation selectors.
- chunk `unicode-range`s are disjoint; each subset's real cmap ⊇ its declared range.
- licence gate (see trap 1).
- outline/advance/LSB/bbox/vertical-metric equality against the source face, sampled.
- canaries: one glyph from each Han chunk (shotgun), the most-Han doc, the worst-Han doc, an
  R/B/I/BI mixed run, and a Jamo+combining/UVS run — screenshot + expected request set, in CI.

CLS is a **separate axis**. Chunking cuts latency; it does not stop reflow. `font-display: swap`
still shifts on a late swap. Match the fallback with `size-adjust` / `ascent-override` /
`descent-override` / `line-gap-override`. Final Lighthouse gate: CLS < 0.1 (target < 0.05),
LCP < 2.5 s. Preload only the exact hashed files the first screen truly uses — preloading
`unicode-range` chunks defeats the point.

## Build & distribution shape

- Deterministic web build in **this** repo, emitting chunks + `@font-face` CSS + a manifest
  (source sha256, fontTools version, chunk ranges, output sha256/size, licence status).
- The release artifact is canonical. `notes` vendors one release's output; it does not generate
  fonts at deploy time.
- Content-hashed filenames; delete stale chunks in the same commit.
- Keep hinting. Keep `--layout-features='*'`.
- Variable fonts are not the better axis here: the sources are static masters and the garden uses
  two weights.
