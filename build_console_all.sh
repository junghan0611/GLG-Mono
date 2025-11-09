#!/usr/bin/env bash
# Build all Console variants (PlemolKRConsole + PlemolKR35Console)
# This script runs the complete build process in nix-shell
#
# Usage:
#   ./build_console_all.sh [--zip]
#
# Options:
#   --zip    Create zip archives of the final fonts

set -e  # Exit on error

# Parse arguments
CREATE_ZIP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --zip)
            CREATE_ZIP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--zip]"
            exit 1
            ;;
    esac
done

echo "🚀 PlemolKR Console Full Build"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "build.ini" ]; then
    echo "❌ Error: build.ini not found. Please run from repository root."
    exit 1
fi

# Read version from build.ini
VERSION=$(grep "^VERSION" build.ini | cut -d'=' -f2 | tr -d ' ')

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

BUILD_LOG="build/build.log"

echo "Building PlemolKRConsole (1:2 ratio)..."
echo "  (Logs: $BUILD_LOG)"
time nix-shell --run "python3 fontforge_script.py --console" 2>"$BUILD_LOG"
echo "✅ PlemolKRConsole fontforge complete"
echo ""

echo "Building PlemolKR35Console (3:5 ratio)..."
echo "  (Logs: $BUILD_LOG)"
time nix-shell --run "python3 fontforge_script.py --console --35 --do-not-delete-build-dir" 2>>"$BUILD_LOG"
echo "✅ PlemolKR35Console fontforge complete"
echo ""

# Stage 2: FontTools - Post-processing (hinting & merging)
echo "🔧 Stage 2: FontTools (hinting & final processing)"
echo "---------------------------------------------------"

echo "Processing all Console variants..."
echo "  (Logs: $BUILD_LOG)"
time nix-shell --run "python3 fonttools_script.py" 2>>"$BUILD_LOG"
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

# Optional: Create zip archives
if [ "$CREATE_ZIP" = true ]; then
    echo "📦 Creating zip archives..."
    echo ""

    # Create zip for PlemolKRConsole
    if [ $CONSOLE_COUNT -gt 0 ]; then
        ZIP_NAME="PlemolKRConsole_${VERSION}.zip"
        cd build
        zip -q "$ZIP_NAME" PlemolKRConsole-*.ttf
        cd ..
        echo "  ✅ Created: build/$ZIP_NAME ($CONSOLE_COUNT fonts)"
    fi

    # Create zip for PlemolKR35Console
    if [ $CONSOLE35_COUNT -gt 0 ]; then
        ZIP_NAME="PlemolKR35Console_${VERSION}.zip"
        cd build
        zip -q "$ZIP_NAME" PlemolKR35Console-*.ttf
        cd ..
        echo "  ✅ Created: build/$ZIP_NAME ($CONSOLE35_COUNT fonts)"
    fi

    echo ""
fi

echo "✅ All Console variants built successfully!"
echo ""
echo "📄 Build log: $BUILD_LOG"
echo ""
echo "Next steps:"
echo "  1. Test fonts in Emacs: build/PlemolKRConsole-Regular.ttf"
echo "  2. Install fonts: cp build/PlemolKR*Console-*.ttf ~/.local/share/fonts/"
echo "  3. Refresh font cache: fc-cache -fv"
if [ "$CREATE_ZIP" = true ]; then
    echo "  4. Release packages: build/PlemolKR*Console_${VERSION}.zip"
fi
