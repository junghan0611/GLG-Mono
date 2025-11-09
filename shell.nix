{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # FontForge with Python support
    fontforge

    # Python and required packages
    python3
    python3Packages.fonttools
    python3Packages.pip

    # Font hinting tool
    ttfautohint

    # Task runner
    go-task

    # Utilities
    git
  ];

  shellHook = ''
    echo "PlemolKR Font Build Environment"
    echo "================================"
    echo ""
    echo "Available commands:"
    echo "  task              - Show available build tasks"
    echo "  task quick        - Quick build (Regular weight only)"
    echo "  task build        - Full build"
    echo "  task check        - Check generated fonts"
    echo ""
    echo "Python packages:"
    python3 -c "import fontforge; print(f'  fontforge: {fontforge.version()}')" 2>/dev/null || echo "  fontforge: checking..."
    python3 -c "import fontTools; print(f'  fontTools: {fontTools.__version__}')" 2>/dev/null || echo "  fontTools: available"
    echo ""
  '';
}
