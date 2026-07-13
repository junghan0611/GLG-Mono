# NEXT — GLG-Mono

Boot sector for the next session. Durable facts live in `AGENTS.md`, not here.

# NOW — web font subsetting

- **Stem**: the garden (`notes.junghanacs.com`) ships 11 MB of GLG-Mono WOFF2; the home page
  alone pulls 5,280 KB (79% of page weight) because GLG Mono is the *body* font. Design is
  approved; nothing is built yet.
- **Current**: review finished 2026-07-13. **No font code touched.** Read
  **`docs/WEBFONT_SUBSET.md`** — it is the SSOT for the measurements, the decisions, and the
  gates. Do not re-derive them.
- **Next**: (1) add a web-font subset task to `Taskfile.yml` — emits chunks + `@font-face` CSS +
  manifest; (2) write the cmap-union verifier (source cmap == union of chunk cmaps, minus the
  declared PUA set); (3) run the style-aware p95 report and settle 32-vs-16 Han chunks.
- **Verify before shipping**: cmap union, licence gate (nameID 0/13/14 *content*), disjoint
  `unicode-range`, bearing/metric equality vs source, CI canaries. All specified in the design doc.
- **Blocker**: none.
- **Do not touch**: `fontforge_script.py`, `fonttools_script.py`, `build.ini`. This is a
  **web-deliverable-only** change. Desktop TTF/NF keeps full Han coverage. Do not "fix" the
  JP base font — this repo is a fork of PlemolJP (a *Japanese* font, upstream dormant since
  2025-06), so the Japanese base is inherited structure, not a bug. Restructuring the build around
  a Korean base is a rewrite of upstream, not a fix.

## Decisions already made — do not relitigate

- **Zero glyph loss.** Ship all 11,172 Hangul and all 13,412 Han, chunked. A corpus-based subset
  is **rejected**: the newest 20% of the garden introduce 191 codepoints the older 80% lack, so it
  would break every time GLG writes a note.
- **Italic ships physical CJK chunks** (option B). Latin is a true italic (different outlines);
  CJK is a 9° skew. Browser synthesis reproduces the slant but not the pixels, and GLG's bar is
  pixel parity.
- **PUA/Nerd excluded.** The font's 14 PUA glyphs are used 0× in the garden; the PUA the garden
  *does* use isn't in the font and already falls back. Recorded as a deliberate web-profile
  exclusion, not a silent exception.

## Traps — verified, will bite

- `pyftsubset` **drops nameID 0/13/14**. The copyright is not just IBM: Hack (Source Foundry,
  MIT + Bitstream Vera), Nerd Fonts, and PlemolJP are all in there, because `merge_hack()` runs in
  the core build regardless of `--skip-nerd`. Needs `--name-IDs='*' --name-legacy` plus shipped
  `OFL.txt` + `THIRD_PARTY_NOTICES.txt`.
- `notes/netlify.toml` gives `*.woff2` a **1-year immutable cache on fixed filenames**. Content-
  hashed names are mandatory or the swap never reaches existing visitors. (That file already
  records one stale-cache incident.)
- Subsetting does **not** damage the v1.0.0 Korean bearing fix or vertical metrics — verified.

# RECENT

- [2026-07-13] Repo brought onto the standard protocol: `CLAUDE.md` (452 lines) promoted to
  `AGENTS.md`; `CLAUDE.md` is now the one-line `@AGENTS.md` import. `NEXT.md` created.
- [2026-07-13] Web font review done end to end: the font carries the full PlemolJP Japanese base
  (Han 48% of the cmap) and there is no web pipeline, so the garden ships the whole thing.
  Cross-checked with the garden steward, design reviewed and approved by GPT. Projected: home
  5,280 KB → ~175 KB, zero glyph loss.
- v1.0.0 has no public GitHub release yet. Unrelated to this work, and not scheduled.
