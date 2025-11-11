#!/usr/bin/env bash
# GLG-Mono Full Build Script using Taskfile.yml
# Builds Console variants with Nerd Fonts patches
#
# Usage:
#   ./build_with_taskfile.sh [--with-35] [--skip-nerd] [--nerd-only] [--help]
#
# Options:
#   --with-35     Also build GLG-Mono35Console (3:5 ratio, adds 16 more fonts)
#   --skip-nerd   Skip Nerd Fonts patching (not recommended for releases)
#   --nerd-only   Only run Nerd Fonts patching (requires existing fonts)
#   --help        Show this help message

set -e  # Exit on error

# Function to show help
show_help() {
    cat << 'EOF'
GLG-Mono Build Script (Taskfile.yml wrapper)

USAGE:
    ./build_with_taskfile.sh [OPTIONS]

OPTIONS:
    --with-35       Build both GLG-Mono (1:2) and GLG-Mono35Console (3:5)
                    Default: Only GLG-Mono (16 fonts)
                    With this: Both variants (32 fonts total)

    --skip-nerd     Skip Nerd Fonts patching (faster for testing)
                    Default: Include Nerd Fonts
                    Build time: ~3 minutes vs ~45 minutes

    --nerd-only     Only patch existing fonts with Nerd Fonts
                    Requires fonts already built in build/ directory
                    Useful for adding Nerd Fonts to existing builds

    --help          Show this help message

EXAMPLES:
    # Official release build (GLG-Mono + Nerd Fonts, ~45 min)
    ./build_with_taskfile.sh

    # Full build (both ratios + Nerd Fonts, ~1.5 hours)
    ./build_with_taskfile.sh --with-35

    # Quick test build (no Nerd Fonts, ~3 minutes)
    ./build_with_taskfile.sh --skip-nerd

    # Add Nerd Fonts to existing fonts
    ./build_with_taskfile.sh --nerd-only

    # All variants without Nerd Fonts (~6 minutes)
    ./build_with_taskfile.sh --with-35 --skip-nerd

WORKFLOW:
    1. Release:     ./build_with_taskfile.sh
    2. Development: ./build_with_taskfile.sh --skip-nerd
    3. Full build:  ./build_with_taskfile.sh --with-35

OUTPUT:
    build/GLG-Mono-*.ttf       - Basic fonts (1:2 ratio)
    build/GLG-Mono35Console-*.ttf     - Wide fonts (3:5 ratio)
    build/nerd/GLG-Mono*Console-*.ttf - Nerd Fonts variants

REQUIREMENTS:
    - Run inside nix-shell for proper environment
    - Taskfile.yml must exist in current directory

For more information, see BUILD_GUIDE.md or run 'task' for available tasks.
EOF
    exit 0
}

# Parse arguments
BUILD_35=false
INCLUDE_NERD=true  # Default: Include Nerd Fonts (soomtong's official build)
NERD_ONLY=false

# Check if no arguments provided
if [[ $# -eq 0 ]]; then
    # Show brief usage hint
    echo "💡 Tip: Run with --help to see all options"
    echo ""
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --with-35)
            BUILD_35=true
            shift
            ;;
        --skip-nerd)
            INCLUDE_NERD=false
            shift
            ;;
        --nerd-only)
            NERD_ONLY=true
            INCLUDE_NERD=true
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo ""
            echo "Usage: $0 [--with-35] [--skip-nerd] [--nerd-only] [--help]"
            echo "Run with --help for detailed information"
            exit 1
            ;;
    esac
done

echo "🚀 GLG-Mono Taskfile.yml Build"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "Taskfile.yml" ]; then
    echo "❌ Error: Taskfile.yml not found. Please run from repository root."
    exit 1
fi

# Check if task is available
if ! command -v task &> /dev/null; then
    echo "❌ Error: 'task' command not found."
    echo "Please run inside nix-shell or install go-task."
    exit 1
fi

# Read version from build.ini
VERSION=$(grep "^VERSION" build.ini | cut -d'=' -f2 | tr -d ' ')

# Start timing
START_TIME=$(date +%s)

# Setup logging
BUILD_LOG="build/build.log"
mkdir -p build

if [ "$NERD_ONLY" = false ]; then
    # Stage 1: Clean
    echo "🧹 Step 1/4: Clean build directory"
    echo "-----------------------------------"
    task clean
    echo "✅ Clean complete"
    echo ""

    # Stage 2: FontForge - Build Console variants
    echo "📝 Step 2/4: FontForge (font merging & glyph manipulation)"
    echo "-----------------------------------------------------------"
    echo "  (Progress: console output, Logs: $BUILD_LOG)"
    echo ""

    echo "Building GLG-Mono (1:2 ratio)..."
    time task build:console 2>"$BUILD_LOG"
    echo "✅ GLG-Mono fontforge complete"
    echo ""

    if [ "$BUILD_35" = true ]; then
        echo "Building GLG-Mono35Console (3:5 ratio)..."
        time task build:console35 2>>"$BUILD_LOG"
        echo "✅ GLG-Mono35Console fontforge complete"
        echo ""
    fi

    # Stage 3: FontTools - Post-processing
    echo "🔧 Step 3/4: FontTools (hinting & final processing)"
    echo "---------------------------------------------------"
    echo "  (Progress: console output, Logs: $BUILD_LOG)"
    echo ""

    if [ "$BUILD_35" = true ]; then
        echo "Processing all Console variants..."
        time task polish 2>>"$BUILD_LOG"
    else
        echo "Processing GLG-Mono only..."
        time task polish:variant VARIANT=Console 2>>"$BUILD_LOG"
    fi
    echo "✅ FontTools complete"
    echo ""

    # Display intermediate results
    echo "📊 Build Results (before Nerd Fonts)"
    echo "====================================="
    echo ""

    echo "Generated fonts:"
    ls -lh build/GLG-Mono*Console*.ttf 2>/dev/null | grep -v fontforge | grep -v fonttools || echo "No fonts generated yet"

    echo ""
    echo "Font count:"
    CONSOLE_COUNT=$(ls build/GLG-Mono-*.ttf 2>/dev/null | wc -l)
    CONSOLE35_COUNT=$(ls build/GLG-Mono35Console-*.ttf 2>/dev/null | wc -l)
    TOTAL_COUNT=$((CONSOLE_COUNT + CONSOLE35_COUNT))

    echo "  GLG-Mono:   $CONSOLE_COUNT fonts"
    if [ "$BUILD_35" = true ]; then
        echo "  GLG-Mono35Console: $CONSOLE35_COUNT fonts"
    fi
    echo "  Total:             $TOTAL_COUNT fonts"
    echo ""
