# ROADMAP — GLG-Mono rebuild

This is the long horizon. `NEXT.md` names the next concrete move; `CHANGELOG.md` records what
closed. The order matters: rebuild the repository and its observability before rebuilding the font.

## North star

GLG-Mono is 힣's working font, not a complete East Asian font. Every shipped codepoint must be
visible in an exact cmap, assigned to one source owner, and admitted by an allowlist. Unsupported
characters fall back; new characters enter only with an explicit codepoint and donor.

## R0 — Own the repository

Goal: turn an inherited PlemolJP/PlemolKR worktree into a small, truthful GLG-Mono repository.

- Keep one root document set: `README.md`, `AGENTS.md`, `NEXT.md`, `ROADMAP.md`, `CHANGELOG.md`.
- Audit inherited entry points and remove only after references and replacement paths are known.
- Resolve the stray `v3.0.0` tag and inspect the v1 release archives before asserting their
  contents or setting the next release policy.
- Decide whether unreferenced `make.ps1` and `old_script/*.sh` still earn a place.
- Keep legal provenance and the legacy internal `FONT_NAME=PlemolJP` compatibility invariant.

Exit: a new contributor can tell what is current, historical, generated, and safe to delete from the
root files alone.

## R1 — Publish the exact cmap

Goal: make the font inventory observable before changing assembly.

- Build a read-only inventory extractor for Plex Mono, Plex Sans KR, Plex Sans JP, Hack, and current
  GLG Regular/Bold faces.
- Generate the 8,567-codepoint Hanja seed from a pinned Source Han Sans KR 2.005 artifact, recording
  URL, version, input/output hashes, Unicode data version, alias count, and alias-map hash.
- Compose per-face expected cmap and owner maps; compare with actual output using
  `missing = expected - actual` and `unexpected = actual - expected`.
- Generate human-readable compressed ranges and an Emacs fontset from the exact list, never the
  other way around.

Exit: current Regular/Bold reproduce the documented 21,499 expected, 413 missing, and 6,760
unexpected baseline; every expected codepoint has one owner.

## R2 — Rebuild assembly by allowlist

Goal: produce clean Regular and Bold proofs without deciding architecture by argument.

- Subset each donor to owned codepoints and approved layout features before FontForge sees it.
- Admit JP outlines only for resolved Hanja seed entries; admit no Kana, radicals, enclosed forms,
  or regional layout by inheritance.
- Recover the full Plex Sans KR cmap, including `￦`, `㈜`, enclosed Hangul, and unit symbols.
- Preserve Latin/coding geometry, Hangul centring, zero-width glyphs, physical italics, legal names,
  and deterministic output.
- Use the existing type-6 chained-context projection and mutation discipline instead of inventing a
  weaker desktop verifier.

Exit: Regular and Bold both pass `missing == 0`, `unexpected == 0`, width, reachability, layout,
geometry, and legal-provenance gates without fragile exceptions. If JP-base needs exceptions,
replace it with KR-first assembly.

## R3 — Finish web delivery

Goal: ship four physical GLG web faces without a Han payload.

- Keep Regular, Bold, Italic, and BoldItalic; ordinary Korean pages request only Regular and Bold.
- Exclude Han and Kana from both WOFF2 cmap and CSS claims; a system or remote CJK font owns Han.
- Preserve coverage of the retained web cmap, decomposed geometry, hint programs, metrics fields,
  layout/shaping semantics, `BASE`, name IDs 0/13/14, notices, and deterministic hashes.
- Verify the files that ship, not their source; every new gate arrives with a mutation proving it
  can fail.
- Browser-check Korean, NFD marks, Jamo, ligatures, physical italics, and Han fallback canaries such
  as `脈`, `如`, `一日一生`, and `無學論道`.

Exit: four immutable WOFF2 files, two normal-page requests, no GLG Han request, no tofu, and measured
bytes/LCP/CLS accepted by GLG.

## R4 — Visual polish only after ownership

Recovered research identified useful later questions, but none may bypass the cmap contract.

- **Math:** default to IBM Plex Math as an Emacs fallback. Consider individual symbols or a separate
  variant only after real usage supplies an explicit codepoint list and owner; never import whole
  Unicode blocks for “completeness.”
- **Line height:** inventory actual ascent/descent violations before scaling anything. Math symbols,
  emoji, box drawing, block elements, geometric shapes, and PUA each need measured canaries and
  source ownership; no blanket block transformation.
- **Bearing:** preserve bbox centring for Korean fullwidth glyphs and the NF post-process. A 0–2 unit
  residual from integer rounding is acceptable; a new transform must prove it does not disturb
  unrelated glyphs.
- **Terminal symbols:** preserve fullwidth/halfwidth contracts and verify box drawing joins at the
  rendered pixel level rather than assuming Unicode category implies geometry.

Exit: each polish change answers a concrete rendering problem, has before/after evidence, and adds a
gate that fails without the fix.

## R5 — Productize and snapshot

- Extend the clean proof to all eight weights, physical Italic/BoldItalic, Console/35, HS, and NF
  variants only after R2 passes.
- Reconcile release assets with the Console-first policy and publish exact cmap/range/Emacs outputs
  beside the fonts.
- Use the `tag-release` loop: move closed NEXT items and commits into `CHANGELOG.md`, cut an explicit
  CalVer snapshot, push, and stamp the agenda only when GLG requests it.
