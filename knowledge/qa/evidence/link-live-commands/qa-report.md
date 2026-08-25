# QA Report — link_live_commands (Plan 533, Step 2)

**Date:** 2026-08-25
**Role:** QA
**Branch:** bellows-wt/533

---

## Q1 — Full Suite

```
1453 passed, 1 warning in 44.91s
```

**L4 accounting:** Plan pinned 1445 collected. Measured: 1453 collected. Delta: +8 (the 8 new tests in `test_link_live_commands.py`). Zero failures.

Raw output: `pytest_full.txt` in this evidence directory.

---

## Q2 — End-to-End Rehearsal (tmp only)

All runs used `--commands-dir` pointing at a tmp directory. `~/.claude` was never touched.

### Run 1 — Arm (c): plain files present

Seeded a tmp commands dir with plain copies of both vendored files (`wrap.md` 5597 B, `eluvian.md` 978 B) — the mini's exact current state.

```
LINKED wrap.md: /var/.../commands/wrap.md → .../hooks/commands/wrap.md
LINKED eluvian.md: /var/.../commands/eluvian.md → .../hooks/commands/eluvian.md
Exit code: 0
```

- Both targets are now symlinks resolving to the vendored files.
- Both `.pre-symlink` backups exist with original byte counts preserved (wrap.md: 5597 B, eluvian.md: 978 B).

### Run 2 — Arm (a): already linked (idempotent)

```
OK wrap.md: .../commands/wrap.md → .../hooks/commands/wrap.md
OK eluvian.md: .../commands/eluvian.md → .../hooks/commands/eluvian.md
Exit code: 0
```

- File count unchanged (4 before, 4 after). No new backups created.

### Run 3 — Arm (b): foreign symlink refusal

Created a foreign file and symlinked `wrap.md` to it.

```
REFUSED wrap.md: symlink → .../foreign.md (expected .../hooks/commands/wrap.md)
Exit code: 1
```

- Foreign symlink untouched (still points to the foreign file).
- No `eluvian.md` created — tool stopped after first refusal.

---

## Q3 — Fence Check

```
 tests/test_link_live_commands.py | 155 +++++++++++++++++++++++++++++++++++++++
 tools/link_live_commands.py      | 115 +++++++++++++++++++++++++++++
 2 files changed, 270 insertions(+)
```

Diff-stat matches the plan scope: exactly the two new files.

---

## Verification Table

| Arm | Description | Test Coverage | Rehearsal | Status |
|-----|-------------|---------------|-----------|--------|
| (a) | Symlink already correct → OK, no action | test 2 (idempotent) | Run 2 | ✅ |
| (b) | Foreign symlink → refuse, exit 1, nothing modified | test 5 (foreign symlink) | Run 3 | ✅ |
| (c) | Plain file → backup `.pre-symlink`, then symlink | test 3 (plain files backed up) | Run 1 | ✅ |
| (d) | Target absent → create symlink | test 1 (fresh dir) | — | ✅ |
| backup-collision | `.pre-symlink` exists → timestamped variant | test 4 (backup collision) | — | ✅ |
| missing-vendored | Vendored file absent → refuse before action | test 6 (missing vendored) | — | ✅ |
| dry-run | `--dry-run` prints plan, no filesystem changes | test 7 (dry-run) | — | ✅ |
| missing-dir | Commands dir absent → created, then linked | test 8 (missing commands dir) | — | ✅ |
| self-verify | After linking, byte-equality + symlink target check | all linking tests | Run 1, Run 2 | ✅ |
| fence | Diff-stat == exactly the two new files | — | Q3 | ✅ |
| suite | Full suite 1453 passed, 0 failures | Q1 | — | ✅ |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/533/knowledge/qa/evidence/link-live-commands/
Files verified: 2
```