fi

# Stage 4: Nerd Fonts Patching (optional)
if [ "$INCLUDE_NERD" = true ] || [ "$NERD_ONLY" = true ]; then
    echo "🎨 Step 4/4: Nerd Fonts Patching"
    echo "================================="
    echo ""
    echo "⚠️  Warning: This step takes 1-1.5 hours for all 32 fonts"
    echo ""

    # Check if fonts exist
    if [ ! -f "build/GLG-Mono-Regular.ttf" ]; then
        echo "❌ Error: Base fonts not found. Run without --nerd-only first."
        exit 1
    fi

    # Setup Nerd Fonts logging
    NERD_LOG="build/nerd_patch.log"

    if [ "$BUILD_35" = true ]; then
        echo "Starting Nerd Fonts patch for all Console variants..."
        echo "  (Progress: console output, Detailed logs: $NERD_LOG)"
        echo "  (Monitor in another terminal: tail -f $NERD_LOG)"
        echo ""
        # Run patch - stderr to log, stdout to console
        time task patch:nerd:all 2>"$NERD_LOG"
    else
        echo "Starting Nerd Fonts patch for GLG-Mono only..."
        echo "  (Progress: console output, Detailed logs: $NERD_LOG)"
        echo "  (Monitor in another terminal: tail -f $NERD_LOG)"
        echo ""
        # Run patch for GLG-Mono only
        time task patch:nerd 2>"$NERD_LOG"
    fi

    echo ""
    echo "✅ Nerd Fonts patching complete"
    echo ""

    # Display Nerd Fonts results
    echo "📊 Nerd Fonts Results"
    echo "====================="
    echo ""

    if [ -d "build/nerd" ]; then
        NERD_CONSOLE_COUNT=$(ls build/nerd/GLG-MonoNF-*.ttf 2>/dev/null | wc -l)
        NERD_CONSOLE35_COUNT=$(ls build/nerd/GLG-Mono35ConsoleNF-*.ttf 2>/dev/null | wc -l)
        NERD_TOTAL_COUNT=$((NERD_CONSOLE_COUNT + NERD_CONSOLE35_COUNT))

        echo "Generated Nerd Fonts:"
        echo "  GLG-MonoNF:    $NERD_CONSOLE_COUNT fonts"
        echo "  GLG-Mono35ConsoleNF:  $NERD_CONSOLE35_COUNT fonts"
        echo "  Total:                $NERD_TOTAL_COUNT fonts"
        echo ""

        echo "Sample fonts:"
        ls -lh build/nerd/ | head -10
    else
        echo "❌ No Nerd Fonts generated (check nerd_patch.log)"
    fi
fi

# End timing
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "⏱️  Total build time: ${MINUTES}m ${SECONDS}s"
echo ""

# Summary
echo "✅ Build Complete!"
echo "=================="
echo ""

if [ "$NERD_ONLY" = false ]; then
    echo "📁 Output locations:"
    if [ "$BUILD_35" = true ]; then
        echo "  Basic fonts:  build/GLG-Mono*Console-*.ttf (32 fonts)"
        if [ "$INCLUDE_NERD" = true ]; then
            echo "  Nerd Fonts:   build/nerd/GLG-Mono*ConsoleNF-*.ttf (32 fonts)"
        fi
    else
        echo "  Basic fonts:  build/GLG-Mono-*.ttf (16 fonts)"
        if [ "$INCLUDE_NERD" = true ]; then
            echo "  Nerd Fonts:   build/nerd/GLG-MonoNF-*.ttf (16 fonts)"
        fi
    fi
    echo ""
fi

echo "📋 Next steps:"
echo "  1. Verify fonts: task verify"
if [ "$INCLUDE_NERD" = true ] || [ "$NERD_ONLY" = true ]; then
    echo "  2. Check Nerd Fonts: task verify:nerd"
    echo "  3. Test in Emacs: build/nerd/GLG-MonoNF-Regular.ttf"
else
    echo "  2. Test in Emacs: build/GLG-Mono-Regular.ttf"
    echo "  3. (Optional) Add Nerd Fonts: ./build_with_taskfile.sh --nerd-only"
fi
echo "  4. Install fonts: cp build/GLG-Mono*Console*.ttf ~/.local/share/fonts/"
echo "  5. Refresh font cache: fc-cache -fv"
echo ""

# Log file summary
echo "📄 Build logs:"
if [ "$NERD_ONLY" = false ]; then
    echo "  FontForge/FontTools: $BUILD_LOG"
fi
if [ "$INCLUDE_NERD" = true ] || [ "$NERD_ONLY" = true ]; then
    echo "  Nerd Fonts patch:    $NERD_LOG"
fi
echo ""
