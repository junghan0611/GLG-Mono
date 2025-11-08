# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PlemolKR** is a Korean programming font that merges IBM Plex Mono (English monospace) with IBM Plex Sans KR (Korean) to create a comprehensive programming font. This is a fork of the PlemolJP project, adapted for Korean language support.

**Repository**: soomtong/PlemolKR
**Current Branch**: kr
**Version**: v3.0.0
**License**: SIL Open Font License 1.1 (fonts), MIT License (build scripts)

### Font Composition
- **English/ASCII**: IBM Plex Mono (monospace, primary programming glyphs)
- **Korean**: IBM Plex Sans KR (Korean characters - primary target)
- **Japanese**: IBM Plex Sans JP (legacy support, may be removed)
- **Additional Glyphs**: Hack font (supplementary symbols)
- **Optional Icons**: Nerd Fonts (Powerline symbols, devicons)

### Migration Status: PlemolJP → PlemolKR
The codebase is in transition from PlemolJP to PlemolKR:
- `build.ini` defines both `FONT_NAME = PlemolJP` (legacy) and `NEW_FONT_NAME = PlemolKR`
- `fonttools_script.py` uses `NEW_FONT_NAME` to generate PlemolKR output files
- Some internal references still use PlemolJP naming - this is intentional for build compatibility

## Architecture

### Two-Stage Build Process

#### Stage 1: FontForge Script (fontforge_script.py)
Handles font merging and glyph manipulation:
1. Opens source fonts from `/source` directory
2. Unlinking font references for direct glyph manipulation
3. Adjusts EM squares (880 ascent + 120 descent = 1000 total)
4. Merges Hack font for supplementary glyphs
5. Deletes duplicate glyphs (prioritizes appropriate font for each range)
6. Applies custom glyph adjustments (punctuation, brackets, etc.)
7. Handles width transformations (1:2 or 3:5 ratios)
8. Generates italic variants via skew transformation (9 degrees)
9. Optionally adds Nerd Fonts glyphs
10. Outputs intermediate TTF files with `fontforge_` prefix

#### Stage 2: FontTools Script (fonttools_script.py)
Post-processes and finalizes fonts:
1. Applies ttfautohint with style-specific control files
2. Removes vhea/vmtx tables from Korean/Japanese font
3. Merges hinted English and Korean/Japanese portions
4. Extracts and modifies font tables (OS/2, post, name)
5. Fixes metadata for proper font recognition
6. Outputs final TTF files (removes temporary prefixes)

### Directory Structure

```
/source              - Source fonts and custom glyphs
  /IBM-Plex-Mono     - English monospace font (8 weights + italics)
  /IBM-Plex-Sans-KR  - Korean font (8 weights, no italics)
  /IBM-Plex-Sans-JP  - Japanese font (legacy)
  /hack              - Hack font for supplementary glyphs
  /nerd-fonts        - Optional Nerd Fonts symbols
  /AdjustedGlyphs    - Custom glyph modifications (.sfd files)
  FullWidthBoxDrawings.sfd - Custom box drawing characters

/build               - Output directory (gitignored, temporary files)

/hinting_post_process - ttfautohint control files
  normal-{Weight}-ctrl.txt  - Hinting for 1:2 width fonts
  35-{Weight}-ctrl.txt      - Hinting for 3:5 width fonts

/work_scripts        - Utility scripts
  check_glyph_number.py - Count glyphs in font files

/old_script          - Legacy bash/PowerShell scripts (deprecated)

/doc                 - Documentation
  install_via_homebrew.md - Homebrew installation guide

build.ini            - Build configuration
fontforge_script.py  - Stage 1: Font merging
fonttools_script.py  - Stage 2: Font finalization
Taskfile.yml         - Build automation
```

## Build System

### Prerequisites
- Python 3.x
- FontForge (with Python bindings)
- Python packages: fontTools, ttfautohint
- Task (taskfile.dev) - optional but recommended

### Configuration File (build.ini)

