{
  description = "GLG-Mono — 힣's monospace font: IBM Plex Mono + IBM Plex Sans KR/JP";

  # nixpkgs is the only input: this repo pins the same channel as the host system
  # (nixos-26.05), and a font build must be reproducible without further hops.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];
      forAllSystems = f:
        nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          name = "GLG-Mono";

          buildInputs = with pkgs; [
            # Stage 1 — glyph merging and width transforms
            fontforge

            # Stage 2/3 — table post-processing, hinting, WOFF2 web fonts.
            # Taken from the generic python3Packages set so the interpreter and its
            # modules cannot drift apart. brotli is what makes `font.flavor = "woff2"`
            # work; without it fontTools raises ImportError at save time.
            python3
            python3Packages.fonttools
            python3Packages.brotli
            python3Packages.ttfautohint-py
            python3Packages.uharfbuzz   # web verifier: shape with the real engine, not a model

            ttfautohint
            go-task
            fontconfig
            git
          ];

          shellHook = ''
            echo "GLG-Mono — font build environment"
            echo "=================================="
            python3 "${./work_scripts/env_report.py}" || true
            echo ""
            echo "  task                # list build tasks"
            echo "  task quick          # Regular-weight desktop build"
            echo "  task verify:widths  # advance-width regression gate"
            echo ""
          '';
        };
      });
    };
}
