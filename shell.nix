let
  # Pin to NixOS 25.05 stable
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-25.05.tar.gz";
  pkgs = import nixpkgs {};
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    # FontForge with Python support
    fontforge

    # Python 3.12 and required packages
    python312
    python312Packages.fonttools
    python312Packages.ttfautohint-py  # Python bindings for ttfautohint
    python312Packages.pip

    # Font hinting tool (CLI)
    ttfautohint

    # Task runner
    go-task

    # Utilities
    git
    fontconfig  # For fc-cache, fc-list
  ];

  shellHook = ''
    echo "PlemolKR Font Build Environment"
    echo "================================"
    echo ""
    echo "Available commands:"
    echo "  task                      - Show available build tasks"
    echo "  ./build_console_all.sh    - Build all Console variants (recommended)"
    echo "  task quick                - Quick build (Regular weight only)"
    echo "  task build                - Full build"
    echo ""
    echo "Python packages:"
    python3 -c "import fontforge; print(f'  fontforge: {fontforge.version()}')" 2>/dev/null || echo "  fontforge: checking..."
    python3 -c "import fontTools; print(f'  fontTools: {fontTools.__version__}')" 2>/dev/null || echo "  fontTools: available"
    python3 -c "import ttfautohint; print(f'  ttfautohint: available')" 2>/dev/null || echo "  ttfautohint: missing (install required)"
    echo ""
  '';
}