Critical settings:
```ini
VERSION = v3.0.0
FONT_NAME = PlemolJP      # Legacy internal name (do not change)
NEW_FONT_NAME = PlemolKR  # Output font name (use this for KR fonts)
JP_FONT = IBM-Plex-Sans-JP/unhinted/IBMPlexSansJP-{style}.ttf
KR_FONT = IBM-Plex-Sans-KR/unhinted/IBMPlexSansKR-{style}.ttf
ENG_FONT = IBM-Plex-Mono/IBMPlexMono-{style}.ttf

# Font metrics (EM = 1000)
EM_ASCENT = 880
EM_DESCENT = 120
OS2_ASCENT = 950
OS2_DESCENT = 225

# Width ratios
HALF_WIDTH_12 = 528   # Half-width for 1:2 ratio (528:1056)
FULL_WIDTH_35 = 1000  # Full-width for 3:5 ratio (600:1000)

ITALIC_ANGLE = 9
```

### Common Commands

**Using Taskfile (recommended):**
```bash
# Show available tasks
task

# Quick builds (debug mode - Regular weight only)
task quick              # Fastest: 1:2 ratio, Regular only
task quick:35           # 3:5 ratio, Regular only
task quick:nerd         # Nerd Fonts, Regular+Bold only

# Standard builds (stage 1: fontforge)
task build              # Default 1:2 ratio, all weights
task build:35           # 3:5 ratio, all weights
task build:console      # Console mode, all weights
task build:console35    # Console + 3:5 ratio

# Nerd Fonts builds
task build:nf           # 1:2 + Nerd Fonts
task build:nf35         # 3:5 + Nerd Fonts
task build:console-nf   # Console + Nerd Fonts
task build:console-nf35 # Console + 3:5 + Nerd Fonts

# Post-processing (stage 2: fonttools)
task polish             # Process all built fonts
task polish:variant VARIANT=35Console  # Process specific variant

# Complete workflows
task full               # Build + polish: default + 3:5
task full:all           # Build + polish: all variants
task full:nerd          # Build + polish: Nerd Fonts variants

# Nerd Fonts patching (using FontPatcher)
task patch:nerd         # Patch PlemolKRConsole fonts
task patch:nerd:wide    # Patch PlemolKR35Console fonts
task patch:nerd:all     # Patch all Console variants

# Utilities
task clean              # Remove build directory
task check              # List generated fonts and glyph count
task verify             # Check Korean/Japanese character presence
task install            # Install fonts to ~/Library/Fonts/ (macOS)
```

**Direct script usage:**
```bash
# fontforge_script.py (Stage 1)
python fontforge_script.py                # Build all variants (slow!)
python fontforge_script.py --debug        # Only Regular weight (fast)
python fontforge_script.py --minimal      # Only Regular + Bold
python fontforge_script.py --35           # 3:5 width ratio
python fontforge_script.py --console      # Console mode
python fontforge_script.py --nerd-font    # Include Nerd Fonts
python fontforge_script.py --hidden-zenkaku-space  # Hide full-width space
python fontforge_script.py --do-not-delete-build-dir  # Preserve existing builds

# Combine flags
python fontforge_script.py --35 --console --nerd-font --do-not-delete-build-dir

# fonttools_script.py (Stage 2)
python fonttools_script.py                # Process all fonts in build/
python fonttools_script.py 35             # Process only 35 variant
python fonttools_script.py Console        # Process only Console variant
python fonttools_script.py 35Console      # Process only 35Console variant

# Utilities
python work_scripts/check_glyph_number.py build/PlemolKR-Regular.ttf
python work_scripts/check_glyph_number.py -r source/  # Recursive
```

### Build Options Explained

**Width Ratios:**
- Default (1:2): Half-width is exactly 1/2 of full-width, compact
- `--35` (3:5): Half-width is 3/5 of full-width, larger ASCII characters

**Console Mode (`--console`):**
- Prioritizes IBM Plex Mono glyphs over Japanese/Korean
- Converts East Asian Ambiguous Width characters to half-width
- Includes additional console symbols (e.g., heavy check mark U+2714)
- Many symbols display as half-width

**Nerd Fonts (`--nerd-font`):**
- Adds Powerline symbols (U+E0B0-E0D7)
- Includes devicons and other programming-related symbols
- Glyphs adjusted to half-width

