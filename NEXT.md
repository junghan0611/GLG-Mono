# NEXT — GLG-Mono

Boot sector for the next session. Durable contract: `AGENTS.md`; long horizon: `ROADMAP.md`.
Closed work moves to `CHANGELOG.md` through the `tag-release` loop.

# NOW — R0: own the inherited repository

Do not start cmap or font implementation yet. The current job is to decide what belongs in
GLG-Mono, recover durable information from inherited material, and leave a small truthful surface.

## Current checkpoint

- Root document set established: `README.md`, `AGENTS.md`, `NEXT.md`, `ROADMAP.md`, `CHANGELOG.md`.
- The old `docs/` tree is removed only after its durable content was promoted:
  - bearing metrics and web/cmap gates → `AGENTS.md`;
  - completed build, bearing, web and cmap work → `CHANGELOG.md`;
  - math fallback, Unicode-height ideas and rebuild phases → `ROADMAP.md`;
  - philosophy and product identity → `README.md`;
  - terminal screenshot → `assets/glg-mono-terminal.png`.
- No font implementation changed. Two Python docstrings now point at `AGENTS.md` instead of deleted
  documents; `webfont_subset.py` also corrects the stale Han count from 13,412 to 13,022.

## Next concrete move

1. **Root inventory:** classify every tracked top-level entry as product source, build entry point,
   generated/vendor material, historical compatibility, or deletion candidate. Do not delete code
   merely because references are absent.
2. **Inherited build candidates:** decide `make.ps1` and `old_script/*.sh`. Confirm whether Windows or
   historical reproduction still matters before removal. `build_console_all.sh` stays because the
   Taskfile references it.
3. **Tag hygiene:** decide whether to delete the stray local/remote `v3.0.0` tag, which points to
   older inherited history and has no matching release.
4. **Release truth:** inspect the published v1 desktop/NF archives before asserting their internal
   family/variant contents; reconcile the evidence with the Console-first release policy.
5. **Close R0:** rerun root-link/task/reference checks and the global hooks, then review the staged
   repository rebuild as one coherent commit. Push and stamp only on explicit GLG request.

## R0 acceptance

- A new session can understand the repository from the five root documents without hidden design
  files.
- No broken links, stale task names, false coverage claims, or contradictory license statements.
- Every retained inherited script or vendor directory has an explicit reason to remain.
- Removed research remains recoverable from git history and its durable findings are represented in
  AGENTS, ROADMAP, or CHANGELOG.
- `git diff --check` and the global pre-commit hook pass; no long font build is required for the
  document/repository-only checkpoint.

## R0 stop conditions

- Do not start `font_inventory.py`, Hanja seed generation, donor subsetting, or web implementation.
- Do not alter source fonts, `FONT_NAME=PlemolJP`, legal provenance, or build behaviour.
- Do not turn ROADMAP ideas into requirements without current measurements.
- Do not recreate a `docs/` archive; git history is the raw archive.

# PARKED — R1: publish the exact cmap

After R0 closes, resume at ROADMAP R1:

1. read-only Regular/Bold inventory;
2. pinned 8,567-codepoint Hanja seed and donor-resolution provenance;
3. expected/actual cmap and owner gate;
4. `/tmp` allowlist-first Regular + Bold proof;
5. compressed range and Emacs fontset output;
6. separate four-face Han/Kana-free web lane.

Baseline to reproduce, not merely quote:

```text
expected cmap   21,499
current cmap    27,846
missing            413 = 163 base-layer codepoints + 250 aliases
unexpected        6,760 = 1,424 non-Han + 5,336 Han
```

The full fixed decisions, gates and FontForge traps live in `AGENTS.md`; do not duplicate them here.
