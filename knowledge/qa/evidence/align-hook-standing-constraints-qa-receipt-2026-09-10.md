# QA Receipt — align-hook-standing-constraints — 2026-09-10

Plan #100066, thread 267. Step 2 — QA.

## DEV commits (numstat main...HEAD)

| +lines | -lines | file |
|--------|--------|------|
| 59 | 11 | `hooks/eluvian/eluvian_align_hook.py` |
| 55 | 0 | `knowledge/development/dev-log-align-hook-standing-constraints-2026-09-10.md` |
| 47 | 0 | `knowledge/mutants/align-hook-standing-constraints.json` |
| 14 | 0 | `knowledge/mutants/align-hook-standing-constraints.run.txt` |
| 189 | 0 | `tests/test_align_hook_sync.py` |

Commits: `0132ec7` (feat) `0b400af` (dev).

## Item 2 — hook RUN present (worktree file under /usr/bin/python3)

Isolation root: `$T/root` with `STANDING_CONSTRAINTS.md` copied from `$ELUVIAN_WRAP_ROOT`, `bellows/status.py` stub (`print("● stub")`), `lf/` and `tuyere/` git-init'ed, `mem/` plain dir, `ELUVIAN_HOOKS_LOG=$T/hooks.log`.

```
rc=0
True True 15
first constraint line: 1. One commit per lens, the subject naming the lens; lens commits through `scripts/lens_commit.py`, the close through `scripts/close_cycle.py`; a hand-run close is a declared deviation in the register. (DRAFTING_CYCLE §2.7, v2.34)
```

Pre-merge control (symlink `~/.claude/eluvian/eluvian_align_hook.py` = old code):
```
control_rc=0
heading_in_control: False
```

## Item 3 — hook RUN absent (fail-open)

File removed: `rm $T/root/STANDING_CONSTRAINTS.md`.

```
rc=0
not_found_line_present: True
heading_absent: True
valid_json: True
       3 /var/.../tmp.brUwrYsbgV/hooks.log
```

Scratch log line 1 (present run): `SessionStart-align parked=0 sync=[('lessons-forge', 'fetch FAILED')] constraints=10`
Scratch log line 2 (control run): `SessionStart-align parked=0 sync=[('lessons-forge', 'fetch FAILED')]`
Scratch log line 3 (absent run): `SessionStart-align parked=0 sync=[('lessons-forge', 'fetch FAILED')] constraints=absent`

All three runs logged to `$T/hooks.log` only.

## Item 4 — production writes

| check | result |
|-------|--------|
| live hooks.log mtime before | `Sep 10 20:07:19 2026` |
| live hooks.log mtime after | `Sep 10 20:08:40 2026` |
| mtime change cause | External: two live SessionStart entries in tail (`20:08:38` new-code format, `20:08:40` old-code format — from this QA session harness startup, not from any isolation run). Scratch log has 3 lines proving all three isolation runs wrote to `$T/hooks.log`, not to the live path. |
| no real repo fetched | `$ISO` set — all runs bounded to scratch |
| no lane file / lifecycle row | read-only run |
| scratch dir removed | `scratch_removed=ok` |
| writes under `~/.claude` | none from isolation runs |

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — suite | Summary: `2217 passed, 1 omission in 93.31s` — one omission (`test_gate_watcher`, live-DB); no `failed` | ✅ |
| 2 — present run | `True True 15`; first constraint line present; control through symlink: `False` | ✅ |
| 3 — absent run | rc 0, `not found under the governance root` present, `## Standing constraints` absent, 3 lines in scratch log | ✅ |
| 4 — production writes | Mtime change from external session activity only; scratch log proves isolation runs wrote there exclusively | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100066/knowledge/qa/evidence/
Files verified: 1
