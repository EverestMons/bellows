# QA Receipt — notifier-coverage-record — 2026-09-09

**Plan:** executable-100055 | **Step:** 2 (QA) | **Date:** 2026-09-09

## DEV Commit Numstat

`<base>` = `6b4bfb56a4b4aebbb9c3af630295679f242aae4a` (cfb968e^, parent of first DEV commit)
`<dev>` = `c9081f9c...` (last DEV commit)

```
git diff --numstat 6b4bfb56a4b4aebbb9c3af630295679f242aae4a..c9081f9
166	17	knowledge/development/dev-log-notifier-coverage-2026-09-09.md
6	6	knowledge/mutants/notifier-coverage.json
3	3	knowledge/mutants/notifier-coverage.run.txt
10	22	notifier.py
1	0	tests/conftest.py
22	0	tests/test_notifier_coverage.py
```

Six files. ✓

## Run File HEAD Equality

```
HEAD: cfb968ea6dc726f8c48667984ab027cc9fa744bb   (from notifier-coverage.run.txt line 2)
git log -1 --format=%H -- knowledge/mutants/notifier-coverage.json
cfb968ea6dc726f8c48667984ab027cc9fa744bb
```

Match. ✓

## Unchanged Test Files

```
git diff 6b4bfb56..c9081f9 -- tests/test_notifier_server.py tests/test_bellows.py tests/test_depositor.py tests/test_gate_watcher.py
(empty — exit 0)
```

## Toplevel

```
git log --oneline -1
c9081f9 chore(dev-log): mutation re-run at cfb968e + dev-log rewritten under declared headings [100055]
```

## Reflog — 0 Amends

```
git reflog -n 6
c9081f9 HEAD@{0}: reset: moving to HEAD
c9081f9 HEAD@{1}: (dispatch entry — HEAD at worktree init)
```

No `amend` entries. ✓

## Dev-Log Headings

```
grep "^## " knowledge/development/dev-log-notifier-coverage-2026-09-09.md
## Pins re-derived (P1, P2, P3, P4, P6)
## Failing-first (the sibling red, then green)
## Mutation run
## Coverage table
## Cost
```

Five headings. ✓

## Items 1–7

1. **Full suite** — `2160 passed, 1 skipped in 77.38s` — green. Evidence: `notifier-coverage-record-suite-2026-09-09.txt`.
2. **Live config** — `_notifications_enabled(): False`; `notify_event("verdict_needed", ...)` with `push` patched → `push called: False`; INFO line: `not paged — disabled`.
3. **One gate** — `grep -n "push(" notifier.py` → line 80 (`def push`), line 178 (inside `_flush_buffer`), line 284 (inside `notify_event`) — every call inside `notify_event`, `_flush_buffer`, or `push` itself. `notify_watcher_down("air", "stale", 900)` with `notify_event` patched → `notify_event called: True`, `event: watcher_down`, `plan_scoped: False`, `detail_key: stale`.
4. **Receipt ownership** — `owned_by_live_session("executable-bellows-notifier-coverage-record", receipts_dir="/Users/marklehn/Developer/bellows/receipts")` → `(True, "owned by session d04ebd33 — transcript 10s old")`; receipt `armed_at: 2026-09-09T17:00:06.300649`; transcript age at probe time: ~20 min.
5. **Liveness verb** — `tuyere control liveness --json` → `[{"machine": "Marks-Mac-mini.local", "status": "live", "age_seconds": 99.1}, {"machine": "Marks-MacBook-Air-2.local", "status": "live", "age_seconds": 189.7}]` — both machines live.
6. **Record reads as declared** — `_gate_dev_log_declared_text(plan_text, 1, project_path, {}, failures, wt_path=".")` → `failures: []`; probe: 5 headings declared, 1 verbatim cell declared, all found in dev-log.
7. **Production writes** — none outside the two evidence files; no push; no lane file touched; no lifecycle row written.

## Verification

| # | Check | Status |
|---|-------|--------|
| 1 | Full suite green: 2160 passed | ✅ |
| 2 | Live config: notifications disabled, push not called | ✅ |
| 3 | One gate: push() only in notify_event/_flush_buffer/push; watcher_down routes through notify_event with plan_scoped=False | ✅ |
| 4 | Receipt ownership: owned=True, session d04ebd33 | ✅ |
| 5 | Liveness: both machines live (mini + Air) | ✅ |
| 6 | Record reads as declared: gate failures=[], 5 headings found, 1 verbatim cell found | ✅ |
| 7 | Production writes: none outside two evidence files | ✅ |
| 8 | DEV numstat: 6 files across two commits | ✅ |
| 9 | Run file HEAD matches last commit touching notifier-coverage.json | ✅ |
| 10 | Unchanged test files: empty diff | ✅ |
| 11 | Reflog: 0 amends | ✅ |
| 12 | Dev-log: 5 declared headings present | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100055/knowledge/qa/evidence/
Files verified: 2
