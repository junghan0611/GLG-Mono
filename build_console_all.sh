#!/usr/bin/env bash
# Build all Console variants (PlemolKRConsole + PlemolKR35Console)
# This script runs the complete build process in nix-shell

set -e  # Exit on error

echo "🚀 PlemolKR Console Full Build"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "build.ini" ]; then
    echo "❌ Error: build.ini not found. Please run from repository root."
    exit 1
fi

# Start timing
START_TIME=$(date +%s)

# Clean build directory
echo "🧹 Cleaning build directory..."
rm -rf build
mkdir -p build
echo "✅ Clean complete"
echo ""

# Stage 1: FontForge - Build Console variants
echo "📝 Stage 1: FontForge (font merging & glyph manipulation)"
echo "--------------------------------------------------------"

echo "Building PlemolKRConsole (1:2 ratio)..."
time nix-shell --run "python3 fontforge_script.py --console"
echo "✅ PlemolKRConsole fontforge complete"
echo ""

echo "Building PlemolKR35Console (3:5 ratio)..."
time nix-shell --run "python3 fontforge_script.py --console --35 --do-not-delete-build-dir"
echo "✅ PlemolKR35Console fontforge complete"
echo ""

# Stage 2: FontTools - Post-processing (hinting & merging)
echo "🔧 Stage 2: FontTools (hinting & final processing)"
echo "---------------------------------------------------"

echo "Processing all Console variants..."
time nix-shell --run "python3 fonttools_script.py"
echo "✅ FontTools complete"
echo ""

# Final results
echo "📊 Build Results"
echo "================"
echo ""

echo "Generated fonts:"
ls -lh build/PlemolKR*Console*.ttf | grep -v fontforge | grep -v fonttools

echo ""
echo "Font count:"
CONSOLE_COUNT=$(ls build/PlemolKRConsole-*.ttf 2>/dev/null | wc -l)
CONSOLE35_COUNT=$(ls build/PlemolKR35Console-*.ttf 2>/dev/null | wc -l)
TOTAL_COUNT=$((CONSOLE_COUNT + CONSOLE35_COUNT))

echo "  PlemolKRConsole:   $CONSOLE_COUNT fonts"
echo "  PlemolKR35Console: $CONSOLE35_COUNT fonts"
echo "  Total:             $TOTAL_COUNT fonts"

# End timing
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "⏱️  Total build time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "✅ All Console variants built successfully!"
echo ""
echo "Next steps:"
echo "  1. Test fonts in Emacs: build/PlemolKRConsole-Regular.ttf"
echo "  2. Install fonts: cp build/PlemolKR*Console-*.ttf ~/.local/share/fonts/"
echo "  3. Refresh font cache: fc-cache -fv"
