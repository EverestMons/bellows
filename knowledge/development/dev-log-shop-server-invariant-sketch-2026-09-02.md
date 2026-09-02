# Dev Log — shop-server-invariant-sketch-2026-09-02 (plan 100018, Step 1)

**Date:** 2026-09-02
**Plan:** `shop-server-invariant-sketch-2026-09-02`
**Plan id:** 100018
**Step:** 1 (DEV)

## Roots

- **Bellows worktree:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100018` — resolved via `git rev-parse --show-toplevel`; `bellows.py` and `tests/` present (TREE_OK)
- **Governance root (`$GOV`):** `/Users/marklehn/Developer/eluvian-governance` — `$SK` and `COMPANY.md` both present (GOV_OK)
- **Canonical venv (`$BPY`):** `/Users/marklehn/Developer/bellows/.venv/bin/python`

## A1 — Pins re-derived (pre-edit)

| pin | value | check |
|-----|-------|-------|
| P1 — SKETCH_SHA | `4508b20abb79eac8` | matches plan ✓ |
| P1 — line count | 231 | matches plan ✓ |
| P1 — last writer | `3b347a7` | matches plan ✓ |
| P2 — ANCHOR count | 1 (`it costs nothing the order does not already build.`) | ✓ |
| P2 — trailing byte | `0a` | ✓ |
| P3 — `# Addendum 2026-09-02` | 0 | ✓ |
| P3 — `every machine is a shop, and the server role is the only difference` | 0 | ✓ |
| P3 — `## The invariant, stated` | 0 | ✓ |
| P3 — `## What the invariant does to threads 81 and 82` | 0 | ✓ |
| P3 — `## Where it lands next (bound, not deferred)` | 0 | ✓ |
| P6 — COMPANY.md sha | `7883745e23467b4e` | matches plan ✓ |
| git status of SK | EMPTY | no concurrent edits ✓ |

## A2 — G1: append executed

Addendum written to temp file `/tmp/addendum-100018-XXXXXX.txt` (25 lines) via quoted heredoc (no shell expansion).

**Token counts after append:**

| token | before | after |
|-------|--------|-------|
| `# Addendum 2026-09-02` | 0 | 1 |
| `every machine is a shop, and the server role is the only difference` | 0 | 1 |
| `## The invariant, stated` | 0 | 1 |
| `## What the invariant does to threads 81 and 82` | 0 | 1 |
| `## Where it lands next (bound, not deferred)` | 0 | 1 |

P2 anchor post-append: **1** (unchanged) ✓

**P4 — append-only diff:**
```
1 file changed, 25 insertions(+)
```
`<` line count in diff against HEAD: **0** ✓

## A3 — Governance commit

Commit: `e5250a0`
Message: `[100018] multi-machine sketch addendum 2026-09-02: the shop/server invariant — every machine is a shop, the server role is the only difference; threads 81/82 re-read under it`

`git -C "$GOV" log --oneline -1` confirms: `e5250a0 [100018] multi-machine sketch addendum 2026-09-02: the shop/server invariant — every machine is a shop, the server role is the only difference; threads 81/82 re-read under it`

P6 post-commit: `7883745e23467b4e` (COMPANY.md unchanged) ✓
