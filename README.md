# GLG-Mono

> **Hih's Monospace Font for 8-Layer Ecosystem**

GLG-Mono is a Korean programming font designed for knowledge management and AI collaboration. It merges IBM Plex Mono (English) with IBM Plex Sans KR (Korean) to provide comprehensive Unicode support in terminals and editors.

[한글 문서](README-KO.md) | [Philosophy](docs/PHILOSOPHY.org)

## Name Origin

### 힣 (U+D7A3) - Hangul Syllable Hih
- The last syllable in Korean Unicode
- Philosophical meaning: "Letting go of ego" - writing without self
- Technical meaning: End boundary of regex `[가-힣]`

### GLG - Giggling Language Glyph
- "힣" typed on QWERTY keyboard = "glg"
- English meaning: "giggling" - coding with a smile
- "힣 for everyone" - joyful writing for all

For deeper philosophy and background, see [`docs/PHILOSOPHY.org`](docs/PHILOSOPHY.org).

## Key Features

### 1. Unicode Completeness
- **87% → 100% Coverage**: All symbols needed for knowledge management
- **Denote File Naming**: Perfect support for metadata-rich filenames
  ```
  § ¶ † ‡ № ⓕ ↔ → ⊢ ∉ © ¬ ¢ ¤ µ ¥ £ ¡ ¿
  ```
- **Programming Ligatures**: Functional programming and logic symbols
  ```
  λ ƒ ∘ ∅ ∈ ∉ ∧ ∨ ∀ ∃
  ```
- **Planned Addition**: Double-struck math symbols (ℤ ℝ 𝔹 𝕥 𝕗)
- **Math & Logic Symbols**: Type systems, functional programming, logic operations
- **Ancient Korean**: ㅹ ㆅ ㅺ ㉼ ㉽
- **CJK Brackets**: 『』 《》 〈〉 ｢｣

### 2. 8-Layer Ecosystem Integration
GLG-Mono serves as the foundational typography across a multi-layered knowledge system:

```
Layer 7: Knowledge Publishing  → Digital Garden (notes.junghanacs.com)
Layer 6: Agent Orchestration   → meta-config
Layer 5a: Migration            → memex-kb
Layer 5b: Life Timeline        → memacs-config
Layer 4: AI Memory             → claude-config (PARA + Denote)
Layer 3: Knowledge Management  → Org-mode 1,400+ files + Zotero 156k+ lines
Layer 2: Development           → doomemacs-config
Layer 1: Infrastructure        → nixos-config
```

Provides consistent typography across all layers with a single font.

### 3. TUI Terminal Optimization
- **Single-Font Completeness**: Terminals have limited font fallback (unlike Emacs)
- **AI Agent Collaboration**: Optimized for terminal-based AI tools (Claude Code, etc.)
- **Console Mode**: Half-width display for arrows and other symbols
- **Nerd Fonts Support**: Powerline symbols, devicons, and dev icons

### 4. Technical Differentiation
- **Korean Glyph Bearing Fix**: Precise rendering without overlap (LSB/RSB 0-2px)
- **Web Font Support**: WOFF2 format for Digital Garden integration
- **Full Set by Default**: Includes Normal, Console, 35, 35Console variants
- **8 Weights**: Thin ~ Bold, each in Regular/Italic styles

## Font Families

| Font Family | Width Ratio | Description |
|------------|-------------|-------------|
| **GLG-Mono** | Half 1:Full 2 | Standard version. IBM Plex Mono for ASCII, IBM Plex Sans for Korean/Japanese |
| **GLG-Mono Console** | Half 1:Full 2 | Console-optimized. Half-width symbols (arrows, etc.). Recommended for terminals |
| **GLG-Mono 35** | Half 3:Full 5 | Larger ASCII version. Better for English-heavy code |
| **GLG-Mono 35 Console** | Half 3:Full 5 | Combines 35 ratio with Console mode |

### Optional Variants
- **NF** suffix: Includes Nerd Fonts (e.g., GLG-MonoConsoleNF)
- **HS** suffix: Hidden full-width Space (disables visualization)

Each family provides 16 files (8 weights × 2 styles).

## Download & Installation

### Download from Releases
Select your preferred variant from the Assets section of the release page:

- `GLG-Mono_vx.x.x.zip` - Standard version
- `GLG-Mono_NF_vx.x.x.zip` - With Nerd Fonts
- `GLG-Mono_HS_vx.x.x.zip` - Hidden full-width space

### Installation

**Linux:**
```bash
mkdir -p ~/.local/share/fonts/GLG-Mono
unzip GLG-Mono_*.zip -d ~/.local/share/fonts/GLG-Mono
fc-cache -fv
```

**macOS:**
```bash
# Method 1: Double-click TTF files in Finder
# Method 2: Command line
cp *.ttf ~/Library/Fonts/
```

**Windows:**
1. Extract downloaded ZIP file
2. Select TTF files → Right-click → "Install"

## Building from Source

### Requirements
- Python 3.x
- FontForge (with Python bindings)
- Python packages: `fontTools`, `ttfautohint`
- Task (optional, recommended): https://taskfile.dev

### Build System

**For NixOS users:**
```bash
nix-shell  # Automatically loads all dependencies
```

**Using Taskfile (recommended):**
```bash
# Quick test builds (Regular weight only)
task quick              # 1:2 ratio
task quick:35           # 3:5 ratio
task quick:nerd         # Nerd Fonts

# Full builds (all weights)
task build              # Standard 1:2
task build:console      # Console mode
task build:nf           # Nerd Fonts
task build:console-nf35 # Console + 3:5 + Nerd Fonts

# Build + post-process (complete fonts)
task full               # Standard + 35
task full:all           # All variants
task full:nerd          # Nerd Fonts variants

# Utilities
task check              # List built fonts
task verify             # Verify Korean/Japanese glyphs
task clean              # Remove build directory
```

**Direct script execution:**
```bash
# Stage 1: FontForge (font merging)
python fontforge_script.py --debug --console --nerd-font

# Stage 2: FontTools (hinting & finalization)
python fonttools_script.py

# Check results
ls -lh build/GLG-Mono*.ttf
```

See `Taskfile.yml` for detailed build options.

## Project Lineage

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
  - Unicode completeness
  - 8-Layer ecosystem integration
```

Thanks to all contributors.

## License

- **Font files**: SIL Open Font License 1.1
- **Build scripts**: MIT License

See [LICENSE](LICENSE) file for details.

## Related Links

- **Digital Garden**: https://notes.junghanacs.com (힣's Digital Garden)
- **Project Philosophy**: [docs/PHILOSOPHY.org](docs/PHILOSOPHY.org)
- **Build Guide**: [docs/BUILD.md](docs/BUILD.md) (coming soon)
- **PlemolJP**: https://github.com/yuru7/PlemolJP
- **PlemolKR**: https://github.com/soomtong/PlemolKR
- **IBM Plex**: https://github.com/IBM/plex

## Contributing

Issues and pull requests are always welcome.

See [`CLAUDE.md`](CLAUDE.md) for project philosophy and coding guidelines.

---

**"힣 for everyone"** - Code with a smile 🙂
