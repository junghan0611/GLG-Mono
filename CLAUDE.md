# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**GLG-Mono** (힣's Monospace Font) is a Korean programming font for knowledge management and AI collaboration. It merges IBM Plex Mono (English) with IBM Plex Sans KR (Korean) to provide complete Unicode coverage for the 8-Layer ecosystem.

**Repository**: junghan0611/GLG-Mono
**Version**: v1.0.0
**License**: SIL Open Font License 1.1 (fonts), MIT License (build scripts)

### Name Origin

- **힣 (U+D7A3)**: Last syllable in Korean Unicode, meaning "letting go of ego"
- **GLG**: "힣" typed on QWERTY keyboard, meaning "giggling" - coding with a smile
- **Philosophy**: See `docs/PHILOSOPHY.org`

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
  - Knowledge management & AI collaboration font
  - Unicode completeness (87% → 100% goal)
  - 8-Layer ecosystem integration
```

## Development Environment

### NixOS Setup (Required)

**All build commands must run inside nix-shell:**

```bash
# Enter development environment
nix-shell

# Or run single command
nix-shell --run "task quick"
```

The `shell.nix` file provides:
- Python 3 with FontForge bindings
- fontTools and ttfautohint packages
- All required dependencies for font building

### Prerequisites

When using nix-shell, all dependencies are automatically provided:
- Python 3.x
- FontForge (with Python bindings)
- fontTools
- ttfautohint
- Task (taskfile.dev)

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

### Two-Stage Build Process

1. **Stage 1: FontForge** (`fontforge_script.py`)
   - Font merging and glyph manipulation
   - Width transformations
   - Italic generation (9° skew)
   - Optional Nerd Fonts integration

2. **Stage 2: FontTools** (`fonttools_script.py`)
   - ttfautohint application
   - Font table modifications
   - Final post-processing

### Quick Start

```bash
# Enter nix-shell
nix-shell

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
# Inside nix-shell
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
task patch:nerd         # Patch GLG-MonoConsole
task patch:nerd:wide    # Patch GLG-Mono35Console
task patch:nerd:all     # Patch all Console variants
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
  /IBM-Plex-Sans-JP  - Japanese font (legacy)
  /hack              - Supplementary glyphs
  /nerd-fonts        - Optional Nerd Fonts
  /AdjustedGlyphs    - Custom glyph modifications (.sfd)

/build               - Output directory (gitignored)

/hinting_post_process - ttfautohint control files
  normal-{Weight}-ctrl.txt  - For 1:2 ratio
  35-{Weight}-ctrl.txt      - For 3:5 ratio

/docs                - Documentation
  PHILOSOPHY.org     - Project philosophy
  install_via_homebrew.md - Homebrew guide

/work_scripts        - Utility scripts

build.ini            - Build configuration
fontforge_script.py  - Stage 1: Font merging
fonttools_script.py  - Stage 2: Post-processing
Taskfile.yml         - Build automation
shell.nix            - NixOS development environment
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
# Quick iteration (inside nix-shell)
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

### Glyph Handling

**Custom Adjustments:**
- Quotation marks: Enlarged and repositioned
- Punctuation (;:,.) : Scaled up 8%
- 'r' glyph: Custom via .sfd (non-italic)
- Full-width brackets: Widened ±180 units
- Arrow symbols: Enlarged for visibility

**Width Normalization:**
- Glyphs < 500 → 600 (temporary half-width)
- Glyphs 500-1000 → 1000 (full-width)
- Final 1:2: 528:1056
- Final 3:5: 600:1000

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

### Documentation

- Philosophy: `docs/PHILOSOPHY.org`
- Korean README: `README-KO.md`
- English README: `README.md`
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

1. **Always use nix-shell** for consistent build environment
2. **Test with `task quick`** before full builds
3. **Verify glyphs** with `task verify` after changes
4. **Keep FONT_NAME=PlemolJP** in build.ini for compatibility
5. **Console variants** are the primary release targets

### Common Pitfalls

- Don't run build commands outside nix-shell
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
