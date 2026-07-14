# AGENTS.md

Project context for AI agents.

## Agent workspace

- **`AGENTS.md`** (this file) — durable, shared baseline for any agent (Claude, GPT, Gemini) working on this repo. Edit when a rule or convention stabilizes. Durable facts live here.
- **`NEXT.md`** — disposable session handoff: the next concrete move, its verification, and blockers. A boot sector, not a knowledge base. Read it at session start; when a NEXT item turns into a stable fact, graduate it into `AGENTS.md` and drop it from NEXT. Branch work uses `NEXT--<branch>.md`, deleted before merging to `main`.
- **`CHANGELOG.md`** — closed work promoted from NEXT by the `tag-release` loop.
- **`CLAUDE.md`** — one line, `@AGENTS.md`. Do not put content there.
- **`ROADMAP.md`** — manual long-horizon rebuild phases; NEXT remains the concrete boot sector.

Keep the document surface small: README for people, AGENTS for durable truth, ROADMAP for direction,
NEXT for active work, and CHANGELOG for closed snapshots. Do not recreate a `docs/` tree.

## Project Overview

**GLG-Mono** (힣's Monospace Font) is 힣's own Korean programming font. It combines Hangul, Latin,
coding symbols and a pinned Hanja seed; inherited pan-CJK coverage is not a product goal and is
being removed. It represents no standard — see the north star below.

**Repository**: junghan0611/GLG-Mono
**Version**: v1.0.0
**License**: SIL Open Font License 1.1 (fonts), MIT License (build scripts)

### Name Origin

- **힣 (U+D7A3)**: Last syllable in Korean Unicode, meaning "letting go of ego"
- **GLG**: "힣" typed on QWERTY keyboard, meaning "giggling" - coding with a smile
- **Philosophy**: own and observe the glyphs in the font; completeness is not the goal.

### Project Heritage

```
IBM Plex (2017, IBM)
  ├─ IBM Plex Mono (English monospace)
  ├─ IBM Plex Sans JP (Japanese)
  └─ IBM Plex Sans KR (Korean)
    ↓
PlemolJP (2021, Yuko OTAWARA)
  - Japanese programming font
    ↓
PlemolKR (2024, soomtong)
  - Korean programming font
    ↓
GLG-Mono (2025, junghan0611)
  - 힣's own working font: an owned, observable Unicode assembly
  - Layers: Latin/coding (Plex Mono) + Korean (Plex Sans KR) + Hanja seed + symbols
```

**Upstream**: <https://github.com/yuru7/PlemolJP> — a *Japanese* programming font. This repo is a
fork of it, which is why IBM Plex Sans JP is present and why the v1 build is structured around it.
Upstream has had no updates since 2025-06; we do not track it.

### v2 North Star — an owned, observable Unicode assembly

> GLG-Mono is a font for 힣's own working environment. It publishes its supported range as an
> exact Unicode cmap, traces every codepoint to an owner, and lets no undeclared character into
> the build.

GLG-Mono represents no standard and claims no canonical Hanja repertoire. Chasing "a complete CJK
font" is what makes this codebase explode; being able to *see and own* what is inside it is the
product. Three questions replace every standards argument:

1. which codepoints does the font support right now,
2. which source does each glyph come from,
3. does anything unexpected arrive when a layer is added or removed.

**Exact cmap is the SSOT.** Block ranges and the Emacs fontset form are *generated outputs* of it,
never the source of truth. Unicode blocks lie: U+3200 and U+3300 each mix Korean letters, Japanese
forms and unit symbols in one block, so no block-level rule is safe. Only codepoint-level
allowlists are.

**Layer ownership** (higher wins a contested codepoint):

```text
custom adjustments (AdjustedGlyphs)
> IBM Plex Mono        — Latin, coding symbols
> IBM Plex Sans KR     — Hangul and every Korean support character it carries
> IBM Plex Sans JP     — the selected Hanja seed, and nothing else
> Hack                 — supplementary glyphs
> Nerd Fonts           — NF variants only
```

The JP layer is admitted for Hanja codepoints only. That single rule dissolves the classification
problem: we never have to argue which character is "Japanese-only", because Kana, radicals,
enclosed forms and Japanese GSUB have no path in.

**Hanja seed** — the 8,567 BMP ideographs of Source Han Sans KR 2.005 are the **GLG-Mono Hanja
seed**, not a standard and not canonical. The JP donor draws 7,686 directly and 250 through
compatibility aliases, so the font claims **7,936**; the remaining 631 fall back to another font,
and unsupported Hanja is simply Hanja 힣 does not type. Seed membership is generated from a pinned
artifact — never from education policy, hand curation or the garden corpus.

**The gate that keeps the font clean** — every build emits four sets and an owner map:

```text
missing    = expected − actual   must be 0
unexpected = actual − expected   must be 0
```

Measured today (Regular): base layers hold 13,563 codepoints with zero Han, yet the shipped font has
27,846. It **drops 163 codepoints Plex Sans KR provides** (including `￦` U+FFE6 and `㈜` U+321C,
because `merge_kr_glyphs()` copies only four Hangul ranges). Against the exact 21,499-codepoint
contract, the current face has 413 missing (those 163 plus 250 aliases not yet created) and 6,760
unexpected (1,424 non-Han plus 5,336 Han outside the claimed set).

The set equality is necessary but not sufficient. Every proof also requires:

- exactly one owner for every expected codepoint, and zero JP-owned non-seed mappings;
- a layout **keep-allowlist**; unknown lookup types and unexpected output fail closed in the
  verifier, not by trusting the subsetter;
- zero *unreachable* unencoded glyphs. Unencoded mark and composite components are legitimate when
  reachable from retained cmap, composites, or layout;
- Regular and Bold checks together, because source faces and Hack marks differ by weight;
- fullwidth retained Hanja/Hangul, halfwidth Latin, zero-width marks, and `task verify:widths`;
- no cmap format 14/UVS table unless a future contract explicitly introduces one;
- preserved physical Italic/BoldItalic faces and the four legal nameID 0 records.

### Language discipline

Say **seed**, **owner**, **allowlist**. Do not say standard, canonical, or 국가표준 — GLG-Mono
justifies its repertoire by ownership, not by authority. Excluded ideographs are **outside the
seed**, not "Japanese-only".

## Development Environment

### NixOS Setup (Required)

**All build commands must run inside the flake dev shell:**

```bash
# Enter development environment
nix develop

# Or run a single command
nix develop --command task quick
```

`flake.nix` pins **nixos-26.05**, the same channel and revision as the host system
(`flake.lock` reuses the system's nixpkgs rev, so entering the shell needs no download).
nixpkgs is the only input; there is no `shell.nix`, and nothing pins a specific Python
minor version — the generic `python3` / `python3Packages` set keeps interpreter and
modules coherent.

Provided: `fontforge` (with Python bindings), `python3`, `fontTools`, `brotli`,
`ttfautohint` (CLI + Python), `go-task`, `fontconfig`. `work_scripts/env_report.py`
prints the resolved versions on shell entry.

`brotli` is not optional: without it `fontTools` raises `ImportError` the moment a
WOFF2 is saved, and the web font build cannot run at all.

### Toolchain traps on 26.05

Two failures surfaced when moving off the 25.05 pin. Both are fixed; do not reintroduce.

- **`ttfautohint-py` >= 0.6 shells out to the CLI**, which rejects `--epoch` (a
  libttfautohint-only option). `options.parse_args()` returns a **dict**, so the old
  `hasattr`/`delattr` guard was a silent no-op. `fonttools_script.py` now pops the key.
- **FontForge 20251009 over-compresses `hmtx`.** It reads a monospaced face as
  compressible and writes `numberOfHMetrics=4`; every glyph past index 4 then inherits a
  half-width advance, destroying zero-width glyphs (combining accents, soft hyphen,
  ZWSP, line separators, unencoded mark components). Outlines, glyph names and cmap all
  survive intact, so only an advance-width check catches it, and roughly half the
  casualties are unreachable from cmap. There is no `generate()` flag to disable it.

  **Every FontForge → TTF round-trip must snapshot widths and write them back** via
  `font_widths.py`. There are four:

  | Where | Why it round-trips |
  |---|---|
  | `fontforge_script.py` final `generate()` | writes the eng and jp faces |
  | `fontforge_script.py` `merge_hack()` | Hack goes out to a temp TTF, then `mergeFonts()` |
  | `fontforge_script.py` alt_uni handler | generate + reopen to fix up `select()` |
  | `fix_nf_korean_bearing.py` | rewrites the Nerd Fonts face after patching |

  `merge_hack()` is the subtle one. Hack-Regular has no U+0305 or U+030D-U+0361 while
  Hack-Bold ships them at advance 0, so only Bold and BoldItalic pulled those marks
  through the Hack path — the corruption hit two faces out of sixteen and left Regular
  looking clean.

  `task verify:widths` (`test_advance_widths.py`) is the guard. It states the contract
  over glyph *names*, not codepoints, and applies no Unicode-category filter, because
  both would walk past the unencoded casualties.

## Font Families

| Family | Width Ratio | Description |
|--------|-------------|-------------|
| **GLG-Mono** | 1:2 | Standard version |
| **GLG-MonoConsole** | 1:2 | Console-optimized (recommended for release) |
| **GLG-Mono35** | 3:5 | Wide English characters |
| **GLG-Mono35Console** | 3:5 | Wide + Console mode |

### Variants

- **NF** suffix: Nerd Fonts included (e.g., GLG-MonoConsoleNF)
- **HS** suffix: Hidden full-width Space

Each family: 16 fonts (8 weights × 2 styles)

### Release Policy

**Official releases include Console variants only:**
- GLG-MonoConsole (1:2 ratio)
- GLG-Mono35Console (3:5 ratio) - optional

## Build System

### Multi-Stage Build Process

1. **Stage 1: FontForge** (`fontforge_script.py`)
   - Font merging and glyph manipulation
   - Width transformations
   - Italic generation (9° skew)
   - Optional Nerd Fonts integration (internal method)

2. **Stage 2: FontTools** (`fonttools_script.py`)
   - ttfautohint application
   - Font table modifications
   - Final post-processing

3. **Stage 3: Nerd Fonts Patching** (Optional, via FontPatcher)
   - External Nerd Fonts patching with FontPatcher
   - Post-processing: Korean glyph bearing fix (`fix_nf_korean_bearing.py`)
   - Ensures Korean glyphs remain centered after merge

### Quick Start

```bash
# Enter the dev shell
nix develop

# Quick test build (Regular weight only)
task quick

# Build Console variants (recommended)
./build_with_taskfile.sh

# Full build with all variants
./build_with_taskfile.sh --with-35

# Build without Nerd Fonts (faster)
./build_with_taskfile.sh --skip-nerd
```

### Common Tasks

```bash
# Inside nix develop
task                    # Show all tasks
task quick              # Fast build (Regular only)
task build:console      # Build GLG-MonoConsole
task build:console35    # Build GLG-Mono35Console
task polish             # Post-process fonts
task check              # Verify generated fonts
task verify             # Check Korean/Japanese glyphs
task clean              # Clean build directory

# Complete workflows
task full               # Build + polish: default + 3:5
task full:nerd          # Build + polish: Nerd Fonts

# Nerd Fonts patching (using FontPatcher)
task patch:nerd         # Patch GLG-Mono → GLG-MonoNF (auto post-processing)
task patch:nerd:wide    # Patch GLG-Mono35Console → GLG-Mono35ConsoleNF
task patch:nerd:all     # Patch all Console variants

# Verification
task verify:nerd        # Verify Nerd Fonts icons
task verify:bearing     # Verify Korean glyph bearing (NF vs non-NF)
task verify:widths      # Verify combining marks keep advance 0 (hmtx regression guard)
```

### Build Options

**Width Ratios:**
- Default (1:2): Half-width = 1/2 of full-width (528:1056)
- `--35` (3:5): Half-width = 3/5 of full-width (600:1000)

**Console Mode:**
- Prioritizes IBM Plex Mono glyphs
- Converts East Asian Ambiguous Width to half-width
- Better terminal alignment

**Nerd Fonts:**
- Powerline symbols (U+E0B0-E0D7)
- Devicons and programming symbols
- Half-width adjusted

## Directory Structure

```
/source              - Source fonts and custom glyphs
  /IBM-Plex-Mono     - English monospace
  /IBM-Plex-Sans-KR  - Korean font
  /IBM-Plex-Sans-JP  - Japanese font — the BASE font, inherited from PlemolJP (see Font Composition)
  /hack              - Supplementary glyphs
  /nerd-fonts        - Optional Nerd Fonts
  /AdjustedGlyphs    - Custom glyph modifications (.sfd)

/build               - Output directory (gitignored)

/hinting_post_process - ttfautohint control files
  normal-{Weight}-ctrl.txt  - For 1:2 ratio
  35-{Weight}-ctrl.txt      - For 3:5 ratio

/work_scripts        - Utility scripts (env_report.py, check_glyph_number.py)

/old_script          - Inherited PlemolJP shell scripts; unreferenced, kept as history

build.ini            - Build configuration
fontforge_script.py  - Stage 1: Font merging
fonttools_script.py  - Stage 2: Post-processing
fix_nf_korean_bearing.py - Stage 3: NF post-processing
font_widths.py       - Advance-width repair for every FontForge TTF round-trip
webfont_subset.py    - Web: build the WOFF2 tiers
webfont_verify.py    - Web: the eight gates (reuse its type-6 chained-context projection)
test_webfont_gates.py - Web: plants 14 defects and demands each gate bites
test_korean_bearing_nf.py - Korean bearing verification
test_advance_widths.py - Zero-advance guard (hmtx regression)
verify_korean_complete.py - Complete Korean glyph validator
Taskfile.yml         - Build automation
build_console_all.sh - Console build entry point (Taskfile's web:build error path points here)
flake.nix            - NixOS development environment (nixos-26.05 pin)
flake.lock           - Locked nixpkgs revision (matches the host system)
build_with_taskfile.sh - Main build script
```

## Configuration (build.ini)

```ini
VERSION = v1.0.0
FONT_NAME = PlemolJP      # Legacy internal name (DO NOT CHANGE)
NEW_FONT_NAME = GLG-Mono  # Output font name

# Font metrics (EM = 1000)
EM_ASCENT = 880
EM_DESCENT = 120
OS2_ASCENT = 950
OS2_DESCENT = 225

# Width ratios
HALF_WIDTH_12 = 528   # 1:2 ratio
FULL_WIDTH_35 = 1000  # 3:5 ratio

ITALIC_ANGLE = 9
```

**Important:** Keep `FONT_NAME = PlemolJP` for internal compatibility. Use `NEW_FONT_NAME` for output files.

## Development Workflow

### Making Changes

1. **Modify configuration**: Edit `build.ini`
2. **Adjust glyphs**: Modify .sfd files in `/source/AdjustedGlyphs/`
3. **Change build logic**: Edit `fontforge_script.py` or `fonttools_script.py`
4. **Update hinting**: Modify control files in `/hinting_post_process/`

### Testing Workflow

```bash
# Quick iteration (inside nix develop)
task quick              # Build Regular weight
task check              # Verify output
task verify             # Check Korean/Japanese glyphs

# Test specific variant
python fontforge_script.py --debug --console
python fonttools_script.py Console
ls -lh build/GLG-MonoConsole-Regular.ttf
```

### Debug Flags

- `--debug`: Build Regular weight only (fastest)
- `--minimal`: Build Regular + Bold
- `--do-not-delete-build-dir`: Preserve existing builds

## Git Workflow

### Commit Guidelines

- **Professional commit messages**: No "Generated with Claude" or "Co-Authored-By"
- **Follow existing style**: Check `git log` for patterns
- **Meaningful descriptions**: Explain what and why

### Working with Changes

```bash
# Check status
git status

# Stage and commit
git add <files>
git commit -m "Brief description

Detailed explanation if needed"

# Push to GitHub
git push origin main
```

## Technical Details

### Font Composition and Provenance

**Current v1 fact:** `fontforge_script.py:214` opens IBM Plex Sans JP as `jp_font` and merges Korean
onto it, which is why the shipped face carries **13,022 Han and 263 Kana**. The inherited assembly
is subtractive — it inherits everything JP has and then removes — and that is exactly what the v2
contract inverts. It is not the product contract.

- **The JP-base merge does not merely carry Japanese baggage; it drops Korean.**
  `merge_kr_glyphs()` (`:361`) copies Plex Sans KR from four ranges only — `AC00-D7A3`,
  `3131-318E`, `A960-A97F`, `D7B0-D7FF` — so every other Korean character KR provides is discarded:
  163 codepoints, including `￦` (U+FFE6) and `㈜` (U+321C). Any gate that only asks "did Japanese
  leave?" misses this; the cmap diff gate asks both directions.
- Assembly must become **allowlist-first**: subset each donor to its owned codepoints with
  fontTools (which computes layout closure), then let FontForge do geometry. The verifier—not the
  subsetter—fails closed on unknown rules and unexpected output. A blocklist of Japanese features
  (`jp78`, `hkna`, `ruby`, …) is the fragile exception we refuse —
  a donor version bump can extend it behind our back.
- The base font choice stops being philosophy and becomes an implementation detail: whichever
  assembly makes `missing == 0 && unexpected == 0` hold without fragile exceptions is the right one.
- Italic builds currently use `jp_style="Regular", eng_style="Italic"` (`:131`). Latin is IBM Plex
  Mono's **true italic**; retained CJK is algorithmic `skew(9°) + translate(-40, 0)` oblique. v2
  must preserve the physical Italic/BoldItalic faces while removing Japanese width sentinels.
- `merge_hack()` runs in the **core build**, independent of `--skip-nerd`; Hack glyphs are in every
  face.
- Measured: GPOS is already clean (`remove_lookups(remove_gpos=True)` at `:263` leaves only `mark`,
  four type-4 lookups), and **neither donor nor build has a cmap format 14 / UVS table**. The
  surviving Japanese coupling is **GSUB only** — 44 features, 73 lookups, 7 chained-contextual —
  plus 7,841 unencoded glyphs. Assert UVS stays absent; do not spend design on it.

**Four copyrights live in nameID 0** — IBM Plex, Hack (Source Foundry; MIT + Bitstream Vera),
Nerd Fonts (Ryan L McIntyre), PlemolJP (Yuko Otawara). Refactoring repertoire does not erase legal
provenance. `pyftsubset` silently drops nameID 0/13/14 unless given `--name-IDs='*' --name-legacy`.

### Web Fonts

Desktop and web have different coverage contracts. Desktop v2 carries the Hanja seed its donor can
render; web WOFF2 intentionally carries **no Han and no Japanese syllabaries**. A system or remote
CJK fallback owns Han on the web, where readable non-tofu output—not parity with the desktop
donor—is the acceptance bar. Both contracts publish an exact cmap; only their content differs.

The final topology is four physical faces: Regular, Bold, Italic and BoldItalic. Ordinary Korean
pages request only Regular and Bold. The verified 8-file `{core,jp}` build remains a superseded
baseline: one Han character fetched an entire ~2 MB `jp` face. Before any later topology change,
state artifact count, normal-page request count, exclusions and fallback owner, then obtain GLG
approval. The constraints in this section are the web delivery contract.

The web verifier checks the delivered WOFF2, never merely the source. It **has been wrong once**: an
earlier version read the source, and a delivered face with `GSUB` deleted passed all eight gates. A
gate that cannot fail is not a gate, so `test_webfont_gates.py` (`task web:test-gates`, ~24 s) plants
fourteen defects in a copy of the distribution and demands a FAIL for each. Any new gate arrives with
the mutation that proves it bites.

1. **Coverage:** each face's delivered cmap matches its declared exact set; split tiers are disjoint.
2. **Geometry:** decomposed outlines, advance and LSB match by glyph, including unencoded closure.
3. **Hinting:** glyph instructions and `cvt `/`fpgm`/`prep`/`gasp` survive. Do **not** demand binary
   equality of composite glyph records — their component GIDs are renumbered by design.
4. **Metrics:** compare stable **fields, not tables**. `hhea.numberOfHMetrics`, `maxp.numGlyphs` and
   `head.checkSumAdjustment` *must* differ; a whole-table check fails on a correct subset.
5. **Layout/shaping:** derive GPOS mark/base and GSUB ligature/context closure before partitioning;
   an unknown lookup type **fails closed**. Two traps live here, and both are why the gate models
   record semantics instead of trusting shaping:
   - **A chained context is its records, not its coverage.** Delete a type-6 rule's
     `SubstLookupRecord`s and the contexts still match — they simply substitute nothing, and coverage
     compares equal. This font makes it concrete: lookup 25 (`ccmp`, five subtables, each invoking
     lookup 26) has **coverage identical to lookup 29, which carries no records at all**. Project each
     record as `(SequenceIndex, the rules of the lookup it names)`, resolved by glyph name, because
     subsetting renumbers lookup indices.
   - **HarfBuzz composes before it lays out**, so shaping canaries cannot stand in for that check:
     `d` + U+030C becomes precomposed `dcaron`, and the `d/l/t/L` + caron chain never fires. `g` +
     U+0326 and `j` + U+0300 have no precomposed form, do fire, and are caught. **A rule no text can
     reach still must not be silently dropped.**
6. **Global/legal tables:** preserve `BASE` — `pyftsubset` drops unknown tables by default, so
   `--passthrough-tables` is required and the result must be verified binary-identical. Keep nameID
   0/13/14 (`--name-IDs='*' --name-legacy --name-languages='*'`), OFL and third-party notices.
7. **Stylesheet truth:** CSS ranges, filenames, hashes, sizes and manifest totals describe what ships.
8. **Determinism:** two clean builds match byte-for-byte. Required because notes serves WOFF2
   immutable for a year.

**Keep `post` glyph names.** Dropping them (post 3.0) is legitimate, but measured on the full Regular
face it saves only 79,768 bytes (~3%) — not enough to weaken name-based verification. If it is ever
done, subset **with** `--glyph-names`, verify against the source by name, then rewrite only `post` and
diff every other sfnt table against the verified intermediate.

The next two notes apply only when reproducing or inspecting the **superseded eight-file baseline**;
the final four-face contract has no `jp` tier:

- **`test_advance_widths.py` guards the desktop build. Never point it at a `jp` tier** — that tier has
  neither the Console discriminator characters nor most of the Latin contract glyphs. The web
  verifier compares each tier against its source face instead, which subsumes the zero-advance check.
- **Declare the baseline `jp` range by its blocks, not by its exact cmap.** Stating the cmap
  precisely takes 4,664 spans (≈50 KB per face, 200 KB across four), and the garden bundles its
  stylesheet into one render-blocking `index.css` — that moves the weight out of the font and into
  the CSS. Measured: 210.5 KB becomes 11.3 KB. The cost is that a missing ideograph fetches the tier
  and then falls back: a wasted request, never a wrong glyph. Codepoints shaping pulls into `core`
  are punched out of the `jp` range so the tiers never claim the same character; the verifier checks.

Do not reintroduce corpus-trained Hangul/Han frequency slicing or dozens of outputs. A discarded
192-file prototype proved that approach can minimize transfer but violates the cleanup goal. The
honest ceiling of a corpus-free design is that Hangul cannot be split further without frequency data
— Korean text scatters across the syllable block and would fetch every codepoint-ordered slice
anyway. Subsetting must preserve Korean bearing, physical Italic/BoldItalic, metrics, hinting,
`BASE`, legal names and supported-profile shaping. GPOS mark inputs include both marks and covered
bases; GSUB multi-input ligatures cannot cross physical files. In the superseded baseline, 14 PUA
codepoints were its only deliberate exclusion and remain recorded in that manifest. The final
four-face contract instead excludes Han and Kana by its own exact cmap.

### Glyph Handling

**Recovered metrics contract:**

```text
advance width = LSB + (bbox.xMax - bbox.xMin) + RSB
offset        = (target width - bbox width) / 2 - bbox.xMin
```

IBM Plex Sans KR Hangul uses advance 892 while inherited JP fullwidth glyphs use 1000. GLG maps
those outlines into 1056 (1:2) or 1000 (3:5) cells. The original KR outlines showed representative
28–45 unit side-bearing asymmetry; bbox centring reduced that to 0–2 units. The residual is accepted
TrueType integer rounding, not a reason for another global transform. The historical lesson is to
measure width, bbox, LSB and RSB from the generated font rather than infer them from Unicode blocks.

**Custom Adjustments:**
- Quotation marks: Enlarged and repositioned
- Punctuation (;:,.) : Scaled up 8%
- 'r' glyph: Custom via `source/AdjustedGlyphs/r-{Weight}.sfd` (non-italic).
  `fontforge_script.py:473` clears `eng_font[0x0072]` so the .sfd outline wins. The hand-adjustment
  that produced those files, inherited from PlemolJP: the point near the centre moves `x: -35`, the
  right end of the baseline stroke moves `x: -50`. Redo this if a new weight ever needs an `r`.
- Full-width brackets: Widened ±180 units
- Arrow symbols: Enlarged for visibility

**Width Normalization:**
- Glyphs < 500 → 600 (temporary half-width)
- Glyphs 500-1000 → 1000 (full-width)
- Final 1:2: 528:1056
- Final 3:5: 600:1000

**Korean Glyph Bearing (Overlap Fix):**
- IBM Plex Sans KR glyphs have actual width 892px (not 1000px)
- bbox-based center alignment: `offset = (target_width - actual_width) / 2 - bbox[0]`
- Applied in `set_width_600_or_1000()` and `transform_half_width()`
- **Critical**: Nerd Fonts patching requires post-processing
  - FontForge's `mergeFonts()` corrupts bearing alignment
  - `fix_nf_korean_bearing.py` re-applies center alignment
  - Automatically executed by `task patch:nerd`

### Font Table Modifications

**OS/2 Table:**
- `xAvgCharWidth`: Set to half-width (528 or 600)
- Weight values: 100-700

**post Table:**
- `isFixedPitch`: 1 for 1:2, 0 for 3:5

### Platform Compatibility

**macOS:**
- Removes horizontal baseline table
- Fixes glyph clipping in terminals

**VSCode Terminal:**
- Adjusted vertical metrics
- Ascent: 950, Descent: 225

## Resources

### Repository documents

- `README.md` — Korean, single public introduction. There is no `README-KO.md`; do not create one.
- `AGENTS.md` — durable product, build and verification contract.
- `ROADMAP.md` — long-horizon repository and font rebuild phases.
- `NEXT.md` — active handoff and unresolved repo hygiene.
- `CHANGELOG.md` — closed snapshots maintained by the `tag-release` loop.
- Digital Garden: https://notes.junghanacs.com

### Source Projects

- IBM Plex: https://github.com/IBM/plex
- PlemolJP: https://github.com/yuru7/PlemolJP
- PlemolKR: https://github.com/soomtong/PlemolKR
- Hack: https://github.com/source-foundry/Hack
- Nerd Fonts: https://github.com/ryanoasis/nerd-fonts

### Font Tools

- FontForge: https://fontforge.org/
- fontTools: https://github.com/fonttools/fonttools
- ttfautohint: https://www.freetype.org/ttfautohint/
- Task: https://taskfile.dev

## Important Notes

### Key Principles

1. **Always use `nix develop`** for consistent build environment
2. **Test with `task quick`** before full builds
3. **Verify glyphs** with `task verify` after changes
4. **Keep FONT_NAME=PlemolJP** in build.ini for compatibility
5. **Console variants** are the primary release targets

### Common Pitfalls

- Don't run build commands outside `nix develop`
- Don't change `FONT_NAME` in build.ini
- Don't forget `--do-not-delete-build-dir` for multi-variant builds
- Stage 2 (fonttools) must run after Stage 1 (fontforge)
- Italics are generated algorithmically (9° skew), not from source

### Performance Tips

- Use `--debug` for quick testing (Regular weight only)
- Use `--skip-nerd` for faster builds without Nerd Fonts
- Full Nerd Fonts patching takes 1-1.5 hours
- Quick build: ~3 minutes
- Full build: ~45 minutes with Nerd Fonts

## Contributing

Issues and pull requests are welcome.

For questions or discussions:
- GitHub Issues: https://github.com/junghan0611/GLG-Mono/issues
- Digital Garden: https://notes.junghanacs.com

---

**"모두의 힣"** - Code with a smile 🙂


