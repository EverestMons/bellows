# QA Receipt — watcher-down-dedupe — 2026-09-14

Plan: `executable-100101` | Step 2 QA | thread 331

## DEV commits (3d21c30..54ca523)

```
git diff --numstat 3d21c30..HEAD
49      0       knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md
26      0       knowledge/mutants/watcher-down-dedupe.json
11      0       knowledge/mutants/watcher-down-dedupe.run.txt
11      4       notifier.py
120     1       tests/test_notifier_coverage.py
```

Five files across two commits (`ae0df7f`, `54ca523`).

## Item 2 — pages counted through tests

```
tests/test_notifier_coverage.py::test_8_watcher_down_episodes PASSED     [ 16%]
tests/test_notifier_coverage.py::test_8a_watcher_down_stale_plus_live_stale_first PASSED [ 33%]
tests/test_notifier_coverage.py::test_8b_watcher_down_stale_plus_live_live_first PASSED [ 50%]
tests/test_notifier_coverage.py::test_8c_watcher_down_two_machines_stale PASSED [ 66%]
tests/test_notifier_coverage.py::test_8d_watcher_down_mark_live_new_episode PASSED [ 83%]
tests/test_notifier_coverage.py::test_8e_liveness_poll_two_polls_one_page PASSED [100%]
```

The daemon which ran STEP 1 loaded the old `notifier.py`; the restart is owed after close. No call into the module outside pytest; nothing pages.

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite: 2369 passed, 9 warnings, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate); suite file written with `>`, not piped | ✅ |
| 2 | Six PASSED lines for test_8 and 8a–8e pasted above; daemon loaded old notifier.py; nothing pages | ✅ |
| 3 | No production writes outside the two evidence files; $T removed; no lane file, no live lifecycle row, no daemon act, no page | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100101/knowledge/qa/evidence/
Files verified: 1
