#!/usr/bin/env python3
"""Report the toolchain the dev shell actually provides.

Printed by the flake's shellHook. A missing entry here means a build stage will
fail later in a much less obvious way — brotli in particular only surfaces when
fontTools tries to save a WOFF2.
"""
import importlib
import sys

MODULES = ["fontforge", "fontTools", "brotli", "ttfautohint"]


def version_of(name: str) -> str:
    module = importlib.import_module(name)
    if name == "fontforge":
        return module.version()
    return getattr(module, "__version__", "ok")


def main() -> int:
    print(f"  {'python':12s}: {sys.version.split()[0]}")
    missing = []
    for name in MODULES:
        try:
            print(f"  {name:12s}: {version_of(name)}")
        except ImportError:
            print(f"  {name:12s}: MISSING")
            missing.append(name)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
