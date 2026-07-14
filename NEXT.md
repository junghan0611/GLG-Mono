# NEXT — GLG-Mono

Boot sector for the next session. Durable contract: `AGENTS.md`; long horizon: `ROADMAP.md`.
Closed work moves to `CHANGELOG.md` through the `tag-release` loop.

# NOW — R0: own the inherited repository

Do not start cmap or font implementation yet. The current job is to decide what belongs in
GLG-Mono, recover durable information from inherited material, and leave a small truthful surface.

Snapshot `v2026.7.14` establishes the recovered root knowledge surface. R0 remains open for the
tracked-root, inherited-script, tag, and release-asset decisions below.

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
5. **Close R0:** record the decisions above in the durable surfaces, remove their completed NEXT
   items through the next tag-release loop, and rerun root-link/task/reference checks and hooks.

## R0 acceptance

- A new session can understand the repository from the five root documents without hidden design
  files.
- No broken links, stale task names, false coverage claims, or contradictory license statements.
- Every retained inherited script or vendor directory has an explicit reason to remain.
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