**Hidden Space (`--hidden-zenkaku-space`):**
- Disables full-width space (U+3000) visualization
- Default behavior makes accidental full-width spaces visible

### Font Families Generated

Each build produces multiple font families:

1. **PlemolKR** - Standard 1:2 width ratio (528:1056)
2. **PlemolKRConsole** - Console-optimized, half-width symbols
3. **PlemolKR35** - 3:5 width ratio (600:1000), larger ASCII
4. **PlemolKR35Console** - 3:5 width + console mode

Optional variants:
- **NF** suffix: Nerd Fonts included (e.g., PlemolKRConsoleNF)
- **HS** suffix: Hidden full-width Space (e.g., PlemolKRHS)

Each family includes:
- 8 weights: Thin, ExtraLight, Light, Regular, Text, Medium, SemiBold, Bold
- 2 styles per weight: Normal, Italic
- Total: 16 font files per family
- With all variants: 100+ font files possible

## Font Development Details

### Glyph Handling Strategy

**Duplicate Resolution:**
- U+00A2, U+00A3, U+00A5 (currency): Use IBM Plex Sans (Korean/Japanese)
- U+00C0-U+0259 (Latin Extended): Use IBM Plex Mono
- U+3000 (full-width space): Custom visualization or IBM Plex Sans
- U+274C (cross mark): Deleted (fallback to system emoji)
- Overlapping ranges: Carefully prioritized based on font purpose

**Custom Adjustments:**
- Quotation marks: Enlarged and repositioned
- Punctuation (;:,.) : Scaled up 8%
- 'r' glyph: Custom adjustment via .sfd file (non-italic only)
- Full-width brackets: Widened opening by ±180 units
- Full-width period/comma: Scaled up 40-45%
- Quotation marks (U+2018-201E): Scaled 25%, full-width
- Arrow symbols: Enlarged for better visibility
- Half-width symbols: Centered and scaled appropriately

**Width Normalization:**
- Glyphs < 500 width → 600 (temporary, becomes half-width later)
- Glyphs 500-1000 or Latin U+00C0-U+0192 → 1000 (full-width)
- Final 1:2 ratio: 528 (half) : 1056 (full)
- Final 3:5 ratio: 600 (half) : 1000 (full)

### Italic Generation
- Japanese/Korean fonts don't have italic styles natively
- Generated algorithmically via skew transformation (9° angle)
- Horizontal offset: -40 units
- English italics use native IBM Plex Mono Italic glyphs

### Hinting Strategy
- Uses ttfautohint for optimal rendering
- Style-specific control files in `/hinting_post_process/`
- Parameters: `-l 6 -r 45 -D latn -f none -S -W -X 13-`
- Italics use default hinting (no control file)
- Original hinting removed before reapplication

### Font Table Modifications

**OS/2 Table:**
- `xAvgCharWidth`: Set to half-width value (528 or 600)
- `fsSelection`: Style-specific bit flags
- `panose`: Adjusted for monospace/proportional classification
- Weight values: 100-700 based on style

**post Table:**
- `isFixedPitch`: 1 for 1:2 ratio, 0 for 3:5 ratio

**name Table:**
- Cleaned to remove erroneous copyright entries
- Family names follow pattern: `{FONT_NAME} {variant} {weight}`
- Supports both regular and typographic family names

### Technical Considerations

**macOS Compatibility:**
- Removes horizontal baseline table to fix glyph clipping in terminals
- Duplicate glyph names resolved with encoding suffix
- post table usage errors mitigated

**VSCode Terminal:**
- Vertical metrics adjusted for bottom-row character visibility
- Ascent: 950, Descent: 225, Linegap: 0

**Eclipse Pleiades:**
- Special handling for half-width space symbol (U+1D1C)

## Development Workflow

### Making Changes

1. **Modify Configuration**: Edit `build.ini` for version, metrics, or paths
2. **Adjust Glyphs**: Modify .sfd files in `/source/AdjustedGlyphs/`
3. **Change Build Logic**: Edit `fontforge_script.py` or `fonttools_script.py`
4. **Update Hinting**: Modify control files in `/hinting_post_process/`

### Testing Build

