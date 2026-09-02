# QA Receipt — shop-server-invariant-sketch-2026-09-02

**Plan id:** 100018
**Slug:** `shop-server-invariant-sketch-2026-09-02`
**Step:** 2 (QA)
**Date:** 2026-09-02
**QA agent:** bellows QA

## Step 1 Receipt Status

Step 1 is **Complete**. Commit `775cd75` in the bellows worktree (dev log). Governance commit `e5250a0`.

## Verification Table

| Item | Check | Expected | Evidence | Status |
|------|-------|----------|----------|--------|
| 1a | Governance commit tag | `[100018]` commit on `$SK` | `e5250a0 [100018] multi-machine sketch addendum 2026-09-02: the shop/server invariant…` | ✅ |
| 1b | Token: `# Addendum 2026-09-02` | count = 1 | 1 | ✅ |
| 1c | Token: `every machine is a shop, and the server role is the only difference` | count = 1 | 1 | ✅ |
| 1d | Token: `## The invariant, stated` | count = 1 | 1 | ✅ |
| 1e | Token: `## What the invariant does to threads 81 and 82` | count = 1 | 1 | ✅ |
| 1f | Token: `## Where it lands next (bound, not deferred)` | count = 1 | 1 | ✅ |
| 1g | P2 anchor count post-edit | 1 | 1 | ✅ |
| 1h | Line count of `$SK` | 256 | 256 | ✅ |
| 1i | `git status --porcelain` of `$SK` | EMPTY | EMPTY | ✅ |
| 2a | `<` lines in diff(parent..current) | 0 | 0 | ✅ |
| 2b | First `>` line is blank | blank line | `> ` | ✅ |
| 2c | Second `>` line is addendum heading | `> # Addendum 2026-09-02 —…` | `> # Addendum 2026-09-02 — the shop/server invariant: every machine is a shop, and the server role is the only difference` | ✅ |
| 3a | `COMPANY.md` sha | `7883745e23467b4e` | `7883745e23467b4e` | ✅ |
| 3b | `git status` of `$SK` and `COMPANY.md` | EMPTY | EMPTY | ✅ |
| 3c | Governance dirty count (informational) | — | 0 | ✅ |
| 4  | Test suite | `full-suite-shop-server-invariant-sketch.txt`, `exit=0` | `full-suite-shop-server-invariant-sketch.txt` present, `exit=0` | ✅ |

## Bound Follow-Ups (not this plan's scope)

- **Plan B** (`shop-server-invariant-company-2026-09-02`, T2): `COMPANY.md` "Shop-level vs Project-level" — the sentence that a machine runs the shop and the server is the mini's one extra role.
- **`MACHINE_SETUP.md` v1.3**: vocabulary (lines that say "the shop" for the Air) and a §0 row for what the server holds — after `bellows-bootstrap` closes.
- **`GLOSSARY.md`**: `shop` and `server` definitions — a wrap act.
- **Planner pushes governance** after the pause.

## Rule 20 — QA Self-Check Results

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100018/knowledge/qa/evidence/shop-server-invariant-sketch-2026-09-02/
Files verified: 2