**Quick iteration cycle:**
```bash
# Method 1: Using tasks (recommended)
task quick              # Build + polish Regular weight only
task check              # Verify output

# Method 2: Using scripts directly
python fontforge_script.py --debug
python fonttools_script.py
ls -lh build/PlemolKR-Regular.ttf

# Method 3: Test specific variant
python fontforge_script.py --debug --35 --do-not-delete-build-dir
python fonttools_script.py 35
python work_scripts/check_glyph_number.py build/PlemolKR35-Regular.ttf
```

**Debug flags:**
- `--debug`: Build only Regular weight (fastest)
- `--minimal`: Build Regular + Bold only
- `--do-not-delete-build-dir`: Keep previous builds (for multi-variant testing)

**Verification:**
```bash
task check              # List fonts + glyph count
task verify             # Check Korean/Japanese character presence
```

## Code Style & Conventions

**FontForge scripting patterns:**
- Glyph selection: `font.selection.select(("unicode", None), 0xXXXX)`
- Always clear selections: `font.selection.none()`
- Reopen fonts after altuni manipulation to fix encoding issues
- Width transformations preserve ligature multiples
- Use uuid for temporary file naming to avoid conflicts

**Important conventions:**
- FONT_NAME in build.ini must remain "PlemolJP" for internal compatibility
- Use NEW_FONT_NAME for actual output file names
- Intermediate files use prefixes: `fontforge_*` and `fonttools_*`
- Final output removes prefixes

## Resources

### Source Font Information
- IBM Plex: https://github.com/IBM/plex
- Hack: https://github.com/source-foundry/Hack
- Nerd Fonts: https://github.com/ryanlmcintyre/nerd-fonts

### Font Development Tools
- FontForge: https://fontforge.org/
- fontTools: https://github.com/fonttools/fonttools
- ttfautohint: https://www.freetype.org/ttfautohint/

### Related Projects
- PlemolJP (original): https://github.com/yuru7/PlemolJP
- HackGen: https://github.com/yuru7/HackGen
- Firge: https://github.com/yuru7/Firge
- UDEV Gothic: https://github.com/yuru7/udev-gothic

## Key Files Reference

**Build system:**
- `fontforge_script.py` - Stage 1: Font merging and glyph manipulation (~1200 lines)
- `fonttools_script.py` - Stage 2: Hinting, table fixing (~300 lines)
- `build.ini` - Configuration (MUST use FONT_NAME=PlemolJP internally)
- `Taskfile.yml` - Build automation (Korean comments)

**Font sources:**
- `source/IBM-Plex-Mono/` - English monospace (16 files: 8 weights × 2 styles)
- `source/IBM-Plex-Sans-KR/` - Korean glyphs (8 weights, no italics)
- `source/IBM-Plex-Sans-JP/` - Japanese glyphs (legacy, 8 weights)
- `source/hack/` - Supplementary symbols (4 files)
- `source/nerd-fonts/` - Optional icon fonts
- `source/AdjustedGlyphs/` - Custom glyph modifications (.sfd files)

**Hinting control:**
- `hinting_post_process/normal-{Weight}-ctrl.txt` - For 1:2 ratio fonts
- `hinting_post_process/35-{Weight}-ctrl.txt` - For 3:5 ratio fonts

**Utilities:**
- `work_scripts/check_glyph_number.py` - Count glyphs in font files
- `FontPatcher/font-patcher` - Nerd Fonts patcher (external tool)

## Important Notes

### When modifying fonts:
1. Test with `task quick` first (fastest iteration)
2. Verify Korean characters with `task verify`
3. Check glyph counts with `task check`
4. Full build takes significant time - use `--debug` or `--minimal` flags

### Nerd Fonts integration:
- Built-in method: Use `--nerd-font` flag with fontforge_script.py
- External patcher: Use `task patch:nerd:all` on Console variants
- The external patcher (FontPatcher) provides more complete Nerd Fonts coverage

### Common pitfalls:
- Don't change FONT_NAME in build.ini (breaks internal logic)
- Don't forget `--do-not-delete-build-dir` when building multiple variants
- Stage 2 (fonttools) must run after Stage 1 (fontforge)
- Italic variants are generated algorithmically (9° skew), not from source files

